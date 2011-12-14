import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
from pages import BasePage

class Movie(BasePage):
    def get(self, movie_id):
        loader = tornado.template.Loader('templates/')
        admin = self.get_current_user()
        
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
      
        # fetch the movie
        cur.execute('select Title, Year, Note from Work where ID = ?',
                    (movie_id,))
        movie = cur.fetchone()
      
        if movie:
            # fetch the actors
            cur.execute('select FirstName, LastName, Num, Role from Actor where ID = ?',
                        (movie_id,))
            actors = cur.fetchall()
          
            # fetch the directors
            cur.execute('select FirstName, LastName, Num from Director where ID = ?',
                        (movie_id,))
            directors = cur.fetchall()
          
            # fetch the writers
            cur.execute('select FirstName, LastName, Num from Writer where ID = ?',
                        (movie_id,))
            writers = cur.fetchall()
          
            # fetch the countries
            cur.execute('select Country from Country where ID = ?',
                        (movie_id,))
            countries = map(lambda x: x[0], cur.fetchall())
          
            # fetch the languages
            cur.execute('select Language from Language where ID = ?',
                        (movie_id,))
            languages = map(lambda x: x[0], cur.fetchall())
          
            # fetch the genres
            cur.execute('select Genre from Genre where ID = ?',
                        (movie_id,))
            genres = map(lambda x: x[0], cur.fetchall())

            # fetch the votes
            cur.execute('select Up, Down from Votes where ID = ?', 
                        (movie_id,))
            (upvotes, downvotes) = cur.fetchone() or (0, 0)
          
            cur.close()
            
            self.write(loader.load('movie.html').generate(movie=movie,
                                                          ID=movie_id,
                                                          actors=actors,
                                                          directors=directors,
                                                          writers=writers,
                                                          countries=countries,
                                                          languages=languages,
                                                          genres=genres,
                                                          upvotes=upvotes,
                                                          downvotes=downvotes,
                                                          admin=admin))
        else:
            self.error('Movie \'%s\' not found' % movie_id)
