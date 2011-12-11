import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3

import pages

application = tornado.web.Application([
    (r'/', pages.Main),
    (r'/search', pages.Search),
    (r'/movie/(.*)', pages.Movie),
    (r'/serie/(.*)', pages.Serie),
    (r'/poster/(.+)/(.+)', pages.Poster),
    (r'/person/(.+)/(.+)/(.*)', pages.Person),
    (r'/admin', pages.AdminPanel),
    (r'/admin/login', pages.AdminLogin),
    (r'/admin/logout', pages.AdminLogout),
    (r'/admin/add', pages.AdminAdd),
    (r'/admin/add/(movie|serie|episode)', pages.AdminAddWork),
    (r'/admin/add/(director|writer|director)', pages.AdminAddPerson),
    (r'/admin/delete', pages.AdminDelete),
    (r'/admin/delete/work/(.*)', pages.AdminDeleteWork),
    (r'/admin/delete/person/(.+)/(.+)/(.*)', pages.AdminDeletePerson),
    (r'/admin/delete/(director|writer|actor)/(.+)/(.+)/(.*)/(.+)/(.*)', pages.AdminDeletePersonType),
], cookie_secret='N53gLGkySeCvX5AjgUgmtAez7L8JhUP2hb+MYgizGWo=')

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
