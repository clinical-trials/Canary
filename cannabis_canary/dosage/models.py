"""Typed inputs/outputs for the dosage calculator. No PHI."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Cannabinoid(str, Enum):
    THC = "THC"
    CBD = "CBD"


class CalcMode(str, Enum):
    CONCENTRATION = "concentration"  # grams/day + potency %
    LABEL = "label"                  # mg per unit + units/day


@dataclass(frozen=True)
class DoseInput:
    cannabinoid: Cannabinoid
    mode: CalcMode
    grams_per_day: float | None = None
    percent: float | None = None
    mg_per_unit: float | None = None
    units_per_day: float | None = None


@dataclass(frozen=True)
class DoseResult:
    cannabinoid: Cannabinoid
    mg_per_day: float
    mode: CalcMode
