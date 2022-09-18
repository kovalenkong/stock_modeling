from dataclasses import dataclass
from typing import List

from .tokens import TokenType


class Node:
    pass


@dataclass
class Literal(Node):
    kind: TokenType
    value: str


@dataclass
class Ident(Node):
    name: str


@dataclass
class BinaryExpr(Node):
    left: Node
    right: Node
    op: TokenType


@dataclass
class UnaryExpr(Node):
    left: Node
    op: TokenType


@dataclass
class Function(Node):
    name: str
    args: List[Node]


@dataclass
class Comparison(Node):
    left: Node
    right: Node
    op: TokenType
