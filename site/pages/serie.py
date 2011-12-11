import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
from pages import BasePage

class Serie(BasePage):
    def get(self, serie_id):
        loader = tornado.template.Loader('templates/')
        admin = self.get_current_user()
        
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
      
        # fetch the serie
        cur.execute('select Title, Year, Note, EndYear from Work, Serie where Work.ID = ? and Serie.ID = Work.ID',
                    (serie_id,))
        serie = cur.fetchone()
      
        if serie:
            # fetch the actors
            cur.execute('select FirstName, LastName, Num, Role from Actor where ID = ?',
                        (serie_id,))
            actors = cur.fetchall()
          
            # fetch the directors
            cur.execute('select FirstName, LastName, Num from Director where ID = ?',
                        (serie_id,))
            directors = cur.fetchall()
          
            # fetch the writers
            cur.execute('select FirstName, LastName, Num from Director where ID = ?',
                        (serie_id,))
            writers = cur.fetchall()
          
            # fetch the countries
            cur.execute('select Country from Country where ID = ?',
                        (serie_id,))
            countries = map(lambda x: x[0], cur.fetchall())
          
            # fetch the languages
            cur.execute('select Language from Language where ID = ?',
                        (serie_id,))
            languages = map(lambda x: x[0], cur.fetchall())
          
            # fetch the genres
            cur.execute('select Genre from Genre where ID = ?',
                        (serie_id,))
            genres = map(lambda x: x[0], cur.fetchall())
            
            # fetch the episodes
            cur.execute('select ID, Season, EpisodeNum, EpisodeTitle from Episode, SerieEpisode where SerieEpisode.SID=? and Episode.ID=SerieEpisode.EID order by Season, EpisodeNum', (serie_id,))
                        
            episodes = cur.fetchall()

            cur.close()
            
            self.write(loader.load('serie.html').generate(serie=serie,
                                                          ID=serie_id,
                                                          actors=actors,
                                                          directors=directors,
                                                          writers=writers,
                                                          countries=countries,
                                                          languages=languages,
                                                          genres=genres,
                                                          episodes=episodes,
                                                          admin=admin))
        else:
            self.error('Serie \'%s\' not found', serie_id)
