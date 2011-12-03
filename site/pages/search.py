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
t_VALUE = r"(\"[^\"]+\"|[0-9]+)"
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
    def helper(l):
        if l:
            if re.match(t_OPERATOR, l[0]):
                return helper(l[1]) + conversion_table[l[0]] + helper(l[2])
            elif re.match(t_COMPARATOR, l[0]):
                if simple_identifier(l[1]):
                    return l[1] + conversion_table[l[0]] + l[2] + ' '
                elif l[1] == 'Genre' or l[1] == 'Country' or l[1] == 'Language':
                    return (l[2] +' in (select * from ' +
                            l[1] + ' where ' + l[1] + '.ID = W.ID) ')
        else:
            return ''
    if satisfies(l, lambda x: (x == 'EndYear' or
                               x == 'EpisodeNum' or
                               x == 'EpisodeTitle')):
        return 'select ID from Serie W where ' + helper(l)
    elif satisfies(l, lambda x: (x == 'FirstName' or
                                 x == 'LastName')):
        return 'select FirstName, LastName, Num from Person where ' + helper(l)
    else:
        return 'select ID from Work W where ' + helper(l)

# Page
class Search(tornado.web.RequestHandler):
    def post(self):
        l = ply.yacc.parse(self.get_argument('search', ''))
        self.write(convert(l))
        if satisfies(l, lambda x: x == 'EndYear'):
            self.write('Serie')
        elif satisfies(l, lambda x: (x == 'Season' or 
                                     x == 'EpisodeNum' or
                                     x == 'EpisodeTitle')):
            self.write('Episode')
        
        elif satisfies(l, lambda x: (x == 'FirstName' or
                                     x == 'LastName')):
            self.write('Person')
        elif satisfies(l, lambda x: x == 'Title'):
            self.write('Work')
        else:
            self.write(repr(l))


