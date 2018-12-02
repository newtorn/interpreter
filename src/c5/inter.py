# __author__: newtorn
# __date__: 2018-12-1

###############################################################################
#                                                                             #
#  GRAMMAR                                                                    #
#                                                                             #
###############################################################################

'''
	program : compound_statement DOT

    compound_statement : BEGIN statement_list END

    statement_list : statement
                   | statement SEMI statement_list

    statement : compound_statement
              | assignment_statement
              | empty

    assignment_statement : variable ASSIGN expr

    empty :

    expr: term ((PLUS | MINUS) term)*

    term: factor ((MUL | DIV) factor)*

    factor : PLUS factor
           | MINUS factor
           | INTEGER
           | LPAREN expr RPAREN
           | variable

    variable: ID
'''

###############################################################################
#                                                                             #
#  LEXER                                                                      #
#                                                                             #
###############################################################################

# Token types 【单词类型】
(
	INTEGER, PLUS, MINUS, MUL,
	DIV, LPAREN, RPAREN, ID, 
	BEGIN, END, ASSIGN, SEMI,
	DOT, EOF
) = (
	'INTEGER', 'PLUS', 'MINUS', 'MUL', 
	'DIV', 'LPAREN', 'RPAREN', 'ID', 
	'BEGIN', 'END', 'ASSIGN', 'SEMI',
	'DOT', 'EOF'
)

class Token(object):
	'''
	单词或令牌
	'''
	def __init__(self, type, value):
		self.type = type     #单词类型
		self.value = value   #单词的值

	def __str__(self):
		return 'Token({type}, {value})'.format(
			type = self.type,
			value = repr(self.value)
		)

	def __repr__(self):
		return self.__str__()

RESERVED_KEYWORDS = {
	'BEGIN' : Token('BEGIN', 'BEGIN'),
	'END' : Token('END', 'END')
}

class Lexer(object):
	'''
	词法分析器
	'''
	def __init__(self, text):
		self.text = text
		self.pos = 0
		self.current_char = self.text[self.pos]

	def error(self):
		raise Exception('Invalid character')

	def advance(self):
		'''
		从字符序列中获取下一个字符，pos指针增加1
		'''
		self.pos += 1
		if self.pos > len(self.text) - 1:
			self.current_char = None
		else:
			self.current_char = self.text[self.pos]

	def peek(self):
		'''
		从字符序列中获取下一个字符，但不移动pos指针
		'''
		peek_pos = self.pos + 1
		if peek_pos > len(self.text) - 1:
			return None
		else:
			return self.text[peek_pos]

	def skip_whitespace(self):
		'''
		忽略空白字符
		'''
		while self.current_char is not None and self.current_char.isspace():
			self.advance()

	def integer(self):
		'''
		获取一个整数字符序列
		返回转换后的字符序列【整数】
		'''
		result = ''
		while self.current_char is not None and self.current_char.isdigit():
			result += self.current_char
			self.advance()
		return int(result)

	def _id(self):
		'''
		从字符序列中获取标识符
		'''
		result = ''
		while self.current_char is not None and self.current_char.isalnum():
			result += self.current_char
			self.advance()
		token = RESERVED_KEYWORDS.get(result, Token(ID, result))
		return token

	def get_next_token(self):
		'''
		获取下一个单词Token
		返回一个单词Token
		'''
		while self.current_char is not None:

			if self.current_char.isspace():
				self.skip_whitespace()
				continue

			if self.current_char.isdigit():
				return Token(INTEGER, self.integer())

			if self.current_char == '+':
				self.advance()
				return Token(PLUS, '+')

			if self.current_char == '-':
				self.advance()
				return Token(MINUS, '-')

			if self.current_char == '*':
				self.advance()
				return Token(MUL, '*')

			if self.current_char == '/':
				self.advance()
				return Token(DIV, '/')

			if self.current_char == '(':
				self.advance()
				return Token(LPAREN, '(')

			if self.current_char == ')':
				self.advance()
				return Token(RPAREN, ')')

			if self.current_char.isalpha():
				return self._id()

			if self.current_char == ':' and self.peek() == '=':
				self.advance()
				self.advance()
				return Token(ASSIGN, ':=')

			if self.current_char == ';':
				self.advance()
				return Token(SEMI, ';')

			if self.current_char == '.':
				self.advance()
				return Token(DOT, '.')
			
			self.error()

		return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
	'''
	抽象语法树
	'''
	pass

class BinOp(AST):
	'''
	二元算子
	'''
	def __init__(self, left, op, right):
		self.left = left			#左孩子
		self.token = self.op = op 	#操作符
		self.right = right			#右孩子

class UnaryOp(AST):
	'''
	一元算子
	'''
	def __init__(self, op, expr):
		self.token = self.op = op 	#操作符
		self.expr = expr 			#表达式

class Num(AST):
	'''
	数字
	'''
	def __init__(self, token):
		self.token = token
		self.value = token.value

class Compound(AST):
	'''
	复合节点
	'''
	def __init__(self):
		self.children = [] #子节点

class Assign(AST):
	'''
	赋值操作
	'''
	def __init__(self, left, op, right):
		self.left = left 			#左值
		self.token = self.op = op 	#赋值操作符
		self.right = right 			#右值

class Var(AST):
	'''
	变量
	'''
	def __init__(self, token):
		self.token = token
		self.value = token.value

class NoOp(AST):
	'''
	空操作
	'''
	pass

