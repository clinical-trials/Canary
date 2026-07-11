"""Cannabis Canary© FastAPI app — SMART launch, capture form, CDS endpoints.

Security posture (see docs/epic-submission-checklist.md):
- BFF confidential client: tokens live in server-side sessions only.
- No PHI in URLs or logs; POST bodies carry the form data.
- Every chart access and capture is written to the registry audit log.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from cannabis_canary.cds import (
    CONTRAINDICATION_TOPICS,
    contraindication_cards,
    discovery,
    patient_view_cards,
)
from cannabis_canary.cds.services import SERVICE_ID
from cannabis_canary.dosage import (
    CalcMode,
    Cannabinoid,
    DoseInput,
    InvalidDoseInput,
    compute_dose,
)
from cannabis_canary.instrument import (
    EXPOSURE_STATUSES,
    METHODS,
    PRODUCT_TYPES,
    InstrumentValidationError,
    parse_history,
)
from cannabis_canary.registry import RegistryRepo, create_session_factory, init_db
from cannabis_canary.reminder import is_due, next_review_due
from cannabis_canary.smart import (
    FHIRClient,
    build_authorize_url,
    exchange_code,
    extract_context,
    fetch_smart_configuration,
    make_pkce,
)
from cannabis_canary.viz import trend_svg
from cannabis_canary.web.config import Settings
from cannabis_canary.web.sessions import COOKIE_NAME, MemorySessionStore

_TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _patient_display_name(patient: dict) -> str:
    for name in patient.get("name", []):
        if name.get("text"):
            return name["text"]
        parts = name.get("given", []) + [name.get("family", "")]
        joined = " ".join(p for p in parts if p)
        if joined:
            return joined
    return "Unknown patient"


def create_app(settings: Settings, http_client: httpx.Client | None = None) -> FastAPI:
    app = FastAPI(title="Cannabis Canary©", docs_url=None, redoc_url=None)
    app.state.settings = settings
    app.state.http = http_client or httpx.Client(timeout=15)
    app.state.sessions = MemorySessionStore()
    session_factory, engine = create_session_factory(settings.database_url)
    init_db(engine)
    app.state.db_factory = session_factory

    # --- helpers -----------------------------------------------------------

    def current_session(request: Request) -> dict:
        session = app.state.sessions.get(request.cookies.get(COOKIE_NAME))
        if session is None or "access_token" not in session:
            raise HTTPException(401, "No EHR session — launch from the EHR.")
        expires_at = session.get("expires_at")
        if expires_at is not None and datetime.now(timezone.utc) >= expires_at:
            raise HTTPException(401, "Session expired — relaunch from the EHR.")
        return session

    def repo() -> RegistryRepo:
        return RegistryRepo(app.state.db_factory())

    def require_api_header(request: Request) -> None:
        # CSRF mitigation: state-changing JSON APIs demand a custom header
        # that cross-site form posts cannot set.
        if request.headers.get("x-canary-request") != "1":
            raise HTTPException(403, "missing X-Canary-Request header")

    # --- security headers --------------------------------------------------

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; img-src 'self' data:"
        )
        if request.url.path.startswith(("/app", "/api")):
            response.headers["Cache-Control"] = "no-store"
        return response

    # --- basic + CDS Hooks endpoints ---------------------------------------

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return (
            "<h1>Cannabis Canary©</h1><p>This app must be launched from the "
            "EHR (SMART on FHIR EHR launch).</p>"
        )

    @app.get("/cds-services")
    def cds_discovery() -> dict:
        return discovery()

    @app.post(f"/cds-services/{SERVICE_ID}")
    def cds_patient_view() -> dict:
        return {"cards": patient_view_cards(settings.app_base_url)}

    # --- SMART launch flow --------------------------------------------------

    @app.get("/launch")
    def launch(request: Request, iss: str, launch: str):
        smart_config = fetch_smart_configuration(iss, app.state.http)
        verifier, challenge = make_pkce()
        state = secrets.token_urlsafe(16)
        sid, session = app.state.sessions.create()
        session["pending"] = {
            "state": state,
            "verifier": verifier,
            "iss": iss,
            "token_endpoint": smart_config["token_endpoint"],
        }
        url = build_authorize_url(
            authorize_endpoint=smart_config["authorization_endpoint"],
            client_id=settings.client_id,
            redirect_uri=settings.redirect_uri,
            scopes=settings.scopes,
            state=state,
            aud=iss,
            code_challenge=challenge,
            launch=launch,
        )
        response = RedirectResponse(url, status_code=302)
        response.set_cookie(
            COOKIE_NAME, sid, httponly=True, secure=True, samesite="lax"
        )
        return response

    @app.get("/callback")
    def callback(request: Request, code: str, state: str):
        session = app.state.sessions.get(request.cookies.get(COOKIE_NAME))
        pending = (session or {}).get("pending")
        if not pending or not secrets.compare_digest(pending["state"], state):
            raise HTTPException(400, "invalid state — relaunch from the EHR")
        token = exchange_code(
            token_endpoint=pending["token_endpoint"],
            code=code,
            redirect_uri=settings.redirect_uri,
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            code_verifier=pending["verifier"],
            http=app.state.http,
        )
        if token.patient is None:
            raise HTTPException(400, "no patient context in token response")
        session.pop("pending", None)
        session["access_token"] = token.access_token
        session["iss"] = pending["iss"]
        session["patient_id"] = token.patient
        session["fhir_user"] = token.fhir_user or "provider:unknown"
        if token.expires_in is not None:
            session["expires_at"] = datetime.now(timezone.utc) + timedelta(
                seconds=token.expires_in
            )
        repo().record_audit(
            actor=session["fhir_user"], action="login", patient_id=token.patient
        )
        return RedirectResponse("/app", status_code=302)

    # --- provider UI --------------------------------------------------------

    @app.get("/app", response_class=HTMLResponse)
    def provider_app(request: Request):
        session = current_session(request)
        fhir = FHIRClient(session["iss"], session["access_token"], app.state.http)
        patient = fhir.patient(session["patient_id"])
        conditions = fhir.conditions(session["patient_id"])
        observations = fhir.lab_observations(session["patient_id"])
        ctx = extract_context(patient, conditions, observations)

        r = repo()
        r.record_audit(
            actor=session["fhir_user"], action="view",
            patient_id=session["patient_id"],
        )
        points = [
            (at.date(), mg) for at, mg in r.trend_points(session["patient_id"])
        ]
        latest = r.latest_for_patient(session["patient_id"])
        months = settings.review_interval_months
        review = None
        if latest is not None:
            last = latest.authored_at.date()
            review = {
                "last": last.isoformat(),
                "due": next_review_due(last, months).isoformat(),
                "is_due": is_due(last, months),
            }

        return _TEMPLATES.TemplateResponse(
            request,
            "form.html",
            {
                "patient_name": _patient_display_name(patient),
                "context": ctx,
                "exposure_statuses": EXPOSURE_STATUSES,
                "methods": METHODS,
                "product_types": PRODUCT_TYPES,
                "contraindications": CONTRAINDICATION_TOPICS,
                "trend_svg": trend_svg(points),
                "review": review,
                "review_months": months,
            },
        )

    # --- JSON APIs -----------------------------------------------------------

    @app.post("/api/dose")
    async def api_dose(request: Request):
        require_api_header(request)
        body = await request.json()
        try:
            mode = CalcMode(body.get("dose_mode", ""))
            result = compute_dose(
                DoseInput(
                    cannabinoid=Cannabinoid.THC,
                    mode=mode,
                    grams_per_day=body.get("grams_per_day"),
                    percent=body.get("percent_thc"),
                    mg_per_unit=body.get("mg_per_unit"),
                    units_per_day=body.get("units_per_day"),
                )
            )
        except (InvalidDoseInput, ValueError) as exc:
            return JSONResponse({"error": str(exc)}, status_code=422)
        return {"thc_mg_per_day": result.mg_per_day}

    @app.post("/api/history")
    async def api_save_history(request: Request):
        require_api_header(request)
        session = current_session(request)
        body = await request.json()
        try:
            history = parse_history(body)
        except InstrumentValidationError as exc:
            return JSONResponse({"errors": exc.errors}, status_code=422)
        now = datetime.now(timezone.utc)
        r = repo()
        record = r.save_history(
            patient_id=session["patient_id"],
            author_id=session["fhir_user"],
            history=history,
            authored_at=now,
        )
        r.record_audit(
            actor=session["fhir_user"], action="capture",
            patient_id=session["patient_id"],
        )
        return {
            "id": record.id,
            "thc_mg_per_day": record.thc_mg_per_day,
            "authored_at": now.isoformat(),
            "next_review_due": next_review_due(
                now.date(), settings.review_interval_months
            ).isoformat(),
        }

    @app.get("/api/history")
    def api_list_history(request: Request):
        session = current_session(request)
        rows = repo().list_for_patient(session["patient_id"])
        return {
            "records": [
                {
                    "authored_at": row.authored_at.isoformat(),
                    "exposure_status": row.exposure_status,
                    "thc_mg_per_day": row.thc_mg_per_day,
                }
                for row in rows
            ]
        }

    return app


def dev_app() -> FastAPI:
    """uvicorn --factory cannabis_canary.web.app:dev_app"""
    return create_app(Settings.from_env())
