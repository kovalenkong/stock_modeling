import re

import numpy as np

functions = {
    '<': lambda arr, value: arr < value,
    '>': lambda arr, value: arr > value,
    '>=': lambda arr, value: arr >= value,
    '<=': lambda arr, value: arr <= value,
    '==': lambda arr, value: arr == value,
}


def get_statements(array: np.ndarray, *wheres):
    if len(wheres) == 0:
        raise ValueError('there should be at least one where statement')
    regex = r'^(?P<sign>([<>]=?|==))(?P<value>-?\d+(\.\d+)*)$'
    statements = []
    for where in wheres:
        if not isinstance(where, str):
            raise TypeError(f'where statement should be string type, got {type(where)}')
        if not re.fullmatch(regex, where):
            raise ValueError(f'can\' parse where statement: {where}')
        match = re.match(regex, where)
        sign = match.group('sign')
        value = float(match.group('value'))
        statements.append(functions[sign](array, value))
    return statements


def get_and_condition(statements) -> np.ndarray:
    return np.all(statements, axis=0)


def get_values(array: np.ndarray, *wheres):
    statements = get_statements(array, *wheres)
    cond = get_and_condition(statements)
    return array[np.where(cond)[0]]


def countifs(array: np.ndarray, *wheres):
    return len(get_values(array, *wheres))


def sumifs(array: np.ndarray, *wheres):
    return np.sum(get_values(array, *wheres))


def filter_(array: np.ndarray, *wheres) -> np.ndarray:
    return get_values(array, *wheres)
