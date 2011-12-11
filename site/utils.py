from tornado.escape import xhtml_escape as escape
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
            return ('<a href="/movie/%s">%s (%s)</a>' % (escape(ID), title, year))
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
            return ('<a href="/episode/%s">%s (%s) %sx%s: %s</a>' % (escape(ID), title, year, season, epi_num, epi_name))
        else:
            return ('Invalid episode ID: %s' % escape(ID))
    else:
        # Serie
        res = re.search('"(.+)" \(([0-9]{4})[^\)]*\)', ID)
        if res:
            title = escape(res.group(1))
            year = escape(res.group(2))
            return ('<a href="/serie/%s">%s (%s)</a>' % (escape(ID), title, year))
        else:
            return ('Invalid serie ID: %s' % escape(ID))

def is_movie(ID):
    return ID[0] != '"'

def is_serie(ID):
    return ID[0] == '"' and ID.find('{') == -1

def is_episode(ID):
    return ID[0] == '"' and ID.find('{') != -1
