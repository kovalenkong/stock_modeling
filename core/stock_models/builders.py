from typing import Optional

import numpy as np

from .config import Config
from .models import ModelFIV, ModelFixedPeriod, ModelFRZ, ModelMinMax


def build_frz(config: Config) -> ModelFRZ:
    # ожидаемое потребление
    expected_consumption = config.consumption.sum() / config.period
    # срок расходования поставки
    delivery_expiration_time = config.q / expected_consumption
    # ожидаемое потребление за время поставки
    expected_consumption_during_delivery = config.delivery_time * expected_consumption
    # максимальное потребление за время поставки
    max_expected_consumption = (
                                       config.delivery_time + config.delay_time
                               ) * expected_consumption
    # страховой запас
    safety_stock = config.delay_time * expected_consumption
    # пороговый уровень
    threshold_level = expected_consumption_during_delivery + safety_stock
    # максимальный запас
    max_stock = safety_stock + config.q
    # Срок расходования запасов до порогового уровня
    expiration_time_to_threshold_level = (max_stock - threshold_level) / expected_consumption

    period = config.period
    outcome_order = np.zeros(period, dtype=float)  # заказ (ед)
    income_order = np.zeros(period, dtype=float)  # приход (ед)
    balance = np.zeros(period, dtype=float)  # остаток
    number_of_outcome_orders = 0  # количество невыполненных заявок
    delivery_number = 0

    consumption = config.consumption

    for i, el in enumerate(consumption):
        # обновляем остаток на начало дня
        if i == 0:
            balance[0] = config.initial_stock
        else:
            balance[i] = balance[i - 1] - consumption[i - 1] + income_order[i]
            if income_order[i] > 0:
                number_of_outcome_orders -= 1

        # если остаток меньше порогового и не делали заявку
        if balance[i] <= threshold_level and number_of_outcome_orders == 0:
            # заказываем
            outcome_order[i] = config.q
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
                    income_order[int(come_after)] = config.q
            elif isinstance(config.delay, (list, tuple, set)):
                if delivery_number in config.delay:
                    come_after = i + config.delivery_time + config.delay_time
                else:
                    come_after = i + config.delivery_time
                # если не "выходим за порог"
                if come_after < period:
                    income_order[int(come_after)] = config.q
    return ModelFRZ(
        config, consumption, balance, income_order, outcome_order,
        expected_consumption=expected_consumption,
        delivery_expiration_time=delivery_expiration_time,
        expected_consumption_during_delivery=expected_consumption_during_delivery,
        max_expected_consumption=max_expected_consumption,
        safety_stock=safety_stock,
        threshold_level=threshold_level,
        max_stock=max_stock,
        expiration_time_to_threshold_level=expiration_time_to_threshold_level
    )


