import pytest

from cannabis_canary.dosage.calculator import (
    InvalidDoseInput,
    compute_dose,
    total_mg_per_day,
)
from cannabis_canary.dosage.models import (
    CalcMode,
    Cannabinoid,
    DoseInput,
    DoseResult,
)


def _thc(mode, **kw):
    return DoseInput(cannabinoid=Cannabinoid.THC, mode=mode, **kw)


def test_total_mg_per_day_is_additive_across_products():
    inputs = [
        _thc(CalcMode.CONCENTRATION, grams_per_day=1.0, percent=10.0),  # 100
        _thc(CalcMode.LABEL, mg_per_unit=10.0, units_per_day=2.0),       # 20
    ]
    assert total_mg_per_day(inputs) == 120.0


def test_total_mg_per_day_empty_is_zero():
    assert total_mg_per_day([]) == 0.0


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
