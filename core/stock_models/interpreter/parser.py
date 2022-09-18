from typing import List

from .ast import (BinaryExpr, Comparison, Function, Ident, Literal, Node,
                  UnaryExpr)
from .exceptions import ParserError
from .lexer import Token
from .tokens import TokenType


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Node:
        self.pos = 0
        node = self.parse_comparison()
        cur_token = self.current_token()
        if cur_token.token_type != TokenType.EOF:
            raise ParserError('syntax error')
        return node

    def parse_comparison(self) -> Node:
        result = self.parse_add_sub()
        while not self.eof():
            token = self.current_token()
            if token.token_type in (TokenType.EQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
                self.next()
                right = self.parse_add_sub()
                result = Comparison(
                    left=result,
                    right=right,
                    op=token.token_type
                )
            else:
                break
        return result

    def parse_add_sub(self) -> Node:
        result = self.parse_multiplication()
        while not self.eof():
            token = self.current_token()
            if token.token_type in (TokenType.ADD, TokenType.SUB):
                self.next()
                right = self.parse_multiplication()
                result = BinaryExpr(
                    left=result,
                    right=right,
                    op=token.token_type
                )
            else:
                break
        return result

    def parse_multiplication(self) -> Node:
        result = self.parse_division()
        while not self.eof() and self.current_token().token_type == TokenType.MUL:
            self.next()
            right = self.parse_division()
            result = BinaryExpr(
                left=result,
                right=right,
                op=TokenType.MUL
            )
        return result

    def parse_division(self) -> Node:
        result = self.parse_exponential()
        while not self.eof() and self.current_token().token_type == TokenType.DIV:
            self.next()
            right = self.parse_exponential()
            result = BinaryExpr(
                left=result,
                right=right,
                op=TokenType.DIV
            )
        return result

    def parse_exponential(self) -> Node:
        result = self.parse_highest_priority()
        while not self.eof() and self.current_token().token_type == TokenType.EXP:
            self.next()
            right = self.parse_highest_priority()
            result = BinaryExpr(
                left=result,
                right=right,
                op=TokenType.EXP
            )
        return result

    def parse_highest_priority(self) -> Node:
        token = self.current_token()
        if token.token_type == TokenType.LPAREN:
            self.next()
            result = self.parse_comparison()
            cur_token = self.current_token()
            if cur_token.token_type != TokenType.RPAREN:
                raise ParserError('missing \')\'')
            self.next()
            return result
        elif token.token_type in (TokenType.DIGIT, TokenType.STRING):
            self.next()
            return Literal(
                kind=token.token_type,
                value=token.value
            )
        elif token.token_type == TokenType.IDENT:
            if self.next_token().token_type == TokenType.LPAREN:
                self.next()
                args: List[Node] = []
                while not self.eof():
                    self.next()
                    cur_token = self.current_token()
                    if cur_token.token_type == TokenType.RPAREN:
                        break
                    res = self.parse_comparison()
                    args.append(res)
                    cur_token = self.current_token()
                    if cur_token.token_type == TokenType.RPAREN:
                        break
                    elif cur_token.token_type == TokenType.DELIMITER:
                        continue
                    else:
                        raise ParserError(f'expected \';\' or \')\', got {cur_token.token_type}')
                self.next()
                return Function(
                    name=token.value,
                    args=args
                )
            else:
                self.next()
                return Ident(
                    name=token.value
                )
        elif token.token_type in (TokenType.ADD, TokenType.SUB):
            self.next()
            res = self.parse_highest_priority()
            return UnaryExpr(
                left=res,
                op=token.token_type
            )
        raise ParserError(f'unexpected token {token.token_type}')

    def next(self):
        self.pos += 1

    def current_token(self):
        return self.tokens[self.pos]

    def next_token(self):
        return self.tokens[self.pos + 1]

    def eof(self):
        return self.current_token().token_type == TokenType.EOF
