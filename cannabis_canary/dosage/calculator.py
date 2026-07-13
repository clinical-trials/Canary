"""Pure THC/CBD daily-dose math for Cannabis Canary©.

No I/O, no network, no PHI. Everything here is deterministic so the clinically
critical dose math can be validated in isolation. mg/day is the single common
output metric across all product types; the dose is independent of method of
ingestion (method is not a factor in the math).
"""
from __future__ import annotations

from cannabis_canary.dosage.models import CalcMode, DoseInput, DoseResult


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


def compute_dose(dose_input: DoseInput) -> DoseResult:
    """Validate required fields, dispatch on mode, and return a DoseResult.

    Concentration mode requires grams_per_day + percent.
    Label mode requires mg_per_unit + units_per_day.
    Range validation is delegated to the underlying formula functions, which
    raise InvalidDoseInput on out-of-range values.
    """
    if dose_input.mode is CalcMode.CONCENTRATION:
        if dose_input.grams_per_day is None or dose_input.percent is None:
            raise InvalidDoseInput(
                "concentration mode requires grams_per_day and percent"
            )
        mg = mg_per_day_from_concentration(
            dose_input.grams_per_day, dose_input.percent
        )
    elif dose_input.mode is CalcMode.LABEL:
        if dose_input.mg_per_unit is None or dose_input.units_per_day is None:
            raise InvalidDoseInput(
                "label mode requires mg_per_unit and units_per_day"
            )
        mg = mg_per_day_from_label(
            dose_input.mg_per_unit, dose_input.units_per_day
        )
    else:  # pragma: no cover - enum is exhaustive
        raise InvalidDoseInput(f"unknown mode: {dose_input.mode}")
    return DoseResult(
        cannabinoid=dose_input.cannabinoid, mg_per_day=mg, mode=dose_input.mode
    )


def total_mg_per_day(dose_inputs: list[DoseInput]) -> float:
    """Additive total across multiple products.

    A patient may use several product types at once (e.g. a tincture and an
    edible); their mg/day contributions sum to a single daily total. An empty
    list totals 0.0.
    """
    return sum(compute_dose(d).mg_per_day for d in dose_inputs)
