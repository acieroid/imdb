import tornado.ioloop
import tornado.web
import tornado.template

class Main(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader('templates/')
        return self.write(loader.load('base.html').generate())