class Parser(object):
	'''
	语法解析器
	'''
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = self.lexer.get_next_token()

	def error(self):
		raise Exception('Invalid syntax')

	def eat(self, token_type):
		'''
		切换当前的单词为下一个单词
		'''
		if self.current_token.type == token_type:
			self.current_token = self.lexer.get_next_token()
		else:
			self.error()

	def factor(self):
		'''
		获取一个单词作为因子 【目前仅支持整数】
		返回因子节点
		语法:
		factor : (PLUS|MINUS) INTEGER | LPAREN expr RPAREN
		'''
		token = self.current_token
		if token.type == PLUS:
			self.eat(PLUS)
			node = UnaryOp(token, self.factor())
			return node
		elif token.type == MINUS:
			self.eat(MINUS)
			node = UnaryOp(token, self.factor())
			return node
		elif token.type == INTEGER:
			self.eat(INTEGER)
			return Num(token)
		elif token.type == LPAREN:
			self.eat(LPAREN)
			node = self.expr()
			self.eat(RPAREN)
			return node
		else:
			node = self.variable()
			return node

	def term(self):
		'''
		获取一个单词作为项 【目前仅支持整数】
		返回项节点
		语法:
		term : factor ((MUL|DIV) factor)*
		'''
		node = self.factor()

		while self.current_token.type in (MUL, DIV):
			token = self.current_token
			if token.type == MUL:
				self.eat(MUL)
			elif token.type == DIV:
				self.eat(DIV)
			
			node = BinOp(node, token, self.factor())

		return node

	def expr(self):
		'''
		表达式含义分析与计算
		返回表达式跟节点
		语法:
		expr : term ((PLUS|MINUS) term)*
		'''
		node = self.term()

		while self.current_token.type in (PLUS, MINUS):
			token = self.current_token
			if token.type == PLUS:
				self.eat(PLUS)
			elif token.type == MINUS:
				self.eat(MINUS)
			
			node = BinOp(node, token, self.term())

		return node

	def statement(self):
		'''
		语句
		'''
		if self.current_token.type == BEGIN:
			node = self.compound_statement()
		elif self.current_token.type == ID:
			node = self.assignment_statement()
		else:
			node = self.empty()
		return node

	def assignment_statement(self):
		'''
		赋值语句
		'''
		left = self.variable()
		token = self.current_token
		self.eat(ASSIGN)
		right = self.expr()
		node = Assign(left, token, right)
		return node

	def variable(self):
		'''
		变量
		'''
		node = Var(self.current_token)
		self.eat(ID)
		return node

	def empty(self):
		'''
		空操作
		'''
		return NoOp()

	def statement_list(self):
		'''
		多条语句
		'''
		node = self.statement()

		results = [node]

		while self.current_token.type == SEMI:
			self.eat(SEMI)
			results.append(self.statement())

		if self.current_token.type == ID:
			self.error()

		return results

	def compound_statement(self):
		'''
		复合语句
		'''
		self.eat(BEGIN)
		nodes = self.statement_list()
		self.eat(END)

		root = Compound()
		for node in nodes:
			root.children.append(node)

		return root

	def program(self):
		'''
		程序解析入口
		'''
		node = self.compound_statement()
		self.eat(DOT)
		return node

	def parse(self):
		'''
		解析出语法树
		'''
		node = self.program()
		if self.current_token.type != EOF:
			self.error()
		return node


###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
	'''
	节点访问器
	'''
	def visit(self, node):
		'''
		访问节点，如果子类没有提供访问方法，将调用默认访问方法

		'''
		method_name = 'visit_' + type(node).__name__
		visitor = getattr(self, method_name, self.generic_visit)
		return visitor(node)

	def generic_visit(self, node):
		'''
		节点默认访问方法
		'''
		raise Exception("No visit_{} method".format(node.__name__))

class Interpreter(NodeVisitor):
	'''
	解释器
	'''

	GLOBAL_SCOPE = {}

	def __init__(self, parser):
		self.parser = parser
	
	def visit_BinOp(self, node):
		'''
		二元算子节点访问
		'''
		if node.op.type == PLUS:
			return self.visit(node.left) + self.visit(node.right)
		elif node.op.type == MINUS:
			return self.visit(node.left) - self.visit(node.right)
		elif node.op.type == MUL:
			return self.visit(node.left) * self.visit(node.right)
		elif node.op.type == DIV:
			return self.visit(node.left) / self.visit(node.right)

	def visit_UnaryOp(self, node):
		'''
		一元算子节点访问
		'''
		op = node.op.type
		if op == PLUS:
			return +self.visit(node.expr)
		elif op == MINUS:
			return -self.visit(node.expr)

	def visit_Num(self, node):
		'''
		数字节点访问
		'''
		return node.value

	def visit_Compound(self, node):
		'''
		复合节点访问
		'''
		for child in node.children:
			self.visit(child)

	def visit_NoOp(self, node):
		'''
		空操作
		'''
		pass

	def visit_Assign(self, node):
		var_name = node.left.value
		self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

	def visit_Var(self, node):
		var_name = node.value
		val = self.GLOBAL_SCOPE.get(var_name)
		if val is None:
			raise NameError(repr(var_name))
		else:
			return val

	def interpret(self):
		'''
		解释语法树
		'''
		tree = self.parser.parse()
		if tree is None:
			return ''
		return self.visit(tree)


def main():
	while True:
		try:
			text = input('>> ')
		except EOFError:
			break

		if not text:
			continue

		lexer = Lexer(text)
		parser = Parser(lexer)
		interpreter = Interpreter(parser)
		interpreter.interpret()
		print(interpreter.GLOBAL_SCOPE)


if __name__ == '__main__':
	main()
