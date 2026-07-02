import pytest

from cannabis_canary.instrument.validation import (
    InstrumentValidationError,
    parse_history,
    to_questionnaire_response,
)


def valid_payload(**overrides):
    payload = {
        "exposure_status": "current-every-day",
        "start_date": "2005-03-03",
        "method": "sublingual",
        "product_type": "tincture",
        "dose_mode": "concentration",
        "grams_per_day": 1.0,
        "percent_thc": 10.0,
        "medical_use": True,
        "recommending_physician": "Dr. Example",
        "condition_treated": "chronic pain",
        "duic": False,
        "mix_alcohol": False,
        "desire_to_quit": False,
        "counseling_given": True,
        "hyperemesis": False,
        "reproductive_issue": False,
        "schizoaffective": False,
        "adverse_events": [{"date": "2016-01-27", "description": "dizziness"}],
        "comment": "example",
    }
    payload.update(overrides)
    return payload


def test_parse_valid_history_computes_dose():
    h = parse_history(valid_payload())
    assert h.exposure_status == "current-every-day"
    assert h.thc_mg_per_day == 100.0  # 1.0 g @ 10% -> 100 mg/day


def test_parse_label_mode():
    h = parse_history(
        valid_payload(
            dose_mode="label", grams_per_day=None, percent_thc=None,
            mg_per_unit=10.0, units_per_day=2.0,
        )
    )
    assert h.thc_mg_per_day == 20.0


def test_never_user_needs_no_dose():
    h = parse_history(
        {"exposure_status": "never"}
    )
    assert h.thc_mg_per_day is None


def test_rejects_unknown_exposure_status():
    with pytest.raises(InstrumentValidationError) as exc:
        parse_history(valid_payload(exposure_status="sometimes"))
    assert "exposure_status" in str(exc.value)


def test_rejects_unknown_method_and_product():
    with pytest.raises(InstrumentValidationError):
        parse_history(valid_payload(method="injection"))
    with pytest.raises(InstrumentValidationError):
        parse_history(valid_payload(product_type="brownie-mix"))


def test_rejects_bad_date():
    with pytest.raises(InstrumentValidationError):
        parse_history(valid_payload(start_date="03/03/2005"))


def test_rejects_dose_mode_missing_inputs():
    with pytest.raises(InstrumentValidationError):
        parse_history(valid_payload(percent_thc=None))


def test_collects_multiple_errors():
    with pytest.raises(InstrumentValidationError) as exc:
        parse_history(valid_payload(exposure_status="nope", method="injection"))
    assert len(exc.value.errors) >= 2


def test_questionnaire_response_maps_answers():
    h = parse_history(valid_payload())
    qr = to_questionnaire_response(
        h, authored="2026-06-29T12:00:00Z", subject_ref="Patient/abc"
    )
    assert qr["resourceType"] == "QuestionnaireResponse"
    assert qr["status"] == "completed"
    assert qr["subject"]["reference"] == "Patient/abc"
    by_link = {i["linkId"]: i for i in qr["item"]}
    assert by_link["exposure_status"]["answer"][0]["valueCoding"]["code"] == "current-every-day"
    assert by_link["thc_mg_per_day"]["answer"][0]["valueDecimal"] == 100.0
    assert by_link["counseling_given"]["answer"][0]["valueBoolean"] is True
    ae = by_link["adverse_events"]
    ae_items = {i["linkId"]: i for i in ae["item"]}
    assert ae_items["ae_description"]["answer"][0]["valueString"] == "dizziness"
