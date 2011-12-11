import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
import hashlib
import utils
from pages import BasePage

class AdminLogin(BasePage):
    def get(self):
        loader = tornado.template.Loader('templates/')
        self.write(loader.load('login.html').generate())
    def post(self):
        loader = tornado.template.Loader('templates/')
        mail = self.get_argument('mail', '')
        password = self.get_argument('password', '')
        # add mail as salt
        hashed_password = hashlib.sha256(mail+password).hexdigest()
        
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        
        # find the admin in the database
        cur.execute('select 1 from Admin where Mail = ? and Pass = ?',
                    (mail, hashed_password))
        auth = cur.fetchone()

        cur.close()

        if auth:
            self.set_secure_cookie('mail', mail)
            self.success('You are now logged', next='/admin')
        else:
            self.error('Wrong mail or password')

class AdminLogout(BasePage):
    @tornado.web.authenticated
    def get(self):
        loader = tornado.template.Loader('templates/')
        self.clear_cookie('mail')
        self.write(loader.load('login.html').generate())

class AdminPanel(BasePage):
    @tornado.web.authenticated
    def get(self):
        loader = tornado.template.Loader('templates/')
        user = self.get_current_user()
        self.write(loader.load('admin.html').generate(mail=user))

class AdminAdd(BasePage):
    @tornado.web.authenticated
    def post(self):
        loader = tornado.template.Loader('templates/')
        mail = self.get_argument('mail', '')
        password = self.get_argument('password', '')
        hashed_password = hashlib.sha256(mail+password).hexdigest()

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        # check if the new admin already exists
        cur.execute('select 1 from Admin where Mail = ?', (mail,))
        if cur.fetchone():
            cur.close()
            self.error('This admin already exists')
        else:
            cur.execute('insert into Admin (Mail, Pass) values (?, ?)',
                        (mail, hashed_password))
            conn.commit()
            cur.close()
            self.success('Admin added', next='/admin')

class AdminAddWork(BasePage):
    @tornado.web.authenticated
    def post(self, t):
        loader = tornado.template.Loader('templates/')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        title = self.get_argument('title', '')
        epi_title = self.get_argument('epi_title', '')
        try:
            year = int(self.get_argument('year', ''))
            note = self.get_argument('note', '')
            if note != '':
                note = int(note)
                if note < 0 or note < 10:
                    raise ValueError('Invalid note')
            print note
            if t == 'episode':
                season = int(self.get_argument('season', ''))
                epi_num = int(self.get_argument('epi_num', ''))
                date = int(self.get_argument('date', ''))
            if t == 'serie':
                end_year = self.get_argument('end_year', '')
                if end_year != '':
                    end_year = int(end_year)
        except ValueError:
            self.error('Incorrect values, check the values that should be integers')
            return

        if t == 'movie':
            ID = '%s (%d)' % (title, year)
        elif t == 'serie':
            ID = '"%s" (%d)' % (title, year)
        elif t == 'episode':
            # first, we check that the serie exists
            ID = '"%s" (%d)' % (title, year)
            cur.execute('select 1 from Work where ID = ?', (ID,))
            if not cur.fetchone():
                cur.close()
                self.error('This serie does not exists')
                return
            ID = '"%s" (%d) {%s (#%d.%d)}' % (title, year, epi_title, season, epi_num)
        else:
            self.error('Unknown work type: %s' % t)
            return

        # check if already there
        cur.execute('select 1 from Work where ID = ?', (ID,))
        if cur.fetchone():
            cur.close()
            self.error('This work already exists')
        else:
            # add it
            cur.execute('insert into Work (ID, Title, Year, Note) values (?, ?, ?, ?)',
                        (ID, title, year, note))
            if t == 'movie':
                cur.execute('insert into Movie (ID) values (?)', (ID,))
            elif t == 'serie':
                cur.execute('insert into Serie (ID, EndYear) values (?, ?)',
                            (ID, end_year))
            elif t == 'episode':
                cur.execute('insert into Episode (ID, Season, EpisodeNum, Date, EpisodeTitle) values (?, ?, ?, ?, ?)',
                            (ID, season, epi_num, date, epi_title))
            conn.commit()
            cur.close()
            self.success('Work added')

class AdminAddPerson(BasePage):
    @tornado.web.authenticated
    def post(self, t):
        loader = tornado.template.Loader('templates/')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        ID = self.get_argument('id', '')
        role = self.get_argument('role', '')
        fname = self.get_argument('fname', '')
        lname = self.get_argument('lname', '')
        num = self.get_argument('num', '')
        gender = self.get_argument('gender', '')

        cond = 'FirstName = ? and LastName = ? and Num = ?'
        pID = (fname, lname, num)

        # check if work id is valid
        cur.execute('select 1 from Work where ID = ?', (ID,))
        if not cur.fetchone():
            cur.close()
            self.error('There is no such work: %s' % ID)
            return

        # check if person already exists
        cur.execute('select 1 from Person where %s' % cond, pID)
        if not cur.fetchone():
            # person does not exists, add it
            cur.execute('insert into Person (FirstName, LastName, Num, Gender) values (?, ?, ?, ?)',
                        (fname, lname, num, gender))

        # add its role
        if t == 'director':
            cur.execute('insert into Director (FirstName, LastName, Num, ID) values (?, ?, ?, ?)',
                        (fname, lname, num, ID))
        elif t == 'writer':
            cur.execute('insert into Writer (FirstName, LastName, Num, ID) values (?, ?, ?, ?)',
                        (fname, lname, num, ID))
        elif t == 'actor':
            if role == '':
                cur.close()
                self.error('Please specify a role')
                return
            cur.execute('insert into Actor (FirstName, LastName, Num, ID, Role) values (?, ?, ?, ?, ?)',
                        (fname, lname, num, ID, role))

        conn.commit()
        cur.close()
        self.success('Person added')

