from decimal import Decimal, ROUND_HALF_UP


def round_decimal(value, places=2):
    return Decimal(value).quantize(Decimal(f'1.{"0"*places}'), rounding=ROUND_HALF_UP)