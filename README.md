# Cannabis Canary©

A SMART on FHIR + CDS Hooks app for Epic (App Orchard) and Cerner/Oracle Health that
replaces the single yes/no "marijuana use" checkbox with a **structured cannabis
social-history form**, a **THC mg/day dosage calculator**, and **point-of-care decision
support** — prospectively capturing data into a research registry.

**Design spec:** [docs/superpowers/specs/2026-06-29-cannabis-canary-v1-design.md](docs/superpowers/specs/2026-06-29-cannabis-canary-v1-design.md)
**Submission status:** [docs/epic-submission-checklist.md](docs/epic-submission-checklist.md)

## Architecture

```
EHR (Epic / Cerner)
 ├── CDS Hooks patient-view card ──► SMART EHR launch
 ▼
FastAPI backend (BFF confidential client — tokens never reach the browser)
 ├── smart/      SMART discovery, OAuth2 + PKCE, FHIR R4 reads (read-only)
 ├── instrument/ FHIR Questionnaire + validated capture model
 ├── dosage/     pure mg/day math (crown jewel — exhaustively tested)
 ├── registry/   PHI store (SQLAlchemy) + audit log        ← PHI custodian
 ├── cds/        CDS Hooks discovery + decision-support cards
 ├── evidence/   curated-journal PubMed engine (E-utilities) ← NO PHI crosses in
 ├── reminder/   3/6/12-month review scheduling
 ├── viz/        server-side trend SVG
 └── web/        launch flow, provider form UI, JSON APIs
```

Standards-only (SMART App Launch, FHIR R4, CDS Hooks, OAuth2/PKCE) — no
vendor-proprietary calls, which is what makes the same build Epic- and Cerner-compatible.

## Dose formula (user-confirmed)

- Weight+potency products: `mg/day = grams/day × 1000 × (%THC ÷ 100)` → 1.0 g @ 10% = 100 mg/day
- Labeled products: `mg/day = mg per unit × units/day`
- Output is one common mg/day metric, independent of method of ingestion.

## Run locally

Requires Python ≥ 3.11.

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                      # full test suite
```

Run the app (values come from your EHR sandbox registration):

```bash
export CANARY_CLIENT_ID="<client id from fhir.epic.com registration>"
export CANARY_CLIENT_SECRET="<secret, if confidential client>"   # optional; PKCE-only if unset
export CANARY_REDIRECT_URI="https://localhost:8765/callback"
export CANARY_APP_BASE_URL="https://localhost:8765"
export CANARY_DATABASE_URL="sqlite+pysqlite:///./canary.db"      # PostgreSQL in production
export NCBI_API_KEY="<optional, raises PubMed rate limits>"
export CANARY_REVIEW_MONTHS=3                                     # 3 (default), 6, or 12

uvicorn --factory cannabis_canary.web.app:dev_app --port 8765
```

Endpoints: `/launch` + `/callback` (SMART), `/app` (provider form), `/cds-services`
(CDS Hooks discovery), `/api/dose`, `/api/history`, `/health`.

## Testing against sandboxes

- **SMART Health IT launcher** (https://launch.smarthealthit.org) — point its EHR-launch
  simulator at `/launch`; no registration needed.
- **Epic sandbox** (https://fhir.epic.com) — register the app (human step), set the
  client id/secret env vars, launch from the Epic sandbox tooling.

## OAuth2 scopes (least privilege, read-only)

`launch openid fhirUser patient/Patient.read patient/Condition.read
patient/MedicationRequest.read patient/Observation.read`

## PHI handling

- Registry DB is the only PHI store; every login/view/capture is written to the audit log.
- Only de-identified concept terms are ever sent to PubMed/NCBI.
- Tokens are held in server-side sessions (BFF); no PHI in URLs or logs; `no-store` on
  PHI-bearing routes; TLS and encryption-at-rest are deployment requirements
  (see the submission checklist).

## Status

Provider-only v1 per the locked spec. Researcher portal (Phase II population analytics)
and patient-facing views are later phases on the same engine. Branding assets live in
`branding/` (from the design workstream).
