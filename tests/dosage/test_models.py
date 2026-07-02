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
