from tornado.escape import xhtml_escape as escape
from tornado.escape import url_escape
import re

def work_link(ID):
    """Return an HTML link for the work designed by ID (using /serie/
    for a serie, /movie/ for a movie and /episode/ for an episode)"""
    if ID[0] != '"':
        # Movie
        res = re.search('^(.+) \(([0-9]{4})[^\)]*\)$', ID)
        if res:
            title = escape(res.group(1))
            year = escape(res.group(2))
            return ('<a href="/movie/%s">%s (%s)</a>' % (url_escape(ID), title, year))
        else:
            return ('Invalid movie ID: %s' % escape(ID))
    elif ID.find('{') != -1:
        # Episode
        res = re.search('^"(.+)" \(([0-9]{4})[^\)]*\) \{(.*)\(#([0-9]{1,3})\.([0-9]{1,3})\)\}$', ID)
        if res:
            title = escape(res.group(1))
            year = escape(res.group(2))
            epi_name = escape(res.group(3))
            season = escape(res.group(4))
            epi_num = escape(res.group(5))
            return ('<a href="/episode/%s">%s (%s) %sx%s: %s</a>' % (url_escape(ID), title, year, season, epi_num, epi_name))
        else:
            return ('Invalid episode ID: %s' % escape(ID))
    else:
        # Serie
        res = re.search('"(.+)" \(([0-9]{4})[^\)]*\)', ID)
        if res:
            title = escape(res.group(1))
            year = escape(res.group(2))
            return ('<a href="/serie/%s">%s (%s)</a>' % (url_escape(ID), title, year))
        else:
            return ('Invalid serie ID: %s' % escape(ID))

def is_movie(ID):
    return ID[0] != '"'

def is_serie(ID):
    return ID[0] == '"' and ID.find('{') == -1

def is_episode(ID):
    return ID[0] == '"' and ID.find('{') != -1

def person_info(t, person, ID, admin):
    (fname, lname, num) = person
    res = ('<a href="/person/%s/%s/%s">%s %s</a>' %
           (url_escape(fname), url_escape(lname), url_escape(num),
            url_escape(fname), url_escape(lname)))
    if admin:
        res += (' (<a href="/admin/delete/%s/%s/%s/%s/%s">delete</a>)' %
                (t, url_escape(fname), url_escape(lname), url_escape(num),
                 url_escape(ID)))
    return res

def director_info(director, ID, admin):
    return person_info('director', director, ID, admin)

def writer_info(writer, ID, admin):
    return person_info('writer', writer, ID, admin)
