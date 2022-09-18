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


def summa(*args):
    total = 0
    for arg in args:
        if isinstance(arg, (int, float)):
            total += arg
        elif isinstance(arg, (list, np.ndarray)):
            total += sum(arg)
        else:
            raise TypeError(f'can\'t sum type {type(arg)}')
    return total


def length(*args):
    total = 0
    for arg in args:
        if isinstance(arg, (list, np.ndarray)):
            total += len(arg)
        else:
            total += 1
    return total


def get_slice(*args):
    """Возвращает сред массива"""
    if len(args) != 3:
        raise ValueError(f'expected 2 args, got {len(args)}')
    try:
        from_ = int(args[1])
        to = int(args[2])
    except ValueError:
        raise TypeError('expected two integers at 2 and 3 positions')
    arr = args[0]
    if not isinstance(arr, (list, np.ndarray, set, tuple)):
        raise TypeError(f'expected array at 1 position, got {type(arr)}')
    return arr[from_:to]


def minimum(*args):
    min_number = float('inf')
    for arg in args:
        if isinstance(arg, (list, np.ndarray, set, tuple)):
            n = min(arg)
        else:
            n = arg
        if arg < min_number:
            min_number = n
    return min_number


def maximum(*args):
    max_number = float('-inf')
    for arg in args:
        if isinstance(arg, (list, np.ndarray, set, tuple)):
            n = max(arg)
        else:
            n = arg
        if arg > max_number:
            max_number = n
    return max_number
