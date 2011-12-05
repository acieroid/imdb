import tornado.ioloop
import tornado.web
import tornado.template
import sqlite3
import ply.lex
import ply.yacc
import re

# Query language
tokens = (
    "OPERATOR",
    "COMPARATOR",
    "IDENTIFIER",
    "VALUE",
    "LPAREN",
    "RPAREN",
    "SPACE"
)

precedence = (
    ("left", "OPERATOR"),
)

t_OPERATOR = r"(and|or)"
t_COMPARATOR = r"(>=|<=|<|>|==)"
t_IDENTIFIER = r"[A-Z][a-zA-Z_]+"
def t_VALUE(t):
    r"(\"[^\"]+\"|[0-9]+)"
    if t.value[0] == '"':
        t.value = t.value[1:-1]
    else:
        t.value = int(t.value)
    return t
t_LPAREN = "\("
t_RPAREN = "\)"
t_ignore_SPACE = r"\s+"

def t_error(t):
    raise TypeError("Error when lexing '%s'" % t.value)

ply.lex.lex()

def p_paren(p):
    "condition : LPAREN condition RPAREN"
    p[0] = p[2]

def p_op(p):
    "condition : condition OPERATOR condition"
    p[0] = [p[2], p[1], p[3]]

def p_comp(p):
    "condition : IDENTIFIER COMPARATOR VALUE"
    p[0] = [p[2], p[1], p[3]]

def p_error(p):
    raise TypeError("Syntax error at '%s'" % p.value)

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

def convert(l):
    conversion_table = {
        'and': ' and ',
        'or': ' or ',
        '==': ' = ',
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
                           'FirstName', 'LastName'])
    def combine(a, op, b):
        (res_a , params_a) = a
        (res_b, params_b) = b
        return (res_a + op + res_b, params_a + params_b)
    def helper(l):
        # TODO: also return a list containing the l[2] and replace l[2] with '?'
        if l:
            if re.match(t_OPERATOR, l[0]):
                return combine(helper(l[1]), conversion_table[l[0]], helper(l[2]))
#                return helper(l[1]) + conversion_table[l[0]] + helper(l[2])
            elif re.match(t_COMPARATOR, l[0]):
                if simple_identifier(l[1]):
                    return combine((l[1], []), conversion_table[l[0]], ('?', [l[2]]))
#                    return l[1] + conversion_table[l[0]] + l[2] + ' '
                elif l[1] == 'Genre' or l[1] == 'Country' or l[1] == 'Language':
                    return combine(('?', [l[2]]), 'in (select * from ' + l[1] 
                                   + ' where ' + l[1] + '.ID = W.ID) ', ('', []))
#                    return (l[2] +' in (select * from ' +
#                            l[1] + ' where ' + l[1] + '.ID = W.ID) ')
        else:
            return ('', [])
    if satisfies(l, lambda x: (x == 'EndYear' or
                               x == 'EpisodeNum' or
                               x == 'EpisodeTitle')):
        return (combine(('select ID from Serie W where ', []), '', helper(l)), 
                'Serie')
    elif satisfies(l, lambda x: (x == 'FirstName' or
                                 x == 'LastName')):
        return (combine(('select FirstName, LastName, Num from Person where ', 
                        []), '', helper(l)),
                'Person')
    else:
        return (combine(('select ID from Work W where ', []), '', helper(l)),
                'Movie')

# Page
class Search(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader("templates/")
        
        conn = sqlite3.connect("db.sqlite")
        cur = conn.cursor()
        
        # parse the query
        parsed = ply.yacc.parse(self.get_argument('search', ''))
        ((query, args), typeofdata) = convert(parsed)
        
        # execute the query
        cur.execute(query, *args)
        results = cur.fetchall()
        
        cur.close()

        self.write(loader.load('search.html').generate(results=results,
                                                       typeofdata=typeofdata))

