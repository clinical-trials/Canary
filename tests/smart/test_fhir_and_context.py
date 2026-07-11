import json

import httpx

from cannabis_canary.smart.context import extract_context
from cannabis_canary.smart.fhir_client import FHIRClient


def bundle(*resources):
    return {
        "resourceType": "Bundle",
        "entry": [{"resource": r} for r in resources],
    }


PATIENT = {"resourceType": "Patient", "id": "pat-42", "gender": "male",
           "name": [{"text": "Test Patient"}], "birthDate": "1950-02-01"}
CONDITION = {"resourceType": "Condition", "id": "c1",
             "code": {"text": "Chronic pain"}}
UDS_OBS = {"resourceType": "Observation", "id": "o1",
           "code": {"text": "Cannabinoid screen, urine"},
           "valueString": "Positive",
           "effectiveDateTime": "2026-05-01"}
OTHER_OBS = {"resourceType": "Observation", "id": "o2",
             "code": {"text": "Hemoglobin"}, "valueString": "14"}


def make_client(handler):
    return FHIRClient(
        base_url="https://fhir.example.org/r4",
        access_token="tok",
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_fhir_client_sends_bearer_and_reads_patient():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["authorization"]
        seen["accept"] = request.headers["accept"]
        seen["url"] = str(request.url)
        return httpx.Response(200, json=PATIENT)

    client = make_client(handler)
    patient = client.patient("pat-42")
    assert patient["id"] == "pat-42"
    assert seen["auth"] == "Bearer tok"
    assert seen["accept"] == "application/fhir+json"
    assert seen["url"].endswith("/Patient/pat-42")


def test_fhir_client_searches_return_resources():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/Condition" in str(request.url):
            return httpx.Response(200, json=bundle(CONDITION))
        return httpx.Response(200, json=bundle(UDS_OBS, OTHER_OBS))

    client = make_client(handler)
    conditions = client.conditions("pat-42")
    observations = client.lab_observations("pat-42")
    assert conditions[0]["code"]["text"] == "Chronic pain"
    assert len(observations) == 2


def test_extract_context_deidentifies_and_finds_uds():
    ctx = extract_context(PATIENT, [CONDITION], [UDS_OBS, OTHER_OBS])
    assert ctx.sex == "male"
    assert ctx.birth_year == 1950
    assert ctx.problems == ("Chronic pain",)
    assert len(ctx.uds_results) == 1
    assert ctx.uds_results[0].display == "Cannabinoid screen, urine"
    assert ctx.uds_results[0].value == "Positive"
    # De-identified: no name, no id anywhere in the dataclass
    assert "Test Patient" not in json.dumps(ctx.problems)


def test_extract_context_handles_missing_fields():
    ctx = extract_context({"resourceType": "Patient"}, [], [])
    assert ctx.sex is None
    assert ctx.birth_year is None
    assert ctx.problems == ()
    assert ctx.uds_results == ()
