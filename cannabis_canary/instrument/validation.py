"""Validation + typed model for captured cannabis social histories.

Accepts the JSON payload the form posts, validates against the spec's value
sets, computes an ADDITIVE THC mg/day total across one or more products via the
dosage module, and converts to a FHIR R4 QuestionnaireResponse for registry
storage. Collects ALL errors before raising so the provider can fix everything
in one pass.

Payload shape for products (both accepted):
  - New/multi:  {"products": [{"product_type","dose_mode","grams_per_day",
                 "percent_thc","mg_per_unit","units_per_day"}, ...]}
  - Legacy/single: the same keys at the top level (wrapped into one product).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from cannabis_canary.dosage import (
    CalcMode,
    Cannabinoid,
    DoseInput,
    InvalidDoseInput,
    compute_dose,
)
from cannabis_canary.instrument.definition import (
    EXPOSURE_STATUSES,
    METHODS,
    PRODUCT_TYPES,
    QUESTIONNAIRE_URL,
)

_LEGACY_PRODUCT_KEYS = (
    "product_type", "dose_mode", "grams_per_day", "percent_thc",
    "mg_per_unit", "units_per_day",
)


class InstrumentValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class AdverseEvent:
    description: str
    date: date | None = None
    code: str | None = None


@dataclass(frozen=True)
class ProductEntry:
    product_type: str | None = None
    dose_mode: str | None = None
    grams_per_day: float | None = None
    percent_thc: float | None = None
    mg_per_unit: float | None = None
    units_per_day: float | None = None
    thc_mg_per_day: float | None = None  # this product's contribution


@dataclass(frozen=True)
class CannabisHistory:
    exposure_status: str
    start_date: date | None = None
    quit_date: date | None = None
    method: str | None = None
    products: tuple[ProductEntry, ...] = field(default_factory=tuple)
    thc_mg_per_day: float | None = None  # additive total across products
    medical_use: bool | None = None
    recommending_physician: str | None = None
    condition_treated: str | None = None
    duic: bool | None = None
    mix_alcohol: bool | None = None
    desire_to_quit: bool | None = None
    counseling_given: bool | None = None
    hyperemesis: bool | None = None
    reproductive_issue: bool | None = None
    schizoaffective: bool | None = None
    adverse_events: tuple[AdverseEvent, ...] = field(default_factory=tuple)
    comment: str | None = None


def _parse_date(value, field_name: str, errors: list[str]) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        errors.append(f"{field_name}: expected ISO date (YYYY-MM-DD), got {value!r}")
        return None


def _parse_float(value, field_name: str, errors: list[str]) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{field_name}: expected a number, got {value!r}")
        return None


def _parse_bool(value, field_name: str, errors: list[str]) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.lower() in ("true", "false", "yes", "no"):
        return value.lower() in ("true", "yes")
    errors.append(f"{field_name}: expected a boolean, got {value!r}")
    return None


def _parse_product(p: dict, i: int, errors: list[str]) -> ProductEntry:
    ptype = p.get("product_type") or None
    if ptype is not None and ptype not in PRODUCT_TYPES:
        errors.append(
            f"products[{i}].product_type: must be one of {PRODUCT_TYPES}, got {ptype!r}"
        )
    grams = _parse_float(p.get("grams_per_day"), f"products[{i}].grams_per_day", errors)
    pct = _parse_float(p.get("percent_thc"), f"products[{i}].percent_thc", errors)
    mgu = _parse_float(p.get("mg_per_unit"), f"products[{i}].mg_per_unit", errors)
    units = _parse_float(p.get("units_per_day"), f"products[{i}].units_per_day", errors)

    dose_mode = p.get("dose_mode") or None
    dose: float | None = None
    if dose_mode is not None:
        try:
            mode = CalcMode(dose_mode)
        except ValueError:
            errors.append(
                f"products[{i}].dose_mode: must be 'concentration' or 'label', "
                f"got {dose_mode!r}"
            )
            mode = None
        if mode is not None:
            try:
                dose = compute_dose(
                    DoseInput(
                        cannabinoid=Cannabinoid.THC, mode=mode,
                        grams_per_day=grams, percent=pct,
                        mg_per_unit=mgu, units_per_day=units,
                    )
                ).mg_per_day
            except InvalidDoseInput as exc:
                errors.append(f"products[{i}].dose: {exc}")

    return ProductEntry(
        product_type=ptype, dose_mode=dose_mode, grams_per_day=grams,
        percent_thc=pct, mg_per_unit=mgu, units_per_day=units, thc_mg_per_day=dose,
    )


def _raw_products(payload: dict) -> list[dict]:
    if isinstance(payload.get("products"), list):
        return payload["products"]
    if any(payload.get(k) not in (None, "") for k in _LEGACY_PRODUCT_KEYS):
        return [{k: payload.get(k) for k in _LEGACY_PRODUCT_KEYS}]
    return []


def parse_history(payload: dict) -> CannabisHistory:
    """Validate a form payload and return a typed CannabisHistory.

    Raises InstrumentValidationError with ALL problems found.
    """
    errors: list[str] = []

    exposure = payload.get("exposure_status")
    if exposure not in EXPOSURE_STATUSES:
        errors.append(
            f"exposure_status: must be one of {EXPOSURE_STATUSES}, got {exposure!r}"
        )

    method = payload.get("method") or None
    if method is not None and method not in METHODS:
        errors.append(f"method: must be one of {METHODS}, got {method!r}")

    start = _parse_date(payload.get("start_date"), "start_date", errors)
    quit_ = _parse_date(payload.get("quit_date"), "quit_date", errors)

    products = tuple(
        _parse_product(p, i, errors) for i, p in enumerate(_raw_products(payload))
    )
    contributions = [p.thc_mg_per_day for p in products if p.thc_mg_per_day is not None]
    total = sum(contributions) if contributions else None

    bools = {
        name: _parse_bool(payload.get(name), name, errors)
        for name in (
            "medical_use", "duic", "mix_alcohol", "desire_to_quit",
            "counseling_given", "hyperemesis", "reproductive_issue",
            "schizoaffective",
        )
    }

    adverse_events: list[AdverseEvent] = []
    for i, ae in enumerate(payload.get("adverse_events") or []):
        desc = (ae.get("description") or "").strip()
        if not desc:
            errors.append(f"adverse_events[{i}]: description is required")
            continue
        adverse_events.append(
            AdverseEvent(
                description=desc,
                date=_parse_date(ae.get("date"), f"adverse_events[{i}].date", errors),
                code=(ae.get("code") or None),
            )
        )

    if errors:
        raise InstrumentValidationError(errors)

    return CannabisHistory(
        exposure_status=exposure,
        start_date=start,
        quit_date=quit_,
        method=method,
        products=products,
        thc_mg_per_day=total,
        adverse_events=tuple(adverse_events),
        comment=(payload.get("comment") or None),
        recommending_physician=(payload.get("recommending_physician") or None),
        condition_treated=(payload.get("condition_treated") or None),
        **bools,
    )


def _answer(value) -> dict:
    if isinstance(value, bool):
        return {"valueBoolean": value}
    if isinstance(value, float):
        return {"valueDecimal": value}
    if isinstance(value, date):
        return {"valueDate": value.isoformat()}
    return {"valueString": str(value)}


def to_questionnaire_response(
    history: CannabisHistory,
    authored: str,
    subject_ref: str | None = None,
) -> dict:
    """Convert a validated history into a FHIR R4 QuestionnaireResponse dict."""
    items: list[dict] = []

    def add(link_id: str, value, coded: bool = False):
        if value is None:
            return
        answer = (
            {"valueCoding": {"code": value, "display": value.replace("-", " ")}}
            if coded
            else _answer(value)
        )
        items.append({"linkId": link_id, "answer": [answer]})

    add("exposure_status", history.exposure_status, coded=True)
    add("start_date", history.start_date)
    add("quit_date", history.quit_date)
    add("method", history.method, coded=True)

    for product in history.products:
        p_items: list[dict] = []
        if product.product_type is not None:
            p_items.append({
                "linkId": "product_type",
                "answer": [{"valueCoding": {
                    "code": product.product_type,
                    "display": product.product_type.replace("-", " "),
                }}],
            })
        for lid, val in (
            ("grams_per_day", product.grams_per_day),
            ("percent_thc", product.percent_thc),
            ("mg_per_unit", product.mg_per_unit),
            ("units_per_day", product.units_per_day),
        ):
            if val is not None:
                p_items.append({"linkId": lid, "answer": [_answer(val)]})
        if p_items:
            items.append({"linkId": "products", "item": p_items})

    add("thc_mg_per_day", history.thc_mg_per_day)  # additive total
    add("medical_use", history.medical_use)
    add("recommending_physician", history.recommending_physician)
    add("condition_treated", history.condition_treated)
    add("duic", history.duic)
    add("mix_alcohol", history.mix_alcohol)
    add("desire_to_quit", history.desire_to_quit)
    add("counseling_given", history.counseling_given)
    add("hyperemesis", history.hyperemesis)
    add("reproductive_issue", history.reproductive_issue)
    add("schizoaffective", history.schizoaffective)

    for ae in history.adverse_events:
        ae_items = [{"linkId": "ae_description", "answer": [_answer(ae.description)]}]
        if ae.date is not None:
            ae_items.append({"linkId": "ae_date", "answer": [_answer(ae.date)]})
        if ae.code is not None:
            ae_items.append({"linkId": "ae_code", "answer": [_answer(ae.code)]})
        items.append({"linkId": "adverse_events", "item": ae_items})

    if history.comment is not None:
        items.append({"linkId": "comment", "answer": [_answer(history.comment)]})

    qr = {
        "resourceType": "QuestionnaireResponse",
        "questionnaire": QUESTIONNAIRE_URL,
        "status": "completed",
        "authored": authored,
        "item": items,
    }
    if subject_ref is not None:
        qr["subject"] = {"reference": subject_ref}
    return qr
