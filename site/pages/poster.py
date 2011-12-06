import tornado.ioloop
import tornado.web
import tornado.template
import urllib
import urllib2
import json

class Poster(tornado.web.RequestHandler):
    def get(self, title, year):
        # fetch the cover
        response = urllib2.urlopen('http://www.imdbapi.com/?i=&t=' +
                                   urllib.quote_plus(title) +
                                   '&y=' + urllib.quote_plus(year))
        poster = json.loads(response.read())['Poster']
        if poster != 'N/A':
            self.redirect(poster)
        else:
            raise tornado.web.HTTPError(404)

