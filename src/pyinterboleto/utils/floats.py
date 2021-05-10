from decimal import Decimal, getcontext

getcontext().prec = 2  # two decimal places


def is_non_zero_positive_float(value: float) -> bool:
    return Decimal(value) > Decimal(0)


def is_positive_float(value: float) -> bool:
    return Decimal(value) >= Decimal(0)


def is_zero_float(value: float) -> bool:
    return Decimal(value) == Decimal(0)
