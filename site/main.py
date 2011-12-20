import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
import os.path
import pages

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'cookie_secret': 'N53gLGkySeCvX5AjgUgmtAez7L8JhUP2hb+MYgizGWo=',
    'debug': True
}

application = tornado.web.Application([
    (r'/', pages.Main),
    (r'/search', pages.Search),
    (r'/search_results/(.*)', pages.SearchResults),
    (r'/movie/(.*)', pages.Movie),
    (r'/serie/(.*)', pages.Serie),
    (r'/episode/(.*)', pages.Episode),
    (r'/person/(.*)/(.*)/(.*)', pages.Person),
    (r'/poster/(.+)/(.+)', pages.Poster),
    (r'/location/(.+)', pages.Location),
    (r'/(up|down)vote/(.*)', pages.Vote),
    (r'/admin', pages.AdminPanel),
    (r'/admin/login', pages.AdminLogin),
    (r'/admin/logout', pages.AdminLogout),
    (r'/admin/add', pages.AdminAdd),
    (r'/admin/add/(movie|serie|episode)', pages.AdminAddWork),
    (r'/admin/add/(director|writer|actor)', pages.AdminAddPerson),
    (r'/admin/add/(genre|country|language)', pages.AdminAddInfo),
    (r'/admin/delete', pages.AdminDelete),
    (r'/admin/delete/work/(.*)', pages.AdminDeleteWork),
    (r'/admin/delete/person/(.*)/(.*)/(.*)', pages.AdminDeletePerson),
    (r'/admin/delete/(director|writer|actor)/(.*)/(.*)/(.*)/(.*)/?(.*)', pages.AdminDeletePersonType),
    (r'/admin/delete/(genre|country|language)', pages.AdminDeleteInfo),
    (r'/requests', pages.Requests),
    (r'/req/1', pages.Request1),
    (r'/req/2', pages.Request2),
    (r'/req/3', pages.Request3),
    (r'/req/4', pages.Request4),
    (r'/req/5', pages.Request5),
    (r'/req/6', pages.Request6),
], **settings)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
