import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
import hashlib

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
            cur.execute('select * from Admin where Mail = ?', (to_delete,))
            if cur.fetchone():
                # it exists, so we delete it
                cur.execute('delete from Admin where Mail = ?', (to_delete,))
                self.write(loader.load('success.html').generate(message='Admin deleted',
                                                                next='/admin'))
            else:
                self.write(loader.load('error.html').generate(message='Admin with mail %s do not exists' % to_delete))
                
