from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .ast import (BinaryExpr, Comparison, Function, Ident, Literal, Node,
                  UnaryExpr)
from .exceptions import InterpreterError
from .tokens import TokenType


class Interpreter:
    def __init__(self, variables: Dict[str, Any], functions: Dict[str, Callable], node: Node):
        self.variables = variables
        self.functions = functions
        self.node = node

    def set_function(self, name: str, func: Callable):
        self.functions[name] = func

    def set_variable(self, name: str, value: Any):
        self.variables[name] = value

    def execute(self):
        return self._execute(self.node)

    def _execute(self, node: Node):
        if isinstance(node, BinaryExpr):
            left = self._execute(node.left)
            right = self._execute(node.right)
            if node.op == TokenType.ADD:
                return left + right
            elif node.op == TokenType.SUB:
                return left - right
            elif node.op == TokenType.MUL:
                return left * right
            elif node.op == TokenType.DIV:
                return left / right
            elif node.op == TokenType.EXP:
                return left ** right
            raise InterpreterError(f'unimplemented binary operation {node.op}')
        elif isinstance(node, Literal):
            if node.kind == TokenType.DIGIT:
                return float(node.value.replace(',', '.'))
            elif node.kind == TokenType.STRING:
                return node.value
            raise InterpreterError(f'unimplemented literal type {node.kind}')
        elif isinstance(node, Ident):
            if node.name not in self.variables:
                raise InterpreterError(f'variable {node.name} not found')
            return self.variables[node.name]
        elif isinstance(node, Function):
            if node.name not in self.functions:
                raise InterpreterError(f'function {node.name} not found')
            args: List[Node] = []
            for arg in node.args:
                args.append(self._execute(arg))
            function = self.functions[node.name]
            return function(*args)
        elif isinstance(node, UnaryExpr):
            res = self._execute(node.left)
            if node.op == TokenType.ADD:
                return res
            elif node.op == TokenType.SUB:
                return -res
            raise InterpreterError(f'unexpected unary operator {node.op}')
        elif isinstance(node, Comparison):
            left = self._execute(node.left)
            right = self._execute(node.right)
            if node.op == TokenType.EQ:
                return left == right
            elif node.op == TokenType.LT:
                return left < right
            elif node.op == TokenType.GT:
                return left > right
            elif node.op == TokenType.LTE:
                return left <= right
            elif node.op == TokenType.GTE:
                return left >= right
            raise InterpreterError(f'unexpected comparison token {node.op}')
        raise InterpreterError(f'unimplemented node type {type(node)}')
