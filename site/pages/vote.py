import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3

class Vote(tornado.web.RequestHandler):
    def get(self, t, ID):
        if t != 'up' and t != 'down':
            raise tornado.web.HTTPError(404)

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        # already some votes ?
        cur.execute('select 1 from Votes where ID = ?', (ID,))
        if not cur.fetchone():
            # no, add the entry
            cur.execute('insert into Votes (ID, Up, Down) values (?, 0, 0)', (ID,))

        # add the vote
        cur.execute('update Votes set %s = %s + 1 where ID = ?' %
                    (t.capitalize(), t.capitalize()), (ID,))
        conn.commit()
        cur.close()
