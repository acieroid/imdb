import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3

import pages

application = tornado.web.Application([
    (r"/", pages.Main),
    (r"/movie/(.*)", pages.Movie),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()