import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
from pages import BasePage

class Requests(BasePage):
    def get(self):
        loader = tornado.template.Loader('templates/')
        self.write(loader.load('requests.html').generate())

class Request(BasePage):
    def __init__(self, application, request, **kwargs):
        BasePage.__init__(self, application, request, **kwargs)
    def get(self):
        loader = tornado.template.Loader('templates/')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        cur.execute(self.sql_request)
        res = cur.fetchall()

        conn.close()

        self.write(loader.load(self.template).generate(res=res,
                                                       request=self.req_num))

class Request1(Request):
    def __init__(self, application, request, **kwargs):
        Request.__init__(self, application, request, **kwargs)
        self.sql_request = '''
select FirstName, LastName, Num from Actor where
  (select count(distinct Year) from Work
    where Year >= 2003
     and Year <= 2007
     and Actor.ID = Work.ID) = (2007-2003)'''
        self.template = 'request_person.html'
        self.req_num = 1

class Request2(Request):
    def __init__(self, application, request, **kwargs):
        Request.__init__(self, application, request, **kwargs)
        self.sql_request = '''
select distinct FirstName, LastName, Num
  from Writer, Movie, Work
  where Writer.ID = Movie.ID and Work.ID = Movie.ID
  group by FirstName, LastName, Num, Year
  having count(Writer.ID) >= 2'''
        self.template = 'request_person.html'
        self.req_num = 2

class Request3(Request):
    def __init__(self, application, request, **kwargs):
        Request.__init__(self, application, request, **kwargs)
        self.sql_request = '''
select distinct X.FirstName, X.LastName, X.Num from Actor X
  where exists (select * from Actor Y1
                  where exists (select * from Actor Z, Actor Y2 
                                  where Z.ID = Y2.ID
                                    and Z.ID != X.ID
                                    and Z.FirstName = ?
                                    and Z.LastName = ?
                                    and Z.Num = ?
                                    and Y2.FirstName = Y1.FirstName
                                    and Y2.LastName = Y1.LastName
                                    and Y2.Num = Y1.Num)
                    and Y1.ID = X.ID)'''
        self.template = 'request_person.html'
        self.req_num = 3
    def get(self):
        loader = tornado.template.Loader('templates/')

        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        fname = self.get_argument('fname', '')
        lname = self.get_argument('lname', '')
        num = self.get_argument('num', '')

        cur.execute(self.sql_request, (fname, lname, num))
        res = cur.fetchall()

        conn.close()

        self.write(loader.load(self.template).generate(res=res,
                                                       request=self.req_num))

class Request4(Request):
    def __init__(self, application, request, **kwargs):
        Request.__init__(self, application, request, **kwargs)
        self.sql_request = '''
select ID from Episode
  where not exists (select * from Person, Actor
                      where Person.Gender = 'M'
                        and Person.FirstName = Actor.FirstName
                        and Person.LastName = Actor.LastName
                        and Person.Num = Actor.Num
                        and Actor.ID = Episode.ID)'''
        self.template = 'request_episode.html'
        self.req_num = 4

class Request5(Request):
    def __init__(self, application, request, **kwargs):
        Request.__init__(self, application, request, **kwargs)
        self.sql_request = '''
select FirstName, LastName, Num from Actor, Serie
 where Actor.ID = Serie.ID
 group by FirstName, LastName, Num
 having  count(*) = (select max(Count) from (select count(*) as Count
                                           from Actor, Serie
                                           where Actor.ID = Serie.ID
                                           group by FirstName, LastName, Num))'''

        self.template = 'request_person.html'
        self.req_num = 5

class Request6(Request):
    def __init__(self, application, request, **kwargs):
        Request.__init__(self, application, request, **kwargs)
        self.sql_request = '''
select Serie.ID, count(Episode.ID), 
       avg(EpisodesPerSeason.Count), avg(ActorsPerSeason.Count)
  from Episode, Serie, Work,
       (select Episode.SID as SID, count(*) as Count
          from Episode group by Episode.SID, Season) EpisodesPerSeason,
       (select SID, count(distinct FirstName||LastName||Num) as Count
          from Episode, Actor
          where Episode.ID = Actor.ID
          group by Episode.SID, Episode.Season) ActorsPerSeason
  where Episode.SID = Serie.ID
    and Episode.SID = EpisodesPerSeason.SID
    and Episode.SID = ActorsPerSeason.SID
    and Serie.ID = Work.ID
    and Work.Note > (select avg(Note) from Work W, Serie S
                      where S.ID = W.ID)
  group by Episode.SID'''
        self.template = 'request_6.html'
        self.req_num = 6