class AdminAddInfo(BasePage):
    @tornado.web.authenticated
    def post(self, t):
        loader = tornado.template.Loader('templates/')

        if t != 'genre' and t != 'country' and t != 'language':
            self.error('Invalid info type: %s' % t)
            return

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        ID = self.get_argument('id', '')
        info = self.get_argument(t, '')

        if info == '':
            cur.close()
            self.error('Invalid info')
            return

        # check if work id is valid
        cur.execute('select 1 from Work where ID = ?', (ID,))
        if not cur.fetchone():
            cur.close()
            self.error('There is no such work: %s' % ID)
            return

        cur.execute('insert into %s (ID, %s) values (?, ?)' % 
                    (t.capitalize(), t.capitalize()),
                    (ID, info))
        conn.commit()
        cur.close()
        self.success('Info added')

class AdminDelete(BasePage):
    @tornado.web.authenticated
    def post(self):
        loader = tornado.template.Loader('templates/')
        to_delete = self.get_argument('mail', '')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        # an admin can't delete himself
        if to_delete == self.get_current_user():
            self.error('You cannot delete yourself')
        else:
            # check that the admin exists
            cur.execute('select 1 from Admin where Mail = ?', (to_delete,))
            if cur.fetchone():
                # it exists, so we delete it
                cur.execute('delete from Admin where Mail = ?', (to_delete,))
                conn.commit()
                cur.close()
                self.success('Admin deleted', next='/admin')
            else:
                cur.close()
                self.error('Admin with mail %s does not exists' % to_delete)

class AdminDeleteWork(BasePage):
    @tornado.web.authenticated
    def get(self, ID):
        loader = tornado.template.Loader('templates/')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        # check that the work exists
        cur.execute('select 1 from Work where ID = ?', (ID,))
        if cur.fetchone():
            # delete it and everything related
            op = '='
            if utils.is_serie(ID):
                # if a serie, also delete its episodes
                op = 'like'
                ID = ID + '%'
            cur.execute('delete from Movie where ID %s ?' % op, (ID,))
            cur.execute('delete from Episode where ID %s ?' % op, (ID,))
            cur.execute('delete from Serie where ID %s ?' % op, (ID,))
            cur.execute('delete from Director where ID %s ?' % op, (ID,))
            cur.execute('delete from Writer where ID %s ?' % op, (ID,))
            cur.execute('delete from Actor where ID %s ?' % op, (ID,))
            cur.execute('delete from Work where ID %s ?' % op, (ID,))
            conn.commit()
            cur.close()
            self.success('Work and related stuff deleted')
        else:
            cur.close()
            self.error('Nothing exists with the ID \'%s\'' % ID)

class AdminDeletePerson(BasePage):
    @tornado.web.authenticated
    def get(self, fname, lname, num):
        loader = tornado.template.Loader('templates/')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        ID = (fname, lname, num)
        cond = 'FirstName = ? and LastName = ? and Num = ?'

        # check that the person exists
        cur.execute('select 1 from Person where %s' % cond, ID)
        if cur.fetchone():
            # delete it
            cur.execute('delete from Director where %s' % cond, ID)
            cur.execute('delete from Writer where %s' % cond, ID)
            cur.execute('delete from Actor where %s' % cond, ID)
            cur.execute('delete from Person where %s' % cond, ID)
            conn.commit()
            cur.close()
            self.success('Person deleted')
        else:
            cur.close()
            self.error('This person does not exists: %s %s (%s)' % ID)

class AdminDeletePersonType(BasePage):
    @tornado.web.authenticated
    def get(self, t, fname, lname, num, ID, role):
        loader = tornado.template.Loader('templates/')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        pID = (fname, lname, num, ID)
        cond = 'FirstName = ? and LastName = ? and Num = ? and ID = ?'

        if t == 'actor':
            cond += ' and Role = ?'
            pID = (fname, lname, num, ID, role)
            cur.execute('select 1 from Actor where %s' % cond, pID)
            if cur.fetchone():
                cur.execute('delete from Actor where %s' % cond, pID)
                conn.commit()
                cur.close()
                self.success('Actor deleted')
            else:
                self.error('This actorx does not exists: %s %s (%s)' % (fname, lname, num))
        elif t == 'director':
            cur.execute('select 1 from Director where %s' % cond, pID)
            if cur.fetchone():
                cur.execute('delete from Director where %s' % cond, pID)
                conn.commit()
                cur.close()
                self.success('Director deleted')
            else:
                self.error('This director does not exists: %s %s (%s)' % (fname, lname, num))
        elif t == 'writer':
            cur.execute('select 1 from Writer where %s' % cond, pID)
            if cur.fetchone():
                cur.execute('delete from Director where %s' % cond, pID)
                conn.commit()
                cur.close()
                self.success('Writer deleted')
            else:
                self.error('This writer does not exists: %s %s (%s)' % (fname, lname, num))
        else:
            self.error('Unknown type of person: %s' % t)
