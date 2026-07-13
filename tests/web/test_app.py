"""End-to-end web tests: fake EHR (MockTransport) + real app + in-memory DB.

Covers the full SMART launch → callback → /app → capture → list cycle.
"""
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from cannabis_canary.web.app import create_app
from cannabis_canary.web.config import Settings

ISS = "https://fhir.ehr.example.org/r4"

SMART_CONFIG = {
    "authorization_endpoint": "https://ehr.example.org/authorize",
    "token_endpoint": "https://ehr.example.org/token",
}
TOKEN = {
    "access_token": "tok-1",
    "token_type": "Bearer",
    "expires_in": 3600,
    "patient": "pat-42",
    "fhirUser": "Practitioner/doc-9",
}
PATIENT = {"resourceType": "Patient", "id": "pat-42", "gender": "male",
           "name": [{"text": "Sandbox Patient"}], "birthDate": "1950-02-01"}


def fake_ehr(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if url.endswith("/.well-known/smart-configuration"):
        return httpx.Response(200, json=SMART_CONFIG)
    if url.startswith("https://ehr.example.org/token"):
        return httpx.Response(200, json=TOKEN)
    if "/Patient/pat-42" in url:
        return httpx.Response(200, json=PATIENT)
    if "/Condition" in url:
        return httpx.Response(200, json={
            "resourceType": "Bundle",
            "entry": [{"resource": {"resourceType": "Condition",
                                    "code": {"text": "Chronic pain"}}}],
        })
    if "/Observation" in url:
        return httpx.Response(200, json={"resourceType": "Bundle", "entry": []})
    return httpx.Response(404, json={"error": f"unmocked {url}"})


@pytest.fixture()
def client() -> TestClient:
    settings = Settings(
        client_id="canary-client",
        client_secret="canary-secret",
        redirect_uri="https://testserver/callback",
        app_base_url="https://testserver",
        database_url="sqlite+pysqlite:///:memory:",
    )
    app = create_app(
        settings, http_client=httpx.Client(transport=httpx.MockTransport(fake_ehr))
    )
    return TestClient(app, base_url="https://testserver")


def do_launch(client: TestClient) -> None:
    resp = client.get(
        "/launch", params={"iss": ISS, "launch": "xyz"}, follow_redirects=False
    )
    assert resp.status_code == 302
    state = parse_qs(urlparse(resp.headers["location"]).query)["state"][0]
    resp = client.get(
        "/callback", params={"code": "abc", "state": state}, follow_redirects=False
    )
    assert resp.status_code == 302
    assert resp.headers["location"] == "/app"


API_HEADERS = {"X-Canary-Request": "1"}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_cds_discovery_and_card(client):
    services = client.get("/cds-services").json()["services"]
    assert services[0]["id"] == "cannabis-canary-social-history"
    cards = client.post(
        "/cds-services/cannabis-canary-social-history", json={}
    ).json()["cards"]
    assert cards[0]["links"][0]["url"] == "https://testserver/launch"
    assert cards[0]["links"][0]["type"] == "smart"


def test_launch_redirects_to_authorize_with_smart_params(client):
    resp = client.get(
        "/launch", params={"iss": ISS, "launch": "xyz"}, follow_redirects=False
    )
    q = parse_qs(urlparse(resp.headers["location"]).query)
    assert q["aud"] == [ISS]
    assert q["launch"] == ["xyz"]
    assert q["code_challenge_method"] == ["S256"]


def test_callback_rejects_bad_state(client):
    client.get("/launch", params={"iss": ISS, "launch": "xyz"},
               follow_redirects=False)
    resp = client.get("/callback", params={"code": "abc", "state": "WRONG"},
                      follow_redirects=False)
    assert resp.status_code == 400


def test_app_requires_session(client):
    assert client.get("/app").status_code == 401


def test_full_flow_form_renders_with_context(client):
    do_launch(client)
    resp = client.get("/app")
    assert resp.status_code == 200
    page = resp.text
    assert "Sandbox Patient" in page
    assert "Chronic pain" in page
    assert "No dose data recorded yet" in page
    assert "Cannabis Use" in page   # SmartForm legend (matches Figure A)
    assert "mg per day" in page     # the big dosage readout label


def test_dose_api(client):
    resp = client.post(
        "/api/dose", headers=API_HEADERS,
        json={"dose_mode": "concentration", "grams_per_day": 1.0,
              "percent_thc": 10.0},
    )
    assert resp.json() == {"thc_mg_per_day": 100.0}

    resp = client.post(
        "/api/dose", headers=API_HEADERS,
        json={"dose_mode": "concentration", "grams_per_day": 1.0,
              "percent_thc": 150.0},
    )
    assert resp.status_code == 422


def test_dose_api_sums_multiple_products(client):
    resp = client.post(
        "/api/dose", headers=API_HEADERS,
        json={"products": [
            {"dose_mode": "concentration", "grams_per_day": 1.0, "percent_thc": 10.0},
            {"dose_mode": "label", "mg_per_unit": 10.0, "units_per_day": 2.0},
        ]},
    )
    assert resp.json() == {"thc_mg_per_day": 120.0}


def test_dose_api_skips_incomplete_rows(client):
    resp = client.post(
        "/api/dose", headers=API_HEADERS,
        json={"products": [
            {"dose_mode": "concentration", "grams_per_day": 2.0, "percent_thc": 10.0},
            {"dose_mode": "", "grams_per_day": None},  # incomplete -> skipped
        ]},
    )
    assert resp.json() == {"thc_mg_per_day": 200.0}


def test_dose_api_requires_custom_header(client):
    resp = client.post("/api/dose", json={"dose_mode": "label"})
    assert resp.status_code == 403


def test_capture_and_list_history(client):
    do_launch(client)
    resp = client.post(
        "/api/history", headers=API_HEADERS,
        json={"exposure_status": "current-every-day",
              "dose_mode": "concentration",
              "grams_per_day": 1.0, "percent_thc": 10.0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["thc_mg_per_day"] == 100.0
    assert body["next_review_due"]

    listed = client.get("/api/history").json()["records"]
    assert len(listed) == 1
    assert listed[0]["exposure_status"] == "current-every-day"

    # invalid payload is rejected with the collected errors
    resp = client.post(
        "/api/history", headers=API_HEADERS,
        json={"exposure_status": "sometimes"},
    )
    assert resp.status_code == 422
    assert "exposure_status" in resp.json()["errors"][0]
