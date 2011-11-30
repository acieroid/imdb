import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3

class Movie(tornado.web.RequestHandler):
  def get(self, movie_id):
    loader = tornado.template.Loader("templates/")
    
    conn = sqlite3.connect("db.sqlite")
    conn.text_factory = str
    cur = conn.cursor()
    cur.execute("select Title, Year, Note from Work where ID = ?",
                (movie_id,))
    
    movie = cur.fetchone()

    cur.execute("select FirstName, LastName, Role from Actor where ID = ?",
                (movie_id,))
    actors = cur.fetchall()

    if movie:
      self.write(loader.load("movie.html").generate(movie=movie, actors=actors))
    else:
      self.write(loader.load("not_found.html").generate(message="Movie not found"))
