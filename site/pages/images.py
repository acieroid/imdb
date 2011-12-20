import tornado.ioloop
import tornado.web
import tornado.template
import urllib2
import json
from tornado.escape import url_escape

class Poster(tornado.web.RequestHandler):
    def get(self, title, year):
        # fetch the cover
        response = urllib2.urlopen('http://www.imdbapi.com/?i=&t=' +
                                   url_escape(title) +
                                   '&y=' + year)
        table = json.loads(response.read())
        if table['Response'] == 'True':
            poster = table['Poster']
            if poster != 'N/A' and title == table['Title']:
                self.redirect(poster)
            else:
                raise tornado.web.HTTPError(404)
	else:
            raise tornado.web.HTTPError(404)

class Location(tornado.web.RequestHandler):
    def get(self, countries):
        gmap_url = 'http://maps.googleapis.com/maps/api/staticmap?center=Belgium&zoom=1&size=500x400&sensor=true&maptype=satellite'
        for country in countries.split(','):
            gmap_url += ('&markers=label:%s|%s' % 
                         (country[0].capitalize(), country))
        self.redirect(gmap_url)
            
