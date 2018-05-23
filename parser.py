
import plex



class ParseError(Exception):
	
	pass



class MyParser:
	
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		letter = plex.Range("AZaz")
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
		
		
		self.scanner = plex.Scanner(lexicon,fp)
		
	
		self.la,self.val = self.next_token()


	def next_token(self):
		
		
		return self.scanner.read()		

	
	
	

	def match(self,token):
		
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		
		
		self.create_scanner(fp)
		
		
		self.session()
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
		
            self.match("IDENTIFIER")
            self.match("=")
            self.expr()
        elif self.la == "print":
		
            self.match("print")
            self.expr()
        else:
		
            raise ParseError("Excpected: identifier or print")	
	
	def expr(self):
        
        if self.la in ["(", "not", "IDENTIFIER", "True", "False"]:
		
            self.term()
            self.term_tail()
        else:
            raise ParseError("Excpected: '(' or IDENTIFIER or boool value")
	
	def term_tail(self):
        
        if self.la == "or":
		
            self.orp()
            self.term()
            self.term_tail()
            return
        elif self.la in ["IDENTIFIER", "print", ")"] or self.la is None:
            return
        else:
            raise ParseError("Excpected: 'or'")
	
	def term(self):
       
        if self.la in ["(", "not", "IDENTIFIER", "True", "False"]:
		
            self.factor_fnotp()
            self.factor()
            return
        else:
            raise ParseError("Excpected: '(' or IDENTIFIER or boool value")
	
	 def factor(self):
  
         if self.la == "and":
		
            self.andp()
            self.factor_and_fnotp()
            self.factor()
            return
         elif self.la in ["or", "print", "IDENTIFIER", ")"] or self.la is None:
            return
         else:
            raise ParseError("Excpected: 'and'")
	
	def factor_fnotp(self):
      
        self.notp()
        if self.la == '(':
		
            self.match('(')
            self.expr()
            self.match(')')
            return
        elif self.la == "IDENTIFIER":
            self.match(self.la)
        elif self.la in ["True", "False"]:
            self.match(self.la)
        else:
            raise ParseError("Excpected: id, (expr), values")
	
	def orp(self):
     
        if self.la == "or":
            self.match("or")
        else:
            raise ParseError("Excpected: 'or'")
	
	def andp(self):
       
        if self.la == "and":
            self.match("and")
        else:
            raise ParseError("Excpected: 'and'")
	
	def notp(self):
 
        if self.la == "not":
            self.match("not")
        else:
            return
	
	
		



parser = MyParser()


with open("recursive-descent-parsing.txt","r") as fp:

	
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))


