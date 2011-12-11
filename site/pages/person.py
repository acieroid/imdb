import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
from pages import BasePage

class Person(BasePage):
    def get(self, fname, lname, num):
        loader = tornado.template.Loader('templates/')
        admin = self.get_current_user()

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        cond = 'FirstName = ? and LastName = ? and Num = ?'
        ID = (fname, lname, num)

        # fetch the person's information
        cur.execute('select FirstName, LastName, Num, Gender from Person where '
                    + cond, ID)
        person = cur.fetchone()

        if person:
            # fetch its roles
            cur.execute('select ID, Role from Actor where ' + cond, ID)
            roles = cur.fetchall()
            
            # fetch its directed movies
            cur.execute('select ID from Director where ' + cond, ID)
            directed = cur.fetchall()
            
            # fetch its written movies
            cur.execute('select ID from Writer where ' + cond, ID)
            written = cur.fetchall()

            cur.close()
            self.write(loader.load('person.html').generate(person=person,
                                                           roles=roles,
                                                           directed=directed,
                                                           written=written,
                                                           admin=admin))
        else:
            cur.close()
            self.write(loader.load('error.html').generate(message='This person does not exists: %s %s %s' % ID))