def build_fiv(config: Config) -> ModelFIV:
    period = config.period
    # tМЗ*
    t_mz = (period * config.q) / config.consumption.sum()
    # оптимальный интервал времени между заказами TODO КАКАЯ ФОРМУЛА???
    optimal_interval_between_orders = int(t_mz + config.delay_time)  # изначальная
    # optimal_interval_between_orders = int(config.consumption.sum() / config.q)
    # optimal_interval_between_orders = int(t_mz)
    # ожидаемое потребление
    expected_consumption = config.consumption.sum() / len(config.consumption)
    # ожидаемое потребление за время поставки
    expected_consumption_during_delivery = config.delivery_time * expected_consumption
    # максимальное потребление за время поставки
    max_expected_consumption = (
                                       config.delivery_time + config.delay_time
                               ) * expected_consumption
    # страховой запас
    safety_stock = config.delay_time * expected_consumption
    # максимальный запас
    max_stock = safety_stock + optimal_interval_between_orders * expected_consumption

    outcome_order = np.zeros(period, dtype=float)  # заказ (ед)
    income_order = np.zeros(period, dtype=float)  # приход (ед)
    balance = np.zeros(period, dtype=float)  # остаток
    delivery_number = 0
    offset = None

    consumption = config.consumption

    for i, el in enumerate(consumption):
        # обновляем остаток на начало дня
        if i == 0:
            balance[0] = config.initial_stock
        else:
            balance[i] = balance[i - 1] - consumption[i - 1] + income_order[i]

        if offset is None and balance[i] < max_expected_consumption:
            offset = i % optimal_interval_between_orders  # todo: уточнить
        elif offset is not None and (i - offset) % optimal_interval_between_orders == 0:
            pass
        else:
            continue
        # если пора делать заказ
        # определяем размер заказа
        q = max_stock - balance[
            i] + expected_consumption_during_delivery  # todo: утонить - точно ли это, а не max_expected_consumption
        if q <= 0:
            continue
        # размещаем заказ
        outcome_order[i] = q
        delivery_number += 1

        # заказ приедет через
        if isinstance(config.delay, (float, int)):
            if np.random.rand() < config.delay:
                come_after = i + config.delivery_time + config.delay_time
            else:
                come_after = i + config.delivery_time
            # если не "выходим за порог"
            if come_after < period:
                income_order[int(come_after)] = q
        elif isinstance(config.delay, (list, tuple, set)):
            if delivery_number in config.delay:
                come_after = i + config.delivery_time + config.delay_time
            else:
                come_after = i + config.delivery_time
            # если не "выходим за порог"
            if come_after < period:
                income_order[int(come_after)] = q

    return ModelFIV(
        config, consumption, balance, income_order, outcome_order,
        t_mz=t_mz,
        optimal_interval_between_orders=optimal_interval_between_orders,
        expected_consumption=expected_consumption,
        expected_consumption_during_delivery=expected_consumption_during_delivery,
        safety_stock=safety_stock,
        max_stock=max_stock
    )


def build_minimum_maximum(config: Config) -> ModelMinMax:
    period = config.period
    # tМЗ*
    t_mz = (period * config.q) / config.consumption.sum()
    # оптимальный интервал времени между заказами
    optimal_interval_between_orders = int(t_mz + config.delay_time)
    # ожидаемое потребление
    expected_consumption = config.consumption.sum() / len(config.consumption)
    # ожидаемое потребление за время поставки
    expected_consumption_during_delivery = config.delivery_time * expected_consumption
    # максимальное потребление за время поставки
    max_expected_consumption = (
                                       config.delivery_time + config.delay_time
                               ) * expected_consumption
    # страховой запас
    safety_stock = config.delay_time * expected_consumption
    # минимальный запас
    min_stock = safety_stock + expected_consumption_during_delivery
    # максимальный запас
    max_stock = min_stock + t_mz * expected_consumption

    outcome_order = np.zeros(period, dtype=float)  # заказ (ед)
    income_order = np.zeros(period, dtype=float)  # приход (ед)
    balance = np.zeros(period, dtype=float)  # остаток
    delivery_number = 0
    offset: Optional[int] = None

    consumption = config.consumption

    for i, el in enumerate(consumption):
        # обновляем остаток на начало дня
        if i == 0:
            balance[0] = config.initial_stock
        else:
            balance[i] = balance[i - 1] - consumption[i - 1] + income_order[i]

        # если смещение неизвестно и баланс меньше минимального запаса
        if offset is None and balance[i] < min_stock:
            offset = i % optimal_interval_between_orders  # todo: уточнить
        elif offset is not None and (i - offset) % optimal_interval_between_orders == 0:
            pass
        else:
            continue
        # определяем размер заказа
        q = (
                max_stock - balance[i]
                + expected_consumption_during_delivery
        )  # todo: максимальное ожидаемое потребление
        if q <= 0:
            continue
        # размещаем заказ
        outcome_order[i] = q
        delivery_number += 1

        # заказ приедет через
        if isinstance(config.delay, (float, int)):
            if np.random.rand() < config.delay:
                come_after = i + config.delivery_time + config.delay_time
            else:
                come_after = i + config.delivery_time
            # если не "выходим за порог"
            if come_after < period:
                income_order[int(come_after)] = q
        elif isinstance(config.delay, (list, tuple, set)):
            if delivery_number in config.delay:
                come_after = i + config.delivery_time + config.delay_time
            else:
                come_after = i + config.delivery_time
            # если не "выходим за порог"
            if come_after < period:
                income_order[int(come_after)] = q

    return ModelMinMax(
        config, consumption, balance, income_order, outcome_order,
        t_mz=t_mz,
        optimal_interval_between_orders=optimal_interval_between_orders,
        expected_consumption=expected_consumption,
        expected_consumption_during_delivery=expected_consumption_during_delivery,
        max_expected_consumption=max_expected_consumption,
        safety_stock=safety_stock,
        min_stock=min_stock,
        max_stock=max_stock
    )


