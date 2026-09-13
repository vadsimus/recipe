"""
Unit conversion utilities for ingredients.
All conversions are done to/from base units:
- Weight: kg (kilograms)
- Volume: L (liters)
- Pieces: pcs (pieces)
"""
from decimal import Decimal
from typing import Optional, Tuple


# Conversion factors to base units (kg for weight, L for volume)
CONVERSION_FACTORS = {
    # Weight units to kg
    'kg': Decimal('1'),
    'g': Decimal('0.001'),
    '100g': Decimal('0.1'),
    '500g': Decimal('0.5'),
    '1kg': Decimal('1'),
    # Volume units to L
    'l': Decimal('1'),
    'ml': Decimal('0.001'),
    '100ml': Decimal('0.1'),
    '500ml': Decimal('0.5'),
    '1l': Decimal('1'),
    # Piece units (no conversion needed)
    'pcs': Decimal('1'),
    '1pcs': Decimal('1'),
    '10pcs': Decimal('10'),
}


def get_base_unit(unit: str) -> str:
    """Get the base unit for a given unit type."""
    if unit in ['g', 'kg', '100g', '500g', '1kg']:
        return 'kg'
    elif unit in ['l', 'ml', '100ml', '500ml', '1l']:
        return 'L'
    elif unit in ['pcs', '1pcs', '10pcs']:
        return 'pcs'
    else:
        raise ValueError(f"Unknown unit: {unit}")


def convert_to_base_unit(amount: Decimal, from_unit: str) -> Decimal:
    """
    Convert an amount from a given unit to the base unit.

    Args:
        amount: The amount to convert
        from_unit: The unit to convert from (e.g., 'g', 'ml', '100g', '1l')

    Returns:
        The amount in base units (kg for weight, L for volume, pcs for pieces)
    """
    if from_unit not in CONVERSION_FACTORS:
        raise ValueError(f"Unknown unit: {from_unit}")

    return amount * CONVERSION_FACTORS[from_unit]


def convert_from_base_unit(amount: Decimal, to_unit: str) -> Decimal:
    """
    Convert an amount from base unit to a given unit.
    
    Args:
        amount: The amount in base units
        to_unit: The unit to convert to (e.g., 'g', 'ml', 'kg', 'L')
    
    Returns:
        The amount in the target unit
    """
    if to_unit not in CONVERSION_FACTORS:
        raise ValueError(f"Unknown unit: {to_unit}")
    
    factor = CONVERSION_FACTORS[to_unit]
    if factor == 0:
        return Decimal('0')
    return amount / factor


def get_value_per_base_unit(value: Decimal, value_unit: str) -> Decimal:
    """
    Calculate a per-base-unit value (kg, L, or pcs) for a value given for a
    reference unit (e.g., cost given per '100g', or calories given per '1l').

    Args:
        value: The value for the value_unit (e.g., a cost or a calorie count)
        value_unit: The unit the value is specified for (e.g., '1kg', '100g', '1l', '100ml')

    Returns:
        The value per base unit
    """
    # Convert "1 value_unit" to base unit (e.g., '100g' -> 0.1 kg)
    base_amount = convert_to_base_unit(Decimal('1'), value_unit)

    if base_amount == 0:
        return Decimal('0')

    return value / base_amount


def calculate_ingredient_price(
    cost: Decimal,
    cost_unit: str,
    amount: Decimal,
    amount_unit: str
) -> Decimal:
    """
    Calculate the price for an ingredient based on cost, cost unit, amount, and amount unit.
    
    Args:
        cost: The cost for the cost_unit
        cost_unit: The unit the cost is specified for (e.g., '1kg', '100g')
        amount: The amount needed
        amount_unit: The unit of the amount (e.g., 'g', 'kg', 'ml', 'L')
    
    Returns:
        The calculated price
    """
    # Get cost per base unit
    cost_per_base = get_value_per_base_unit(cost, cost_unit)

    # Convert amount to base unit
    amount_in_base = convert_to_base_unit(amount, amount_unit)

    # Calculate price
    return cost_per_base * amount_in_base


def parse_cost_unit(cost_unit: str) -> Tuple[Decimal, str]:
    """
    Parse a cost_unit string to extract amount and unit.
    
    Examples:
        '1kg' -> (1, 'kg')
        '100g' -> (100, 'g')
        '1l' -> (1, 'l')
        '100ml' -> (100, 'ml')
    
    Returns:
        Tuple of (amount, unit)
    """
    # Remove common prefixes and extract
    if cost_unit.endswith('kg'):
        return (Decimal('1'), 'kg') if cost_unit == '1kg' else (Decimal(cost_unit.replace('kg', '')), 'kg')
    elif cost_unit.endswith('g'):
        numeric = cost_unit.replace('g', '')
        return (Decimal(numeric), 'g')
    elif cost_unit.endswith('l'):
        return (Decimal('1'), 'l') if cost_unit == '1l' else (Decimal(cost_unit.replace('l', '')), 'l')
    elif cost_unit.endswith('ml'):
        numeric = cost_unit.replace('ml', '')
        return (Decimal(numeric), 'ml')
    elif cost_unit.endswith('pcs'):
        numeric = cost_unit.replace('pcs', '')
        return (Decimal(numeric) if numeric else Decimal('1'), 'pcs')
    else:
        raise ValueError(f"Cannot parse cost_unit: {cost_unit}")

