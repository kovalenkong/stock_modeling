from dataclasses import dataclass
from typing import List

from .exceptions import LexerError
from .tokens import TokenType


@dataclass
class Token:
    token_type: TokenType
    value: str


class Lexer:
    def __init__(self, formula: str):
        self.pos = 0
        self.formula = formula

    def lex(self):
        tokens: List[Token] = []
        while not self.eof():
            char = self.formula[self.pos]
            if char == '(':
                token = Token(TokenType.LPAREN, '(')
            elif char == ')':
                token = Token(TokenType.RPAREN, ')')
            elif char == '+':
                token = Token(TokenType.ADD, '+')
            elif char == '-':
                token = Token(TokenType.SUB, '-')
            elif char == '*':
                token = Token(TokenType.MUL, '*')
            elif char == '/':
                token = Token(TokenType.DIV, '/')
            elif char == '^':
                token = Token(TokenType.EXP, '^')
            elif char == ';':
                token = Token(TokenType.DELIMITER, ';')
            elif char == '"':
                token = Token(TokenType.STRING, self._read_string())
            elif char == '=':
                token = Token(TokenType.EQ, '=')
            elif char in ('<', '>'):
                comparison_op = self._read_comparison()
                ops = {
                    '<': TokenType.LT,
                    '>': TokenType.GT,
                    '>=': TokenType.GTE,
                    '<=': TokenType.LTE,
                }
                if comparison_op not in ops:
                    raise LexerError(f'unexpected comparison operator {comparison_op}')
                token = Token(ops[comparison_op], comparison_op)
            elif char.isdigit():
                number = self._read_number()
                token = Token(TokenType.DIGIT, number)
            elif char.isalpha():
                token = Token(TokenType.IDENT, self._read_ident())
            elif char.isspace():
                self.next()
                continue
            else:
                raise LexerError(f'unexpected char {char}')
            tokens.append(token)
            self.pos += 1
        tokens.append(Token(TokenType.EOF, ''))
        return tokens

    def _read_string(self) -> str:
        res = ''
        self.pos += 1
        while not self.eof():
            char = self.char()
            if char == '"':
                return res
            self.pos += 1
            res += char
        return res

    def _read_comparison(self) -> str:
        res = ''
        while not self.eof():
            char = self.char()
            if char not in ('>', '<', '='):
                self.prev()
                return res
            self.next()
            res += char
        return res

    def _read_number(self) -> str:
        res = ''
        has_comma = False
        while not self.eof():
            char = self.char()
            if char.isdigit():
                self.next()
                res += char
            elif char == ',' and not has_comma:
                self.next()
                has_comma = True
                res += char
            else:
                self.prev()
                return res
        self.prev()
        return res

    def _read_ident(self) -> str:
        res = ''
        while not self.eof():
            char = self.char()
            if not char.isalpha():
                self.prev()
                return res
            res += char
            self.next()
        return res

    def eof(self) -> bool:
        return self.pos >= len(self.formula)

    def char(self) -> str:
        return self.formula[self.pos]

    def next(self):
        self.pos += 1

    def prev(self):
        self.pos -= 1
