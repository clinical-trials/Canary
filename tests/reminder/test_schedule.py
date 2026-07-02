from datetime import date

import pytest

from cannabis_canary.reminder import is_due, next_review_due


def test_default_interval_is_3_months():
    assert next_review_due(date(2026, 1, 15)) == date(2026, 4, 15)


def test_configurable_6_and_12_months():
    assert next_review_due(date(2026, 1, 15), months=6) == date(2026, 7, 15)
    assert next_review_due(date(2026, 1, 15), months=12) == date(2027, 1, 15)


def test_year_boundary():
    assert next_review_due(date(2026, 11, 30)) == date(2027, 2, 28)


def test_month_end_clamps():
    # Jan 31 + 3 months -> Apr 30 (April has no 31st)
    assert next_review_due(date(2026, 1, 31)) == date(2026, 4, 30)


def test_invalid_interval_rejected():
    with pytest.raises(ValueError):
        next_review_due(date(2026, 1, 15), months=5)


def test_is_due():
    last = date(2026, 1, 15)
    assert is_due(last, today=date(2026, 4, 15))
    assert is_due(last, today=date(2026, 5, 1))
    assert not is_due(last, today=date(2026, 4, 14))
