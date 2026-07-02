"""Pure THC/CBD daily-dose math for Cannabis Canary©.

No I/O, no network, no PHI. Everything here is deterministic so the clinically
critical dose math can be validated in isolation. mg/day is the single common
output metric across all product types; the dose is independent of method of
ingestion (method is not a factor in the math).
"""
from __future__ import annotations


class InvalidDoseInput(ValueError):
    """Raised when dose inputs are missing or out of range."""


def mg_per_day_from_concentration(grams_per_day: float, percent: float) -> float:
    """mg cannabinoid/day from a weight + potency percentage.

    Formula: grams_per_day × 1000 mg/g × (percent ÷ 100).
    Example: 1.0 g at 10% THC -> 100.0 mg/day.
    """
    if grams_per_day < 0:
        raise InvalidDoseInput("grams_per_day must be >= 0")
    if not 0 <= percent <= 100:
        raise InvalidDoseInput("percent must be between 0 and 100")
    return grams_per_day * 1000 * (percent / 100)


def mg_per_day_from_label(mg_per_unit: float, units_per_day: float) -> float:
    """mg cannabinoid/day from a labeled product.

    Formula: mg_per_unit × units_per_day.
    Example: two 10 mg gummies -> 20.0 mg/day.
    """
    if mg_per_unit < 0:
        raise InvalidDoseInput("mg_per_unit must be >= 0")
    if units_per_day < 0:
        raise InvalidDoseInput("units_per_day must be >= 0")
    return mg_per_unit * units_per_day
