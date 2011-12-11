import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
import hashlib
import utils

class AdminPage(tornado.web.RequestHandler):
    def get_login_url(self):
        return '/admin/login'
    def get_current_user(self):
        mail = self.get_secure_cookie('mail')
        return mail

class AdminLogin(AdminPage):
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
            self.redirect(self.get_argument('next', '/admin'))
        else:
            self.write(loader.load('error.html').generate(message='Wrong mail or password'))

class AdminLogout(AdminPage):
    def get(self):
        loader = tornado.template.Loader('templates/')
        self.clear_cookie('mail')
        self.write(loader.load('login.html').generate())

class AdminPanel(AdminPage):
    @tornado.web.authenticated
    def get(self):
        loader = tornado.template.Loader('templates/')
        user = self.get_current_user()
        self.write(loader.load('admin.html').generate(mail=user))

class AdminAdd(AdminPage):
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
            self.write(loader.load('error.html').generate(message='This admin already exists'))
        else:
            cur.execute('insert into Admin (Mail, Pass) values (?, ?)',
                        (mail, hashed_password))
            conn.commit()
            cur.close()
            # TODO: check that the request is successful
            self.write(loader.load('success.html').generate(message='Admin added',
                                                            next='/admin'))

class AdminDelete(AdminPage):
    @tornado.web.authenticated
    def post(self):
        loader = tornado.template.Loader('templates/')
        to_delete = self.get_argument('mail', '')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        # an admin can't delete himself
        if to_delete == self.get_current_user():
            self.write(loader.load('error.html').generate(message='You cannot delete yourself'))
        else:
            # check that the admin exists
            cur.execute('select 1 from Admin where Mail = ?', (to_delete,))
            if cur.fetchone():
                # it exists, so we delete it
                cur.execute('delete from Admin where Mail = ?', (to_delete,))
                conn.commit()
                cur.close()
                self.write(loader.load('success.html').generate(message='Admin deleted',
                                                                next='/admin'))
            else:
                cur.close()
                self.write(loader.load('error.html').generate(message='Admin with mail %s do not exists' % to_delete))

class AdminDeleteWork(AdminPage):
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
                ID = ID + ' {%'
            cur.execute('delete from Movie where ID %s ?' % op, (ID,))
            cur.execute('delete from Episode where ID %s ?' % op, (ID,))
            cur.execute('delete from Director where ID %s ?' % op, (ID,))
            cur.execute('delete from Writer where ID %s ?' % op, (ID,))
            cur.execute('delete from Actor where ID %s ?' % op, (ID,))
            cur.execute('delete from Work where ID %s ?' % op, (ID,))
            conn.commit()
            cur.close()
            self.write(loader.load('success.html').generate(message='Work and related stuff deleted',
                                                            next='/'))
        else:
            cur.close()
            self.write(loader.load('error.html').generate(message='Nothing exists with the ID %s' % ID))

class AdminDeletePerson(AdminPage):
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
            self.write(loader.load('success.html').generate(message='Person deleted',
                                                            next='/'))
        else:
            cur.close()
            self.write(loader.load('error.html').generate(message='%s %s (%s) do not exists' % ID))
