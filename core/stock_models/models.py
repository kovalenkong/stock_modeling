from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import Config


@dataclass
class BaseModel:
    _config: Config
    consumption: np.ndarray
    balance_start: np.ndarray
    balance_end: np.ndarray = field(init=False)
    income_order: np.ndarray
    outcome_order: np.ndarray

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
            'Q*': self._config.q,
            'Дней с отрицательным остатком': df[df['balance_end'] < 0]['balance_end'].count(),
            'Доля дней с отрицательным остатком': df[df['balance_end'] < 0]['balance_end'].count() / df.shape[0],
            # 'Средний остаток': df['balance'].mean(),  # TODO
            'Средний остаток': df[['balance', 'balance_end']].mean().mean(),
        }

    def full_info(self) -> dict:
        raise NotImplementedError


@dataclass
class ModelFRZ(BaseModel):
    delivery_expiration_time: float  # срок расходования поставки
    expected_consumption: float
    expected_consumption_during_delivery: float  # ожидаемое потребление за время поставки
    max_expected_consumption: float  # максимальное потребление за время поставки
    safety_stock: float  # страховой запас
    threshold_level: float  # пороговый уровень
    max_stock: float  # максимальный запас
    expiration_time_to_threshold_level: float  # срок расходования запасов до порогового уровня

    def full_info(self) -> dict:
        specific_info = {
            'Срок расходования поставки': self.delivery_expiration_time,
            'Ожидаемое потребление': self.expected_consumption,
            'Ожидаемое потребление за время поставки': self.expected_consumption_during_delivery,
            'Максимальное потребление за время поставки': self.max_expected_consumption,
            'Страховой запас': self.safety_stock,
            'Пороговый уровень': self.threshold_level,
            'Максимальный запас': self.max_stock,
            'Срок расходования запасов до порогового уровня': self.expiration_time_to_threshold_level,
        }
        base_info = self.base_info()
        base_info.update(specific_info)
        return base_info


@dataclass
class ModelFIV(BaseModel):
    t_mz: float
    optimal_interval_between_orders: float  # оптимальный интервал времени между заказами
    expected_consumption: float  # ожидаемое потребление
    expected_consumption_during_delivery: float  # ожидаемое потребление за время поставки
    safety_stock: float  # страховой запас
    max_stock: float  # максимальный запас

    def full_info(self) -> dict:
        specific_info = {
            'tMZ': self.t_mz,
            'Оптимальный интервал времени между заказами': self.optimal_interval_between_orders,
            'Ожидаемое потребление': self.expected_consumption,
            'Ожидаемое потребление за время поставки': self.expected_consumption_during_delivery,
            'Страховой запас': self.safety_stock,
            'Максимальный запас': self.max_stock,
        }
        specific_info.update(self.base_info())
        return specific_info


@dataclass
class ModelMinMax(BaseModel):
    t_mz: float
    optimal_interval_between_orders: float  # оптимальный интервал времени между заказами
    expected_consumption: float  # ожидаемое потребление
    expected_consumption_during_delivery: float  # ожидаемое потребление за время поставки
    max_expected_consumption: float  # максимальное потребление за время поставки
    safety_stock: float  # страховой запас
    min_stock: float  # минимальный запас
    max_stock: float  # максимальный запас

    def full_info(self) -> dict:
        specific_info = {
            'tMZ': self.t_mz,
            'Оптимальный интервал времени между заказами': self.optimal_interval_between_orders,
            'Ожидаемое потребление': self.expected_consumption,
            'Ожидаемое потребление за время поставки': self.expected_consumption_during_delivery,
            'Максимальное потребление за время поставки': self.max_expected_consumption,
            'Страховой запас': self.safety_stock,
            'Минимальный запас': self.min_stock,
            'Максимальный запас': self.max_stock,
        }
        specific_info.update(self.base_info())
        return specific_info


@dataclass
class ModelFixedPeriod(BaseModel):
    t_mz: float
    optimal_interval_between_orders: float  # оптимальный интервал времени между заказами
    expected_consumption: float  # ожидаемое потребление
    expected_consumption_during_delivery: float  # ожидаемое потребление за время поставки
    max_expected_consumption: float  # Максимальное потребление за время поставки
    safety_stock: float  # страховой запас
    threshold_level: float  # пороговый уровень
    max_stock: float  # максимальный запас

    def full_info(self) -> dict:
        specific_info = {
            'tMZ': self.t_mz,
            'Оптимальный интервал времени между заказами': self.optimal_interval_between_orders,
            'Ожидаемое потребление': self.expected_consumption,
            'Ожидаемое потребление за время поставки': self.expected_consumption_during_delivery,
            'Максимальное потребление за время поставки': self.max_expected_consumption,
            'Страховой запас': self.safety_stock,
            'Пороговый уровень': self.threshold_level,
            'Максимальный запас': self.max_stock,
        }
        specific_info.update(self.base_info())
        return specific_info
