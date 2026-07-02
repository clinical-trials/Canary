from cannabis_canary.instrument.definition import (
    EXPOSURE_STATUSES,
    METHODS,
    PRODUCT_TYPES,
    questionnaire,
)


def test_questionnaire_is_fhir_r4_shape():
    q = questionnaire()
    assert q["resourceType"] == "Questionnaire"
    assert q["status"] == "active"
    assert isinstance(q["item"], list)


def test_questionnaire_contains_all_core_linkids():
    q = questionnaire()

    def collect(items):
        for it in items:
            yield it["linkId"]
            yield from collect(it.get("item", []))

    link_ids = set(collect(q["item"]))
    expected = {
        "exposure_status", "start_date", "quit_date", "method", "product_type",
        "grams_per_day", "percent_thc", "mg_per_unit", "units_per_day",
        "thc_mg_per_day", "medical_use", "recommending_physician",
        "condition_treated", "duic", "mix_alcohol", "desire_to_quit",
        "counseling_given", "hyperemesis", "reproductive_issue",
        "schizoaffective", "adverse_events", "ae_date", "ae_description",
        "comment",
    }
    assert expected <= link_ids


def test_value_sets_match_spec():
    assert "current-every-day" in EXPOSURE_STATUSES
    assert {"oral", "sublingual", "topical", "smoked", "per-rectum"} == set(METHODS)
    assert "tincture" in PRODUCT_TYPES and "oil" in PRODUCT_TYPES
    assert "transdermal-patch" in PRODUCT_TYPES


def test_adverse_events_group_repeats():
    q = questionnaire()
    ae = next(i for i in q["item"] if i["linkId"] == "adverse_events")
    assert ae["type"] == "group"
    assert ae["repeats"] is True
