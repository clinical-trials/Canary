"""FHIR R4 Questionnaire definition for the Cannabis Use social-history form.

Plain-dict FHIR JSON (no external FHIR library needed to *define* the form).
Value sets come from the locked v1 spec (docs/superpowers/specs/
2026-06-29-cannabis-canary-v1-design.md §6).
"""
from __future__ import annotations

QUESTIONNAIRE_URL = "https://cannabis-canary.example.org/fhir/Questionnaire/cannabis-use"

EXPOSURE_STATUSES: tuple[str, ...] = (
    "never",
    "former",
    "current-some-days",
    "current-every-day",
)

METHODS: tuple[str, ...] = (
    "oral",
    "sublingual",
    "topical",
    "smoked",
    "per-rectum",
)

PRODUCT_TYPES: tuple[str, ...] = (
    "cream",
    "edible-gummy",
    "smoked-joint",
    "wax",
    "shatter",
    "vape-pen",
    "vaporizer",
    "transdermal-patch",
    "tincture",
    "oil",
)


def _choice(link_id: str, text: str, codes: tuple[str, ...]) -> dict:
    return {
        "linkId": link_id,
        "text": text,
        "type": "choice",
        "answerOption": [{"valueCoding": {"code": c, "display": c.replace("-", " ")}} for c in codes],
    }


def _item(link_id: str, text: str, type_: str, **extra) -> dict:
    item = {"linkId": link_id, "text": text, "type": type_}
    item.update(extra)
    return item


def questionnaire() -> dict:
    """The Cannabis Use form as a FHIR R4 Questionnaire resource (dict)."""
    return {
        "resourceType": "Questionnaire",
        "url": QUESTIONNAIRE_URL,
        "name": "CannabisUse",
        "title": "Cannabis Canary© — Cannabis Use Social History",
        "status": "active",
        "subjectType": ["Patient"],
        "item": [
            _choice("exposure_status", "Exposure status", EXPOSURE_STATUSES),
            _item("start_date", "Start date", "date"),
            _item("quit_date", "Quit date", "date"),
            _item(
                "products",
                "Cannabis products (multiple types & routes allowed — doses add up)",
                "group",
                repeats=True,
                item=[
                    _choice("product_type", "Type of product", PRODUCT_TYPES),
                    _choice("method", "Method of ingestion", METHODS),
                    _item("grams_per_day", "Grams per day", "decimal"),
                    _item("percent_thc", "Potency (%THC)", "decimal"),
                    _item("mg_per_unit", "mg THC per unit (from product label)", "decimal"),
                    _item("units_per_day", "Units per day", "decimal"),
                ],
            ),
            _item("thc_mg_per_day", "THC mg per day, consumed (total, computed)", "decimal", readOnly=True),
            _item("effective_mg_per_day", "THC mg per day, estimated effective (total, computed)", "decimal", readOnly=True),
            _item("medical_use", "Medical use", "boolean"),
            _item("recommending_physician", "Recommending physician", "string"),
            _item("condition_treated", "Medical condition treating with cannabis", "string"),
            _item("duic", "Driving under the influence of cannabis (DUIC)", "boolean"),
            _item("mix_alcohol", "Mixes alcohol and THC", "boolean"),
            _item("desire_to_quit", "Desire to quit", "boolean"),
            _item("counseling_given", "Counseling given", "boolean"),
            _item("hyperemesis", "Hyperemesis", "boolean"),
            _item(
                "reproductive_issue",
                "Reproductive concerns — sperm motility or breast milk",
                "boolean",
            ),
            _item("schizoaffective", "Presence of schizoaffective disorders", "boolean"),
            _item(
                "adverse_events",
                "Adverse events",
                "group",
                repeats=True,
                item=[
                    _item("ae_date", "Event date", "date"),
                    _item("ae_description", "Description", "string"),
                    _item("ae_code", "Optional code", "string"),
                ],
            ),
            _item("comment", "Comment", "text"),
        ],
    }
