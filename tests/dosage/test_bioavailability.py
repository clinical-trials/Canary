from cannabis_canary.dosage import (
    ROUTE_BIOAVAILABILITY,
    bioavailability_factor,
    effective_mg_per_day,
)


def test_effective_applies_configured_route_factor():
    # Assert the MATH (consumed × factor) against the config, not a hard-coded
    # clinical constant — so editing the factor updates behavior without a test
    # rewrite.
    assert effective_mg_per_day(100.0, "smoked") == 100.0 * ROUTE_BIOAVAILABILITY["smoked"]
    assert effective_mg_per_day(50.0, "oral") == 50.0 * ROUTE_BIOAVAILABILITY["oral"]


def test_topical_is_zero_effective():
    assert effective_mg_per_day(100.0, "topical") == 0.0


def test_unset_route_returns_none():
    assert effective_mg_per_day(100.0, "per-rectum") is None
    assert effective_mg_per_day(100.0, None) is None
    assert effective_mg_per_day(100.0, "unknown-route") is None


def test_bioavailability_factor_lookup():
    assert bioavailability_factor("smoked") == ROUTE_BIOAVAILABILITY["smoked"]
    assert bioavailability_factor(None) is None
