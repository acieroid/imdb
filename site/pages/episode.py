import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
from pages import BasePage

class Episode(BasePage):
    def get(self, episode_id):
        loader = tornado.template.Loader('templates/')
        admin = self.get_current_user()
        
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        
        # fetch the episode (Title is the title of the serie)
        cur.execute('select Title, Year, Note, Season, EpisodeNum, Date, EpisodeTitle, SID from Work, Episode where Episode.ID = ? and Work.ID = Episode.ID',
                    (episode_id,))
        episode = cur.fetchone()
      
        if episode:
            # fetch the actors
            cur.execute('select FirstName, LastName, Num, Role from Actor where ID = ?',
                        (episode_id,))
            actors = cur.fetchall()
          
            # fetch the directors
            cur.execute('select FirstName, LastName, Num from Director where ID = ?',
                        (episode_id,))
            directors = cur.fetchall()
          
            # fetch the writers
            cur.execute('select FirstName, LastName, Num from Writer where ID = ?',
                        (episode_id,))
            writers = cur.fetchall()
          
            # fetch the countries
            cur.execute('select Country from Country where ID = ?',
                        (episode_id,))
            countries = map(lambda x: x[0], cur.fetchall())
          
            # fetch the languages
            cur.execute('select Language from Language where ID = ?',
                        (episode_id,))
            languages = map(lambda x: x[0], cur.fetchall())
          
            # fetch the genres
            cur.execute('select Genre from Genre where ID = ?',
                        (episode_id,))
            genres = map(lambda x: x[0], cur.fetchall())
            
            cur.close()
            
            self.write(loader.load('episode.html').generate(episode=episode,
                                                            ID=episode_id,
                                                            actors=actors,
                                                            directors=directors,
                                                            writers=writers,
                                                            countries=countries,
                                                            languages=languages,
                                                            genres=genres,
                                                            admin=admin))
        else:
            self.error('Episode \'%s\' not found' % episode_id)
