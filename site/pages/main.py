import tornado.ioloop
import tornado.web
import tornado.template
from pages import BasePage

class Main(BasePage):
    def get(self):
        loader = tornado.template.Loader('templates/')
        return self.write(loader.load('base.html').generate())
