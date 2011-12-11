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
        table=json.loads(response.read())
        if table['Response'] == 'True':
            poster = table['Poster']
            if poster != 'N/A' and title == table['Title']:
                self.redirect(poster)
            else:
                raise tornado.web.HTTPError(404)
	else:
            raise tornado.web.HTTPError(404)
