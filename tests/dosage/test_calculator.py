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
