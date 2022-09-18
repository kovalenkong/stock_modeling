from dataclasses import dataclass, field
from typing import List, Union

import numpy as np
import pandas as pd

from .custom_formulas import countifs, filter_, length, sumifs, summa, get_slice, minimum, maximum
from .interpreter.executor import new_interpreter

_CONTEXT_FORMULAS = {
    'SUM': summa,
    'MEAN': lambda *args: np.mean(args),
    'STD': lambda i: np.std(i),
    'ABS': abs,
    'SQRT': lambda i: np.sqrt(i),
    'COUNT': length,
    'MAX': maximum,
    'MIN': minimum,
    'ROUND': lambda i: round(i),
    'COUNTIFS': countifs,
    'SUMIFS': sumifs,
    'FILTER': filter_,
    'AND': lambda *args: all(args),
    'OR': lambda *args: any(args),
    'MOD': lambda i, j: i % j,
    'SLICE': get_slice,
}


@dataclass
class Config:
    consumption: np.ndarray
    order_costs: float
    storage_costs: float
    delivery_time: int
    delay_time: int
    initial_stock: float
    delay: Union[float, int, List[int]]

    formula_point_refill: str
    formula_order_size: str
    formula_score: str = None


def build_author_model(
        config: Config
):
    consumption = config.consumption
    formula_point_refill = config.formula_point_refill
    formula_order_size = config.formula_order_size
    formula_score = config.formula_score
    period = len(consumption)
    outcome_order = np.zeros(period, dtype=float)  # заказ (ед)
    income_order = np.zeros(period, dtype=float)  # приход (ед)
    balance = np.zeros(period, dtype=float)  # остаток
    number_of_outcome_orders = 0  # количество невыполненных заявок
    delivery_number = 0

    context_constants = {
        'S': np.sum(config.consumption),
        'A': config.order_costs,
        'I': config.storage_costs,
        'Delivery': config.delivery_time,
        'Delay': config.delay_time,
        'Consumption': consumption.tolist(),
    }

    interpreter_formula_refill = new_interpreter(formula_point_refill, {}, _CONTEXT_FORMULAS)
    interpreter_formula_order_size = new_interpreter(formula_order_size, {}, _CONTEXT_FORMULAS)

    for i, el in enumerate(consumption):
        if i == 0:
            balance[0] = config.initial_stock
        else:
            # привозим заявку
            balance[i] = balance[i - 1] - consumption[i - 1] + income_order[i]
            if income_order[i] > 0:
                number_of_outcome_orders -= 1

        # update context
        context = {
            **context_constants,
            'balance': balance[i],
            'out': number_of_outcome_orders,
            'day': i,
        }
        interpreter_formula_refill.variables = context
        # если пора делать заявку
        if interpreter_formula_refill.execute():
            # делаем заказ
            interpreter_formula_order_size.variables = context
            order_size = interpreter_formula_order_size.execute()
            if order_size <= 0:
                continue
            outcome_order[i] = order_size
            number_of_outcome_orders += 1
            delivery_number += 1

            # заказ приедет через
            if isinstance(config.delay, (float, int)):
                if np.random.rand() < config.delay:
                    come_after = i + config.delivery_time + config.delay_time
                else:
                    come_after = i + config.delivery_time
                # если не "выходим за порог"
                if come_after < period:
                    income_order[int(come_after)] = order_size
            elif isinstance(config.delay, (list, tuple, set)):
                if delivery_number in config.delay:
                    come_after = i + config.delivery_time + config.delay_time
                else:
                    come_after = i + config.delivery_time
                # если не "выходим за порог"
                if come_after < period:
                    income_order[int(come_after)] = order_size

    context = {
        **context_constants,
        'Fact': balance,
        'Income': income_order,
        'Outcome': outcome_order,
    }  # todo
    score = None
    if formula_score is not None:
        interpreter_score = new_interpreter(formula_score, context, _CONTEXT_FORMULAS)
        score = interpreter_score.execute()
    return ModelAuthor(
        config, consumption, balance, income_order, outcome_order, score
    )


@dataclass
class ModelAuthor:
    _config: Config
    consumption: np.ndarray
    balance_start: np.ndarray
    balance_end: np.ndarray = field(init=False)
    income_order: np.ndarray
    outcome_order: np.ndarray
    score: float

    __df: pd.DataFrame = field(init=False, default=None)

    def __post_init__(self):
        self.balance_end = self.balance_start - self.consumption

    @property
    def df(self):
        if self.__df is None:
            self.__df = pd.DataFrame(
                np.transpose(
                    [self.consumption, self.income_order, self.outcome_order, self.balance_start, self.balance_end]),
                columns=['consumption', 'income', 'outcome', 'balance', 'balance_end']
            )
        return self.__df

    def total_outcome(self) -> (int, float):
        f = self.df[self.df['outcome'] > 0]['outcome']
        return f.count(), f.sum()

    def total_income(self) -> (int, float):
        f = self.df[self.df['income'] > 0]['income']
        return f.count(), f.sum()

    def base_info(self) -> dict:
        df = self.df
        return {
            'Потребность (S)': self._config.consumption.sum(),
            'Период (N)': len(self._config.consumption),
            'Затраты на пополнение запаса (A)': self._config.order_costs,
            'Затраты на хранение ед.запаса (I)': self._config.storage_costs,
            'Дней с отрицательным остатком': df[df['balance_end'] < 0]['balance_end'].count(),
            'Доля дней с отрицательным остатком': df[df['balance_end'] < 0]['balance_end'].count() / df.shape[0],
            'Средний остаток': df[['balance', 'balance_end']].mean().mean(),
            'Значение целевой функции': self.score,
        }

    def full_info(self) -> dict:
        return self.base_info()
