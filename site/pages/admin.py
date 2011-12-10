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
            self.write(loader.load('admin.html').generate(mail=mail))
        else:
            self.write(loader.load('error.html').generate(message='Wrong mail or password'))

class AdminLogout(AdminPage):
    def get(self):
        loader = tornado.template.Loader('templates/')
        self.clear_cookie('mail')
        self.write(loader.load('login.html').generate())
