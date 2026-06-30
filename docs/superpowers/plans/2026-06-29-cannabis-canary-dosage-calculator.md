# Cannabis Canary© — Dosage Calculator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the pure-Python THC/CBD daily-dose calculator — the crown-jewel feature that converts a patient's cannabis product data into a single common **mg/day** metric.

**Architecture:** A standalone, dependency-free Python package (`cannabis_canary.dosage`). All functions are pure (no I/O, no network, **no PHI**), so the clinically critical math is validated in complete isolation before any EHR, registry, or UI layer depends on it. This is the de-identified "engine" side of the PHI boundary.

**Tech Stack:** Python ≥ 3.11, `pytest`. No runtime dependencies.

**Plan scope:** This is plan **1 of 8** for Cannabis Canary© v1 (see `docs/superpowers/specs/2026-06-29-cannabis-canary-v1-design.md`). It delivers *only* the dosage calculator. Provider-facing help-notes *copy* and product-type→mode UI defaults are deliberately deferred to the later form/UI plan; this module exposes the math those layers will call.

## Global Constraints

- **Dose formula (verbatim from spec §7, user-confirmed 2026-06-29):**
  - Concentration products: `mg/day = grams_per_day × 1000 × (percent ÷ 100)` → 1.0 g @ 10% = **100.0 mg/day**
  - Labeled products: `mg/day = mg_per_unit × units_per_day`
  - Output is **independent of method of ingestion** — method is NOT a factor in the math.
- **Purity:** no I/O, no network, no logging of inputs, no global state. Pure functions only.
- **Python ≥ 3.11**; standard library + `pytest` only.
- **Validation is explicit:** invalid inputs raise `InvalidDoseInput` (never return a wrong number silently).

---

