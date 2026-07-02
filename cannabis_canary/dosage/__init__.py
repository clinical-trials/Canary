"""Cannabis Canary© dosage calculator — pure mg/day math (no PHI)."""
from cannabis_canary.dosage.calculator import (
    InvalidDoseInput,
    compute_dose,
    mg_per_day_from_concentration,
    mg_per_day_from_label,
)
from cannabis_canary.dosage.models import (
    CalcMode,
    Cannabinoid,
    DoseInput,
    DoseResult,
)

__all__ = [
    "InvalidDoseInput",
    "compute_dose",
    "mg_per_day_from_concentration",
    "mg_per_day_from_label",
    "CalcMode",
    "Cannabinoid",
    "DoseInput",
    "DoseResult",
]
