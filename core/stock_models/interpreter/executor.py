from typing import Any, Callable, Dict

from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser


def new_interpreter(formula: str, variables: Dict[str, Any], functions: Dict[str, Callable]) -> Interpreter:
    lexer = Lexer(formula)
    tokens = lexer.lex()
    parser = Parser(tokens)
    node = parser.parse()
    interpreter = Interpreter(variables, functions, node)
    return interpreter