### Task 1: Project scaffolding + pure dose formulas

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `cannabis_canary/__init__.py`
- Create: `cannabis_canary/dosage/__init__.py`
- Create: `cannabis_canary/dosage/calculator.py`
- Test: `tests/__init__.py`, `tests/dosage/__init__.py`, `tests/dosage/test_calculator.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces:
  - `mg_per_day_from_concentration(grams_per_day: float, percent: float) -> float`
  - `mg_per_day_from_label(mg_per_unit: float, units_per_day: float) -> float`
  - `InvalidDoseInput(ValueError)`

- [ ] **Step 1: Create project scaffolding**

Create `pyproject.toml`:

```toml
[project]
name = "cannabis-canary"
version = "0.1.0"
description = "Cannabis Canary© — prospective cannabis social-history registry & point-of-care decision support for Epic/Cerner (SMART on FHIR + CDS Hooks)."
requires-python = ">=3.11"

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["cannabis_canary*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
```

Create empty files: `cannabis_canary/__init__.py`, `cannabis_canary/dosage/__init__.py`, `tests/__init__.py`, `tests/dosage/__init__.py`.

Then create the venv and install (run from repo root `~/evidence-synthesis-ehr`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

- [ ] **Step 2: Write the failing test**

Create `tests/dosage/test_calculator.py`:

```python
import pytest

from cannabis_canary.dosage.calculator import (
    InvalidDoseInput,
    mg_per_day_from_concentration,
    mg_per_day_from_label,
)


def test_concentration_one_gram_ten_percent_is_100mg():
    assert mg_per_day_from_concentration(1.0, 10.0) == 100.0


def test_concentration_zero_percent_is_zero():
    assert mg_per_day_from_concentration(2.0, 0.0) == 0.0


def test_concentration_high_potency_concentrate():
    # 0.2 g of 80% THC wax -> 160 mg
    assert mg_per_day_from_concentration(0.2, 80.0) == 160.0


def test_concentration_rejects_negative_grams():
    with pytest.raises(InvalidDoseInput):
        mg_per_day_from_concentration(-1.0, 10.0)


def test_concentration_rejects_percent_over_100():
    with pytest.raises(InvalidDoseInput):
        mg_per_day_from_concentration(1.0, 150.0)


def test_concentration_rejects_negative_percent():
    with pytest.raises(InvalidDoseInput):
        mg_per_day_from_concentration(1.0, -5.0)


def test_label_two_ten_mg_gummies_is_20mg():
    assert mg_per_day_from_label(10.0, 2.0) == 20.0


def test_label_zero_units_is_zero():
    assert mg_per_day_from_label(10.0, 0.0) == 0.0


def test_label_rejects_negative_mg_per_unit():
    with pytest.raises(InvalidDoseInput):
        mg_per_day_from_label(-10.0, 2.0)


def test_label_rejects_negative_units():
    with pytest.raises(InvalidDoseInput):
        mg_per_day_from_label(10.0, -2.0)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/dosage/test_calculator.py -v`
Expected: FAIL — `ModuleNotFoundError` / `ImportError` (calculator module not yet created).

- [ ] **Step 4: Write the minimal implementation**

Create `cannabis_canary/dosage/calculator.py`:

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/dosage/test_calculator.py -v`
Expected: PASS (10 passed).

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .gitignore cannabis_canary/ tests/
git commit -m "feat(dosage): pure mg/day formulas (concentration + label) with validation

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Typed dose model + compute_dose dispatcher + public API

**Files:**
- Create: `cannabis_canary/dosage/models.py`
- Modify: `cannabis_canary/dosage/calculator.py` (add `compute_dose`)
- Modify: `cannabis_canary/dosage/__init__.py` (public exports)
- Test: `tests/dosage/test_models.py`, `tests/dosage/test_compute_dose.py`

**Interfaces:**
- Consumes: `mg_per_day_from_concentration`, `mg_per_day_from_label`, `InvalidDoseInput` (Task 1).
- Produces:
  - `Cannabinoid` enum (`THC`, `CBD`)
  - `CalcMode` enum (`CONCENTRATION`, `LABEL`)
  - `DoseInput` frozen dataclass: `cannabinoid: Cannabinoid`, `mode: CalcMode`, `grams_per_day: float | None = None`, `percent: float | None = None`, `mg_per_unit: float | None = None`, `units_per_day: float | None = None`
  - `DoseResult` frozen dataclass: `cannabinoid: Cannabinoid`, `mg_per_day: float`, `mode: CalcMode`
  - `compute_dose(dose_input: DoseInput) -> DoseResult`
  - Package exports of all of the above + Task 1 functions from `cannabis_canary.dosage`.

- [ ] **Step 1: Write the failing model test**

Create `tests/dosage/test_models.py`:

```python
from cannabis_canary.dosage.models import (
    CalcMode,
    Cannabinoid,
    DoseInput,
    DoseResult,
)


def test_dose_input_defaults_are_none():
    di = DoseInput(cannabinoid=Cannabinoid.THC, mode=CalcMode.CONCENTRATION)
    assert di.grams_per_day is None
    assert di.percent is None
    assert di.mg_per_unit is None
    assert di.units_per_day is None


def test_dose_input_is_frozen():
    di = DoseInput(cannabinoid=Cannabinoid.THC, mode=CalcMode.CONCENTRATION)
    try:
        di.percent = 10.0  # type: ignore[misc]
    except Exception as exc:
        assert exc.__class__.__name__ == "FrozenInstanceError"
    else:
        raise AssertionError("DoseInput should be frozen")


def test_dose_result_holds_values():
    dr = DoseResult(cannabinoid=Cannabinoid.CBD, mg_per_day=42.0, mode=CalcMode.LABEL)
    assert dr.cannabinoid is Cannabinoid.CBD
    assert dr.mg_per_day == 42.0
    assert dr.mode is CalcMode.LABEL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/dosage/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: cannabis_canary.dosage.models`.

- [ ] **Step 3: Write the models**

Create `cannabis_canary/dosage/models.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/dosage/test_models.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Write the failing compute_dose test**

Create `tests/dosage/test_compute_dose.py`:

```python
import pytest

from cannabis_canary.dosage.calculator import InvalidDoseInput, compute_dose
from cannabis_canary.dosage.models import (
    CalcMode,
    Cannabinoid,
    DoseInput,
    DoseResult,
)


def test_compute_dose_concentration_returns_result():
    di = DoseInput(
        cannabinoid=Cannabinoid.THC,
        mode=CalcMode.CONCENTRATION,
        grams_per_day=1.0,
        percent=10.0,
    )
    result = compute_dose(di)
    assert result == DoseResult(
        cannabinoid=Cannabinoid.THC, mg_per_day=100.0, mode=CalcMode.CONCENTRATION
    )


def test_compute_dose_label_returns_result():
    di = DoseInput(
        cannabinoid=Cannabinoid.THC,
        mode=CalcMode.LABEL,
        mg_per_unit=10.0,
        units_per_day=2.0,
    )
    result = compute_dose(di)
    assert result.mg_per_day == 20.0
    assert result.mode is CalcMode.LABEL


def test_compute_dose_supports_cbd():
    di = DoseInput(
        cannabinoid=Cannabinoid.CBD,
        mode=CalcMode.CONCENTRATION,
        grams_per_day=2.0,
        percent=5.0,
    )
    result = compute_dose(di)
    assert result.cannabinoid is Cannabinoid.CBD
    assert result.mg_per_day == 100.0


def test_compute_dose_concentration_missing_percent_raises():
    di = DoseInput(
        cannabinoid=Cannabinoid.THC,
        mode=CalcMode.CONCENTRATION,
        grams_per_day=1.0,
    )
    with pytest.raises(InvalidDoseInput):
        compute_dose(di)


def test_compute_dose_label_missing_units_raises():
    di = DoseInput(
        cannabinoid=Cannabinoid.THC,
        mode=CalcMode.LABEL,
        mg_per_unit=10.0,
    )
    with pytest.raises(InvalidDoseInput):
        compute_dose(di)


def test_compute_dose_propagates_range_validation():
    di = DoseInput(
        cannabinoid=Cannabinoid.THC,
        mode=CalcMode.CONCENTRATION,
        grams_per_day=1.0,
        percent=150.0,
    )
    with pytest.raises(InvalidDoseInput):
        compute_dose(di)
```

- [ ] **Step 6: Run test to verify it fails**

Run: `pytest tests/dosage/test_compute_dose.py -v`
Expected: FAIL — `ImportError: cannot import name 'compute_dose'`.

- [ ] **Step 7: Implement compute_dose**

Append to `cannabis_canary/dosage/calculator.py` (add the import at the top of the file, below the module docstring, and the function at the end):

```python
from cannabis_canary.dosage.models import CalcMode, DoseInput, DoseResult
```

```python
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
```

- [ ] **Step 8: Run test to verify it passes**

Run: `pytest tests/dosage/test_compute_dose.py -v`
Expected: PASS (6 passed).

- [ ] **Step 9: Add public API exports**

Replace `cannabis_canary/dosage/__init__.py` with:

```python
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
```

- [ ] **Step 10: Run the full suite**

Run: `pytest -v`
Expected: PASS (all 19 tests).

- [ ] **Step 11: Commit**

```bash
git add cannabis_canary/dosage/ tests/dosage/
git commit -m "feat(dosage): typed DoseInput/DoseResult model + compute_dose dispatcher

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage (dosage scope only):** Spec §7 formula — both branches (`grams × 1000 × %/100` and `mg/unit × units`) implemented and tested ✅. "Independent of method of ingestion" — method is absent from the math ✅. THC and CBD both supported via `Cannabinoid` ✅. Provider help-notes *copy* and product→mode UI mapping explicitly deferred to the form plan (noted in scope) ✅. The Colorado ±15% potency-variance limitation is a UI advisory, not math — belongs in the form plan ✅.

**2. Placeholder scan:** No TBD/TODO/"add validation"/"handle edge cases" — every step has concrete code and exact commands ✅.

**3. Type consistency:** `mg_per_day_from_concentration`, `mg_per_day_from_label`, `compute_dose`, `DoseInput`, `DoseResult`, `Cannabinoid`, `CalcMode`, `InvalidDoseInput` are spelled identically in the Interfaces blocks, implementation, and tests across both tasks ✅.
