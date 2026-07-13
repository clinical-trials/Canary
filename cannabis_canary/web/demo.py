"""LOCAL DEMO server — renders the real provider form against an in-process
fake EHR so the UI can be viewed without a live SMART launch.

⚠️ DEMO ONLY. This module fabricates a session (no real OAuth handshake) and
ships canned patient data. It is NOT wired into the production entrypoint
(`cannabis_canary.web.app:dev_app`) and must never be run against real PHI.
Run with:  uvicorn --factory cannabis_canary.web.demo:demo_app --port 8765
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
from fastapi.responses import RedirectResponse

from cannabis_canary.instrument import parse_history
from cannabis_canary.registry import RegistryRepo
from cannabis_canary.web.app import create_app
from cannabis_canary.web.config import Settings
from cannabis_canary.web.sessions import COOKIE_NAME

_PATIENT_ID = "pat-demo"

_DEMO_PATIENT = {
    "resourceType": "Patient",
    "id": _PATIENT_ID,
    "gender": "male",
    "birthDate": "1949-05-12",
    "name": [{"text": "Demo Patient (SANDBOX — not a real person)"}],
}
_DEMO_CONDITIONS = {
    "resourceType": "Bundle",
    "entry": [
        {"resource": {"resourceType": "Condition", "code": {"text": "Chronic pain"}}},
        {"resource": {"resourceType": "Condition",
                      "code": {"text": "Post-traumatic stress disorder"}}},
    ],
}
_DEMO_OBS = {
    "resourceType": "Bundle",
    "entry": [
        {"resource": {
            "resourceType": "Observation",
            "code": {"text": "Cannabinoid screen, urine"},
            "valueString": "Positive",
            "effectiveDateTime": "2026-05-01",
        }},
    ],
}


def _fake_ehr(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if f"/Patient/{_PATIENT_ID}" in url:
        return httpx.Response(200, json=_DEMO_PATIENT)
    if "/Condition" in url:
        return httpx.Response(200, json=_DEMO_CONDITIONS)
    if "/Observation" in url:
        return httpx.Response(200, json=_DEMO_OBS)
    return httpx.Response(404, json={"error": f"unmocked {url}"})


def _seed_history(app) -> None:
    repo = RegistryRepo(app.state.db_factory())
    now = datetime.now(timezone.utc)
    for months_ago, grams in [(6, 0.5), (3, 1.0), (0, 1.5)]:
        history = parse_history(
            {
                "exposure_status": "current-every-day",
                "method": "sublingual",
                "product_type": "tincture",
                "dose_mode": "concentration",
                "grams_per_day": grams,
                "percent_thc": 10.0,
                "medical_use": True,
                "condition_treated": "chronic pain",
                "counseling_given": True,
            }
        )
        repo.save_history(
            patient_id=_PATIENT_ID,
            author_id="Practitioner/demo",
            history=history,
            authored_at=now - timedelta(days=30 * months_ago),
        )


def demo_app():
    settings = Settings(
        client_id="demo",
        client_secret="demo",
        redirect_uri="http://127.0.0.1:8765/callback",
        app_base_url="http://127.0.0.1:8765",
        database_url="sqlite+pysqlite:///:memory:",
    )
    app = create_app(
        settings, http_client=httpx.Client(transport=httpx.MockTransport(_fake_ehr))
    )
    _seed_history(app)

    @app.get("/")
    def demo_home():
        return RedirectResponse("/demo", status_code=302)

    @app.get("/demo")
    def demo_launch():
        sid, session = app.state.sessions.create()
        session["access_token"] = "demo-token"
        session["iss"] = "https://fhir.demo.example/r4"
        session["patient_id"] = _PATIENT_ID
        session["fhir_user"] = "Practitioner/demo"
        response = RedirectResponse("/app", status_code=302)
        # secure=False so the cookie works over plain http://127.0.0.1 locally
        response.set_cookie(COOKIE_NAME, sid, httponly=True, secure=False,
                            samesite="lax")
        return response

    return app
