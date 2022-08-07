import ast
import operator
import re
from typing import Any, Dict, Union

import numpy as np


def eval_unaryop(node: ast.UnaryOp, context: dict) -> float:
    OPERATIONS = {
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    operand_value = eval_node(node.operand, context)
    apply = OPERATIONS[type(node.op)]
    return apply(operand_value)


def eval_binop(node: ast.BinOp, context: dict) -> float:
    OPERATIONS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
        ast.Pow: operator.pow,
    }

    left_value = eval_node(node.left, context)
    right_value = eval_node(node.right, context)
    apply = OPERATIONS[type(node.op)]
    return apply(left_value, right_value)


def eval_constant(node: ast.Constant, context: dict) -> float:
    return node.value


def eval_name(node: ast.Name, context: dict) -> float:
    return context[node.id]


def eval_expression(node: ast.Expression, context: dict) -> float:
    return eval_node(node.body, context)


def eval_compare(node: ast.Compare, context: dict) -> bool:
    OPERATORS = {
        ast.Eq: operator.eq,
        ast.Lt: operator.lt,
        ast.Gt: operator.gt,
        ast.LtE: operator.le,
        ast.GtE: operator.ge,
    }
    left = eval_node(node.left, context)
    comparators = [eval_node(i, context) for i in node.comparators]
    for x, y, op in zip([left] + comparators[:-1], comparators, node.ops):
        if not OPERATORS[type(op)](x, y):
            return False
    return True


def eval_call(node: ast.Call, context: dict) -> float:
    args = [eval_node(i, context) for i in node.args]
    kwargs = {}
    for i in node.keywords:
        k, v = eval_keyword(i, context)
        kwargs[k] = v
    res = context[node.func.id.lower()](*args, **kwargs)
    return res


def eval_bool(node: ast.BoolOp, context: dict) -> bool:
    OPERATORS = {
        ast.Or: any,
        ast.And: all,
    }
    values = [eval_node(i, context) for i in node.values]
    return OPERATORS[type(node.op)](values)


def eval_keyword(node: ast.keyword, context: dict) -> (str, Any):
    kname = node.arg
    kvalue = eval_node(node.value, context)
    return kname, kvalue


def eval_subscript(node: ast.Subscript, context: dict):
    slice_ = eval_node(node.slice, context)
    val = eval_node(node.value, context)
    return val[slice_]


def eval_slice(node: ast.Slice, context: dict) -> slice:
    lower = eval_node(node.lower, context) if node.lower else None
    step = eval_node(node.step, context) if node.step else None
    upper = eval_node(node.upper, context) if node.upper else node
    return slice(lower, upper, step)


def eval_index(node: ast.Index, context: dict) -> Any:
    return eval_node(node.value, context)


def eval_node(node: ast.AST, context: dict):
    EVALUATORS = {
        ast.Expression: eval_expression,
        ast.Constant: eval_constant,
        ast.Name: eval_name,
        ast.BinOp: eval_binop,
        ast.UnaryOp: eval_unaryop,

        ast.Compare: eval_compare,
        ast.Call: eval_call,
        ast.BoolOp: eval_bool,
        ast.Subscript: eval_subscript,
        ast.Index: eval_index,
        ast.Slice: eval_slice,
    }
    return EVALUATORS[type(node)](node, context)


def evaluate_formula(formula: str, context: dict) -> Union[float, bool]:
    node = ast.parse(formula, '<string>', mode='eval')
    return eval_node(node, context)


def replacer(formula: str) -> str:
    def f(match: re.Match):
        return match.group().lower()

    return re.sub(r'\s(and|or|in)\s', f, formula, flags=re.IGNORECASE).replace('\n', ' ')


def execute(formula: str, context: dict) -> Union[float, bool]:
    formula = replacer(formula)
    return evaluate_formula(formula, context)
