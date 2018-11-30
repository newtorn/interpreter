# __author__: newtorn
# __date__: 2018-11-29
# expression: A  +   ( B  -   C ) * D + E  / F - (G - (H + I))

# token_type 【单词类型】
INTEGER, PLUS, MINUS, MUL, DIV, EOF = (
	'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF'
)

class Token(object):
	'''
	单词或令牌
	'''
	def __init__(self, type, value):
		self.type = type     #单词类型
		self.value = value   #单词的值

	def __str__(self):
		return 'Token:{type}, {value}'.format(
			type = self.type,
			value = self.value
		)

	def __repr__(self):
		return self.__str__()

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
		从字符序列中获取下一个字符
		'''
		self.pos += 1
		if self.pos > len(self.text) - 1:
			self.current_char = None
		else:
			self.current_char = self.text[self.pos]

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
			
			self.error()

		return Token(EOF, None)


class Interpreter(object):
	'''
	解释器
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
		返回因子的值
		'''
		token = self.current_token
		self.eat(INTEGER)
		return token.value

	def term(self):
		'''
		获取一个单词作为项 【目前仅支持整数】
		返回项的值
		'''
		result = self.factor()

		while self.current_token.type in (MUL, DIV):
			token = self.current_token
			if token.type == MUL:
				self.eat(MUL)
				result *= self.factor()
			elif token.type == DIV:
				self.eat(DIV)
				result /= self.factor()

		return result

	def expr(self):
		'''
		表达式含义分析与计算
		返回表达式的值
		'''
		result = self.term()

		while self.current_token.type in (PLUS, MINUS):
			token = self.current_token
			if token.type == PLUS:
				self.eat(PLUS)
				result += self.term()
			elif token.type == MINUS:
				self.eat(MINUS)
				result -= self.term()

		return result

def main():
	while True:
		try:
			text = input('>> ')
		except EOFError:
			break

		if not text:
			continue

		lexer = Lexer(text)
		inter = Interpreter(lexer)
		result = inter.expr()
		print(result)


if __name__ == '__main__':
	main()
