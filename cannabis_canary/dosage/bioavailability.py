"""Route-of-ingestion bioavailability → an ESTIMATED effective THC dose.

⚠️  CLINICAL ESTIMATES — PENDING SIGN-OFF. These factors convert a *consumed*
    mg/day into an *estimated systemically-absorbed (effective)* mg/day. THC
    bioavailability is HIGHLY variable between individuals, products, and
    studies; treat these as rough midpoints, not measured values. A clinician
    (and the IRB) must review/validate them before clinical use, and they are
    intended to be edited here in one place.

Primary source (chosen for this project):
  Sharma P. et al., "Mechanisms of Action and Pharmacokinetics of Cannabis,"
  The Permanente Journal, DOI 10.7812/TPP/19.200.
    - Inhaled THC bioavailability 10–35% (~25% maximum systemic after
      pyrolysis/sidestream losses)
    - Oral (ingested) THC bioavailability 4–12%
  Sublingual is treated ≈ oral (broader literature / Sativex studies show
  sublingual THC bioavailability similar to oral). Topical creams show no
  meaningful systemic absorption. Rectal and transdermal-patch factors are left
  UNSET (contested / insufficient evidence) — the effective dose is simply not
  estimated for those routes rather than guessed.
"""
from __future__ import annotations

# route (method of ingestion) -> systemic bioavailability fraction (0..1),
# or None when there is no agreed factor (effective dose is not estimated).
ROUTE_BIOAVAILABILITY: dict[str, float | None] = {
    "smoked": 0.25,       # inhaled 10–35%, ~25% max systemic (TPP/19.200)
    "oral": 0.08,         # ingested 4–12% (TPP/19.200), midpoint
    "sublingual": 0.08,   # ≈ oral in controlled studies (flagged)
    "topical": 0.0,       # local only — no meaningful systemic absorption
    "per-rectum": None,   # contested; not estimated
}

# Short, provider-facing guidance per route (no fabricated statistics).
ROUTE_GUIDANCE: dict[str, str] = {
    "smoked": "Inhaled/smoked: ~25% reaches the bloodstream (range 10–35%); "
              "combustion loses much of the THC. The mg entered is what's in the "
              "product, not what's absorbed.",
    "oral": "Oral/edible: low systemic availability (~4–12%) due to first-pass "
            "liver metabolism; onset is slow and effect is delayed.",
    "sublingual": "Sublingual/tincture: held under the tongue; in controlled "
                  "studies availability is similar to oral (not clearly higher).",
    "topical": "Topical cream: acts locally; essentially no systemic absorption "
               "or psychoactivity. Effective systemic dose is treated as ~0.",
    "per-rectum": "Per-rectum: systemic availability is contested and not "
                  "reliably established; effective dose is left unestimated.",
}


def bioavailability_factor(route: str | None) -> float | None:
    if route is None:
        return None
    return ROUTE_BIOAVAILABILITY.get(route)


def effective_mg_per_day(consumed_mg: float, route: str | None) -> float | None:
    """Estimated systemically-absorbed mg/day = consumed × route factor.

    Returns None when the route has no agreed factor, so callers can show
    "not estimated" rather than a fabricated number.
    """
    factor = bioavailability_factor(route)
    if factor is None:
        return None
    return consumed_mg * factor
