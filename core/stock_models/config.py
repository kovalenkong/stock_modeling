import enum
from typing import Any, List, Union

import numpy as np

from .errors import ConfigError


class MODEL_TYPE(enum.Enum):
    FRZ = 'frz'
    FIV = 'fiv'
    MIN_MAX = 'min_max'  # модель "минимум-максимум"
    FIXED_PERIOD = 'fixed_period'


class MODIFICATION(enum.Enum):
    CLASSIC = 'classic'  # классическая
    LOST_SALES = 'lost_sales'  # упущенные продажи
    GRADUAL_REPLENISHMENT = 'gradual_replenishment'  # постепенное пополнение


class Config:
    def __init__(
            self, consumption: np.ndarray, order_costs: float, storage_costs: float,
            delivery_time: int, delay_time: int, initial_stock: float, modification: MODIFICATION,
            delay: Union[float, int, List[int]], **kwargs
    ):
        """

        :param consumption: ожидаемое потребление
        :param order_costs: затраты на пополнение заказа (A)
        :param storage_costs: затраты на хранение ед. заказа (I)
        :param delivery_time: время пополнения заказа
        :param delay_time: возможная задержка
        :param initial_stock: начальный уровень запаса
        :param modification: метод вычисления значения оптимального заказа
        :param delay: возможная задержка
            если задержка указана как число (от 0 до 1), то будет применен метод
            случайной задержки: например delay_probability=0.7 означает, что задержка наступит с вероятностью 70%
            если задержка указана как список чисел, то каждое число будет означать номер прихода товара,
            притом каждый приход, который числится в списке delay, будет привезен с задержкой
        :param kwargs:
            :param deficit_losses: потеря от дефицита единицы товара
            :param s: среднесуточное потребление
            :param d: среднесуточное поступление
        """
        if consumption.ndim != 1:
            raise ConfigError('dimension of consumption array should be 1')
        if not np.all(consumption >= 0):
            raise ConfigError('all consumptions values should be >= 0')
        self.consumption = consumption
        if order_costs < 0:
            raise ConfigError('order costs should be >= 0')
        self.order_costs = order_costs  # A
        if storage_costs <= 0:
            raise ConfigError('storage costs should be > 0')
        self.storage_costs = storage_costs  # I
        self.need = self.consumption.sum()  # S
        self.initial_stock = initial_stock  # начальный запас
        if delivery_time < 1:
            raise ConfigError('delivery time should be at least 1')
        self.delivery_time = delivery_time
        if delay_time < 0:
            raise ConfigError('delay time should be >= 0')
        self.delay_time = delay_time
        self.modification = modification
        if isinstance(delay, (float, int)) and not (0 <= delay <= 1):
            raise ConfigError('if delay is int/float, then 0 <= value <= 1')
        self.delay = delay
        self._kwargs = kwargs
        self.q = self._calculate_q(self.modification, **self._kwargs)

    def default_kwarg(self, name: str, default: Any = None) -> Any:
        return self._kwargs.get(name, default)

    @property
    def period(self):
        return len(self.consumption)

    # @property
    # def q(self):
    #     return self._calculate_q(self.modification, **self._kwargs)

    def _calculate_q(self, modification: MODIFICATION, **kwargs):
        if modification == MODIFICATION.CLASSIC.value:
            return np.ceil(np.sqrt((2 * self.order_costs * self.need) / self.storage_costs))
        elif modification == MODIFICATION.LOST_SALES.value:
            deficit_losses = kwargs.get('deficit_losses')
            if deficit_losses is None or deficit_losses <= 0:
                raise ConfigError('deficit_losses should be number > 0')
            return np.ceil(
                np.sqrt(
                    ((2 * self.order_costs * self.need) / self.storage_costs)
                    * ((deficit_losses + self.storage_costs) / deficit_losses)
                )
            )
        elif modification == MODIFICATION.GRADUAL_REPLENISHMENT.value:
            s = kwargs.get('s')
            d = kwargs.get('d')
            # todo
            val = (
                    (2 * self.order_costs * self.need)
                    / (self.storage_costs * (1 - s / d))
            )
            if val < 0:
                raise ConfigError('wrong values for "s" and "d" parameters')
            return np.ceil(np.sqrt(val))

        raise ConfigError(f'unexpected modification type: {modification}')
