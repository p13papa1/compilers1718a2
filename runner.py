
import plex


class ParseError(Exception):
    pass


class RunError(Exception):
    pass


class MyParser():

    def __init__(self):
        self.st = {}
        self.not_op = None

    def create_scanner(self, fp):
        letter = plex.Range("azAZ")
        digit = plex.Range("09")

        keywords = plex.Str("print", "not", "and", "or")
        true_keyword = plex.NoCase(plex.Str("true", "t", "1"))
        false_keyword = plex.NoCase(plex.Str("false", "f", "0"))
        identifier = letter + plex.Rep(letter | digit)
        assign = plex.Str("=")
        parenthesis = plex.Str("(", ")")
        space = plex.Rep1(plex.Any(" \n\t"))

        lexicon = plex.Lexicon([
            (keywords, plex.TEXT),
            (true_keyword, "True"),
            (false_keyword, "False"),
            (identifier, "IDENTIFIER"),
            (assign, "="),
            (parenthesis, plex.TEXT),
            (space, plex.IGNORE)
        ])

        self.scanner = plex.Scanner(lexicon, fp)
        self.la, self.val = self.next_token()

    def next_token(self):
        return self.scanner.read()

    def match(self, token):
        if self.la == token:
            self.la, self.val = self.next_token()
        else:
            raise ParseError("Excpected: ", self.la)

    def parse(self, fp):
        self.create_scanner(fp)
        self.stmt_list()

    def stmt_list(self):
      
        if self.la in ["IDENTIFIER", "print"]:
            self.stmt()
            self.stmt_list()
        elif self.la is None:
            return
        else:
            raise ParseError("Excpected: identifier or print")

    def stmt(self):
      
        if self.la == "IDENTIFIER":
            varname = self.val
            self.match("IDENTIFIER")
            self.match("=")
            self.st[varname] = self.expr()
        elif self.la == "print":
            self.match("print")
            print(self.expr())
        else:
            raise ParseError("Excpected: identifier or print")

    def expr(self):
 
        if self.la in ["(", "not", "IDENTIFIER", "True", "False"]:
            t = self.term()
            tt = self.term_tail()
            if tt is None:
                return t
            if tt[0] == "or":
                return self.or_operation(t, tt[1])
        else:
            raise ParseError("Excpected: '(' or IDENTIFIER or boool value")

    def term_tail(self):
      
        if self.la == "or":
            op = self.orp()
            t = self.term()
            tt = self.term_tail()
            if tt is None:
                return op, t
            if tt[0] == "or":
                return op, self.or_operation(t, tt[1])
        elif self.la in ["IDENTIFIER", "print", ")"] or self.la is None:
            return
        else:
            raise ParseError("Excpected: 'or'")

    def term(self):
   
        if self.la in ["(", "not", "IDENTIFIER", "True", "False"]:
            f = self.factor()
            ft = self.factor_tail()
            if ft is None:
                return f
            if ft[0] == "and":
                return self.and_operation(f, ft[1])
        else:
            raise ParseError("Excpected: '(' or IDENTIFIER or boool value")

    def factor_tail(self):
      
        if self.la == "and":
            op = self.andp()
            f = self.factor()
            ft = self.factor_tail()
            if ft is None:
                return op, f
            if ft[0] == "and":
                return op, self.and_operation(f, ft[1])
        elif self.la in ["or", "print", "IDENTIFIER", ")"] or self.la is None:
            return
        else:
            raise ParseError("Excpected: 'or' or 'and'")

    def factor(self):
      
        not_op = self.notp()
        if self.la == '(':
            self.match('(')
            e = self.expr()
            self.match(')')
            return e
        elif self.la == "IDENTIFIER":
            varname = self.val
            self.match(self.la)
            if varname in self.st:
                if not_op == "not":
                    return self.not_operation(self.st[varname])
                else:
                    return self.st[varname]
            raise RunError("Unitialized variable: ", varname)
        elif self.la in ["True", "False"]:
            token = self.la
            self.match(token)
            if not_op == "not":
                return self.not_operation(token)
            else:
                return token
        else:
            raise ParseError("Excpected: id, (expr), values")

    def orp(self):
     
        if self.la == "or":
            self.match("or")
            return "or"
        else:
            raise ParseError("Excpected: 'or'")

    def andp(self):
    
        if self.la == "and":
            self.match("and")
            return "and"
        else:
            raise ParseError("Excpected: 'and'")

    def notp(self):
      
        if self.la == "not":
            self.match("not")
            return "not"
        else:
            return

    def or_operation(self, a, b):
        if a == "False" and b == "False":
            return "False"
        else:
            return "True"

    def and_operation(self, a, b):
        if a == "True" and b == "True":
            return "True"
        else:
            return "False"

    def not_operation(self, a):
        if a == "False":
            return "True"
        else:
            return "False"
