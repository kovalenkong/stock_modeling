from dataclasses import dataclass, field
from typing import List, Union

import numpy as np
import pandas as pd

from ._formula_parser import execute

_CONTEXT_FORMULAS = {
    'sum': sum,
    'mean': lambda i: np.mean(i),
    'std': lambda i: np.std(i),
    'abs': abs,
    'sqrt': lambda i: np.sqrt(i),
    'len': len,
    'max': lambda i: max(i),
    'min': lambda i: min(i),
}

DOC = """
Данный фреймворк позволяет описать любую модель управления запасами двумя формулами.

- _Формула нахождения точки пополнения заказа_: формула, которая определяет, _нужно ли_ делать заказ.
Данная формула должна вернуть значение TRUE либо FALSE. Соответственно, если формула возвращает TRUE - 
заказ будет размещен в день вычисления формулы.
- _Формула размера заказа_: формула, которая определяет размер заказа (заказ будет размещен в день, 
когда формула нахождения точки пополнения заказа вернула TRUE).
Формула должна вернуть число (кроме того, формула может быть константой - в этом случае каждый раз будет размещаться 
один и тот же размер заказа)
- _Оценивающая функция_ (опционально): функция, которая должна вернуть число. Данная функция используется для оценки качества модели:
например, формула может суммировать общие затраты (если главной задачей является снижение общих затрат).

##### Константы
- `S` - сумма потребления за весь период
- `A` - затраты на заказ
- `I` - затраты на хранение
- `Delivery` - время доставки
- `Delay` - время возможной задержки
- `Consumption` - потребление (последовательность)

##### Переменные
- `iDay` - индекс текущего дня (начиная с нуля)
- `curBalance` - баланс текущего дня
- `nOut` - количество отправленных но не привезенных заявок

##### Формулы
- `SUM(<последовательность>)` - суммирует диапазон
- `MEAN(<последовательность>)` - находит среднее значение
- `STD(<последовательность>)` - находит стандартное отклонение величины
- `LEN(<последовательность>)` - возвращает длину последовательности
- `MAX(<последовательность>)` - максимальное число из последовательности
- `MIN(<последовательность>)` - минимальное число из последовательности
- `ABS(<число>)` - возвращает модуль числа
- `SQRT(<число>)` - возвращает корень числа

##### Математические операции
- `+` - сложение
- `-` - вычитание
- `*` - умножение
- `/` - деление
- `//` - деление нацело
- `%` остаток от деления
- `**` - возведение в степень

##### Логические операции (возвращают TRUE либо FALSE)
- `>` - значение слева больше значения справа
- `<` - значение слева меньше значения справа
- `>=` - значение слева больше или равно значения справа
- `<=` - значение слева меньше или равно значения справа
- `==` - значение слева равно значения справа
- `OR` - логическое "или"
- `AND` - логическое "и"

Пример:

В соответствии со стилем и синтаксиса данного минифреймворка, можно переписать, например, метод ФРЗ.
Формула нахождения точки пополнения заказа
```logic
balance < (S/LEN(consumption))*delay + delivery*(S/LEN(consumption))
```

_Оценивающая функция_: в формуле оценивающей функции доступны все функции и константы, а также:

- `balance` (<i>последовательность</i>) - остаток на начало дня
- `outcome` (<i>последовательность</i>) - список значений отправленных заявок
- `income` (<i>последовательность</i>) - список значений пришедших заявок
"""


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

    CONTEXT_CONSTANTS = {
        'S': np.sum(config.consumption),
        'A': config.order_costs,
        'I': config.storage_costs,
        'Delivery': config.delivery_time,
        'Delay': config.delay_time,
        'Consumption': consumption.tolist(),
    }

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
            **_CONTEXT_FORMULAS,
            **CONTEXT_CONSTANTS,
            'curBalance': balance[i],
            'nOut': number_of_outcome_orders,
            'iDay': i,
        }
        # если пора делать заявку
        if execute(formula_point_refill, context):
            # делаем заказ
            order_size = execute(formula_order_size, context)
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
        **_CONTEXT_FORMULAS,
        **CONTEXT_CONSTANTS,
        'balance': balance,
        'income': income_order,
        'outcome': outcome_order
    }  # todo

    score = execute(formula_score, context) if formula_score else None
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