def build_fixed_period(config: Config) -> ModelFixedPeriod:
    period = config.period
    # tМЗ*
    t_mz = (period * config.q) / config.consumption.sum()
    # оптимальный интервал времени между заказами
    optimal_interval_between_orders = int(t_mz + config.delay_time)
    # ожидаемое потребление
    expected_consumption = config.consumption.sum() / period
    # ожидаемое потребление за время поставки
    expected_consumption_during_delivery = config.delivery_time * expected_consumption
    # максимальное потребление за время поставки
    max_expected_consumption = (
                                       config.delivery_time + config.delay_time
                               ) * expected_consumption
    # страховой запас
    safety_stock = config.delay_time * expected_consumption
    # пороговый уровень
    threshold_level = expected_consumption_during_delivery + safety_stock
    # максимальный запас
    max_stock = safety_stock + optimal_interval_between_orders * expected_consumption

    outcome_order = np.zeros(period, dtype=float)  # заказ (ед)
    income_order = np.zeros(period, dtype=float)  # приход (ед)
    balance = np.zeros(period, dtype=float)  # остаток
    delivery_number = 0
    offset: Optional[int] = None

    # флаги
    last_q: float = 0  # последний заказ
    frz_done = True
    frz_orders = np.zeros(period, dtype=int)

    consumption = config.consumption

    for i, el in enumerate(consumption):
        # обновляем остаток на начало дня
        if i == 0:
            balance[0] = config.initial_stock
        else:
            balance[i] = balance[i - 1] - consumption[i - 1] + income_order[i]
            if income_order[i] > 0 and frz_orders[i]:
                frz_done = True

        if offset is None and balance[i] < max_expected_consumption and frz_done:
            offset = i % optimal_interval_between_orders  # todo: уточнить
            q = max_stock - balance[i] + expected_consumption_during_delivery
            last_type = 'frz'
        elif offset is not None and (i - offset) % optimal_interval_between_orders == 0:
            if balance[i] < threshold_level:
                q = max_stock - balance[i] + expected_consumption_during_delivery - last_q
            else:
                q = max_stock - balance[i] + expected_consumption_during_delivery
            if q <= 0:
                continue
            last_type = 'fiv'
        elif offset is not None and balance[i] < max_expected_consumption and frz_done:
            q = max_stock - threshold_level + expected_consumption_during_delivery
            last_type = 'frz'
        else:
            continue

        if q <= 0:
            continue
        last_q = q
        if last_type == 'frz':
            frz_done = False
        # размещаем заказ
        outcome_order[i] = q
        delivery_number += 1

        # заказ приедет через
        if isinstance(config.delay, (float, int)):
            if np.random.rand() < config.delay:
                come_after = i + config.delivery_time + config.delay_time
            else:
                come_after = i + config.delivery_time
            # если не "выходим за порог"
            if come_after < period:
                income_order[int(come_after)] = q
                if last_type == 'frz':
                    frz_orders[int(come_after)] = 1
        elif isinstance(config.delay, (list, tuple, set)):
            if delivery_number in config.delay:
                come_after = i + config.delivery_time + config.delay_time
            else:
                come_after = i + config.delivery_time
            # если не "выходим за порог"
            if come_after < period:
                income_order[int(come_after)] = q
                if last_type == 'frz':
                    frz_orders[int(come_after)] = 1
    return ModelFixedPeriod(
        config, consumption, balance, income_order, outcome_order,
        t_mz=t_mz,
        optimal_interval_between_orders=optimal_interval_between_orders,
        expected_consumption=expected_consumption,
        expected_consumption_during_delivery=expected_consumption_during_delivery,
        max_expected_consumption=max_expected_consumption,
        safety_stock=safety_stock,
        threshold_level=threshold_level,
        max_stock=max_stock
    )

