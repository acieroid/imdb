import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
import ply.lex
import ply.yacc
import re
from pages import BasePage

class QueryError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

# Query language
tokens = (
    'OPERATOR',
    'COMPARATOR',
    'CONTAINER',
    'CONTAINER_OP',
    'IDENTIFIER',
    'SORT',
    'VALUE',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SPACE',
)

precedence = (
    ('left', 'SORT'),
    ('left', 'CONTAINER_OP'),
    ('left', 'OPERATOR'),
)

t_OPERATOR = r'(and|or)'
t_CONTAINER_OP = r'(;|,)'
t_CONTAINER = r'contains'
t_SORT = r'sort(\+|\-)'
t_COMPARATOR = r'(>=|<=|<|>|==|=~)'
t_IDENTIFIER = r'[A-Z][a-zA-Z_]+'
def t_VALUE(t):
    r'("[^"]+"|[0-9\.]+)'
    if t.value[0] == '"':
        t.value = t.value[1:-1]
    else:
        t.value = int(t.value)
    return t
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_ignore_SPACE = r'\s+'

def t_error(t):
    raise QueryError('error when lexing "%s"' % t.value)

ply.lex.lex()

def p_query_sort(p):
    'query : condition SORT IDENTIFIER'
    p[0] = [p[2], p[3], p[1]]

def p_query(p):
    'query : condition'
    p[0] = p[1]

def p_paren(p):
    'condition : LPAREN condition RPAREN'
    p[0] = p[2]

def p_op(p):
    'condition : condition OPERATOR condition'
    p[0] = [p[2], p[1], p[3]]

def p_comp(p):
    'condition : IDENTIFIER COMPARATOR VALUE'
    p[0] = [p[2], p[1], p[3]]

def p_cont(p):
    'condition : IDENTIFIER CONTAINER container'
    p[0] = [p[2], p[1], p[3]]

def p_container_op(p):
    'container : LBRACE container_content RBRACE'
    p[0] = p[2]

def p_container_content_op(p):
    'container_content : condition CONTAINER_OP condition'
    p[0] = [p[2], p[1], p[3]]

def p_container_content(p):
    'container_content : condition'
    p[0] = p[1]

def p_error(p):
    raise QueryError('syntax error at "%s"' % p.value)

ply.yacc.yacc()

def satisfies(l, predicate):
    if l:
        if type(l) == list:
            if re.match(t_OPERATOR, l[0]):
                return satisfies(l[1], predicate) or satisfies(l[2], predicate)
            elif re.match(t_COMPARATOR, l[0]):
                return satisfies(l[1], predicate)
        elif predicate(l):
            return True
            
    else:
        return False

def convert_pattern_matching(s):
    # TODO: what to do if the user has entered a query with '%' and '?'
    return re.sub(r'\?', '_', re.sub(r'\*', '%', s))

def convert(l):
    conversion_table = {
        'and': ' and ',
        'or': ' or ',
        '==': ' = ',
        '=~': ' like ',
        '<': ' < ',
        '<=': ' <= ',
        '>': ' > ',
        '>=': ' >= '
    }
    def in_list(x, l):
        try:
            l.index(x)
            return True
        except ValueError:
            return False
    def simple_identifier(x):
        return in_list(x, ['Title', 'Year', 'Note', 'EndYear',
                           'Season', 'EpisodeNum', 'EpisodeTitle',
                           'FirstName', 'LastName', 'Num'])
    def valid_var(t, x):
        if t == 'Episode':
            return (valid_var('Serie', x) or 
                    in_list(x, ['Title', 'Year', 'Note', 'EndYear', 
                                'Season', 'EpisodeNum', 'EpisodeTitle']))
        elif t == 'Serie':
            return (valid_var('Movie', x) or x == 'EndYear')
        elif t == 'Movie':
            return in_list(x, ['Title', 'Year', 'Note', 'Genre', 'Language', 'Country'])
        elif t == 'Person':
            return in_list(x, ['FirstName', 'LastName', 'Num'])
    def combine(a, op, b):
        (res_a, params_a) = a
        (res_b, params_b) = b
        return (res_a + op + res_b, params_a + params_b)
    def helper(l):
        if l:
            if re.match(t_OPERATOR, l[0]):
                return combine(helper(l[1]), conversion_table[l[0]], helper(l[2]))
            elif re.match(t_COMPARATOR, l[0]):
                if l[0] == '=~':
                    return combine((l[1], []), conversion_table[l[0]], 
                                   ('? ', [convert_pattern_matching(l[2])]))
                if simple_identifier(l[1]):
                    return combine((l[1], []), conversion_table[l[0]], ('?', [l[2]]))
                elif l[1] == 'Genre' or l[1] == 'Country' or l[1] == 'Language':
                    return (' exists (select 1 from %s where %s.ID = W.ID and %s.%s = ?)' %
                            ((l[1],)*4), [l[2]])
                else:
                    raise QueryError('Unknown identifier: %s' % l[1])
            else:
                raise QueryError('Unknown operator: %s' % l[0])
        else:
            return ('', [])

    sort = False
    if re.match(t_SORT, l[0]):
        sort = True
        sort_op = l[0]
        sort_var = l[1]
        l = l[2]

    if satisfies(l, lambda x: (x == 'EpisodeNum' or
                               x == 'EpisodeTitle')):
        if satisfies(l, lambda x: not valid_var('Episode', x)):
            raise QueryError('Query contains invalid variable for episode')
        res = combine(('select W.ID from Work W, Serie, Episode where W.ID = Serie.ID and W.ID = Episode.ID and ',
                        []), '', helper(l))
        t = 'Episode'
    elif satisfies(l, lambda x: (x == 'EndYear')):
        if satisfies(l, lambda x: not valid_var('Serie', x)):
            raise QueryError('Query contains invalid variable for serie')
        res = combine(('select W.ID from Work W, Serie where W.ID = Serie.ID and ',
                        []), '', helper(l))
        t = 'Serie'
    elif satisfies(l, lambda x: (x == 'FirstName' or
                                 x == 'LastName')):
        if satisfies(l, lambda x: not valid_var('Person', x)):
            raise QueryError('Query contains invalid variable for person')
        res = combine(('select FirstName, LastName, Num from Person where ',
                        []), '', helper(l))
        t = 'Person'
    else:
        if satisfies(l, lambda x: not valid_var('Movie', x)):
            raise QueryError('Query contains invalid variable for movie')
        res = combine(('select W.ID from Work W where ', []), '', helper(l))
        t = 'Movie'

    if sort:
        if simple_identifier(sort_var):
            if valid_var(t, sort_var):
                sort = ' order by %s' % sort_var
                if sort_op == 'sort-':
                    sort += ' desc'
                l = l[2]
            else:
                raise QueryError('Invalid sort variable: %s' % sort_var)
        else:
            raise QueryError('Cannot sort by %s' % sort_var)
        res = (res[0] + sort, res[1])

    return (res, t)

# Page
class Search(BasePage):
    def get(self):
        loader = tornado.template.Loader('templates/')
        
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        
        # parse the query
        try:
            parsed = ply.yacc.parse(self.get_argument('search', ''))
            ((query, args), typeofdata) = convert(parsed)
            
            # execute the query
            cur.execute(query, *(args,))
            results = cur.fetchall()
            
            cur.close()
            
            self.write(loader.load('search.html').generate(results=results,
                                                           typeofdata=typeofdata))
        except QueryError as e:
            self.error('Your query was incorrect: %s' % e.message)
