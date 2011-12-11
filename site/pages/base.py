import tornado.ioloop
import tornado.web
import tornado.template

class BasePage(tornado.web.RequestHandler):
    def get_login_url(self):
        return '/admin/login'
    def get_current_user(self):
        mail = self.get_secure_cookie('mail')
        return mail
    def error(self, message):
        loader = tornado.template.Loader('templates/')
        self.write(loader.load('error.html').generate(message=message))
    def success(self, message, next='/'):
        loader = tornado.template.Loader('templates/')
        self.write(loader.load('success.html').generate(message=message))
