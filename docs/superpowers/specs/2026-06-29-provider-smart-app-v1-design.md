# Provider SMART on FHIR Evidence App — v1 Design Spec

**Date:** 2026-06-29
**Status:** Draft for user review
**Scope:** Phase 1 — provider-only v1 (the first Epic-App-Orchard-submittable artifact)

---

## 1. Goal

A SMART on FHIR app that a **clinician launches from within Epic** (and, by staying
vendor-neutral, Cerner/Oracle Health) in **patient context**. It reads the patient's
clinical picture (read-only), helps the clinician frame a focused clinical question, runs
a **live literature review over curated peer-reviewed journals in PubMed**, and produces a
**meta-analysis** (forest/funnel plots, heterogeneity) to inform care at the point of decision.

This is **Phase 1 of a larger platform** (researcher portal and patient view come later).
v1 ships **one role: provider.**

## 2. Definition of Done (the only part in our control)

The build is "complete" when all four are true and the app is demoable in the Epic sandbox:

1. **Standards-only** — built entirely on SMART App Launch + FHIR R4 calls. No Epic-proprietary APIs. (This is also what makes it Cerner-portable.)
2. **Registered** at `fhir.epic.com` with **least-privilege, read-only patient scopes**.
3. **Passes Epic's documented security/technical requirements** — TLS, correct token handling, audit logging, no PHI in logs or URLs.
4. **Correct PHI handling** — encryption in transit and at rest, minimum-necessary, and **no PHI ever sent to NCBI/PubMed**.

> ⛔ **HUMAN HANDOFF GATE.** When all four are green, **STOP**. The next steps are *not code*
> and must be performed by a human: (a) **Epic developer-program membership**, and (b) a
> **third-party security assessment / review**. The app will not be "submitted" or "uploaded"
> automatically — that is out of scope for the build.

## 3. Architecture

**Pattern: shared engine + thin SMART app (a slice of "Approach 2").** One reusable Python
analysis engine sits underneath; v1 ships only the provider SMART app on top of it. The
researcher portal and patient view attach to the *same* engine later — additive, no rework.

```
+-------------------- Provider SMART App (v1) ----------------------+
|                                                                   |
|  React SPA (renders inside Epic Hyperdrive embedded browser)      |
|        |  (session cookie; no tokens/PHI in the browser store)    |
|        v                                                          |
|  FastAPI backend  =  SMART confidential client (BFF pattern)      |
|    - auth/         OAuth2 token exchange, session, token storage  |
|    - fhir/         FHIR R4 reads + coded-concept extraction       |
|    - api/          endpoints the SPA calls                        |
|    - audit/,sec/   audit log, config, secrets, PHI boundary       |
|        |                                                          |
|        |  (de-identified clinical concepts ONLY cross this line)  |
|        v                                                          |
|  Shared Analysis Engine (pure-Python package, no PHI, no EHR dep) |
|    - pubmed/       E-utilities search/fetch + curated-journal     |
|                    allowlist filter                               |
|    - extraction/   per-study effect-data model + CSV import       |
|                    (interface designed for assisted-fill later)   |
|    - metaanalysis/ pooling (fixed/random), heterogeneity (Q,I²,τ²)|
+-------------------------------------------------------------------+
```

**Backend-for-Frontend (BFF), confidential client.** The backend holds the client secret,
performs the OAuth2 token exchange, and reads FHIR server-side. Tokens never reach the
browser. This gives us clean audit logging and a small, defensible security surface.

**The PHI boundary is explicit:** PHI lives only in the `auth`/`fhir` layer. Only
**de-identified, coded clinical concepts** (e.g., SNOMED/ICD/RxNorm/LOINC codes and MeSH
terms) cross into the analysis engine. The engine has **no knowledge of patients** and is
independently testable — which is exactly why it can be reused by the later researcher portal.

### Proposed stack (open to veto in review)
- **Backend:** Python + **FastAPI**; `httpx` + `authlib` for OAuth2; `fhir.resources` for R4 parsing.
- **Stats:** `statsmodels` (`stats.meta_analysis`) + `scipy`/`numpy` for pooling and heterogeneity.
- **Frontend:** React SPA; charts rendered client-side (Plotly or D3) from engine-computed numbers.
- **PubMed:** NCBI **E-utilities** (`esearch` + `efetch`/`esummary`), API key via env var, rate-limit aware.

## 4. Components (units, each independently understandable & testable)

| Unit | Does what | Input → Output | Depends on |
|------|-----------|----------------|------------|
| `engine/pubmed` | Search PubMed, screen to curated journals | PICO/terms → screened study metadata list | E-utilities, allowlist config |
| `engine/extraction` | Structured per-study effect-data model + CSV import/validation | rows → validated `StudyEffect` records | (pure) |
| `engine/metaanalysis` | Pool effects; compute heterogeneity | `StudyEffect[]` + method → pooled estimate, CI, Q/I²/τ² | statsmodels/scipy |
| `smartapp/auth` | SMART App Launch (confidential BFF), token & session mgmt | launch params → authed session | authlib, httpx |
| `smartapp/fhir` | FHIR R4 reads + concept extraction at PHI boundary | token + patient ctx → coded concepts (de-identified) | fhir.resources |
| `smartapp/api` | Endpoints the SPA calls | HTTP → JSON | the above |
| `web` | UI: launch, confirm question, run review, render plots | — | api |
| `common/audit`,`common/security` | Audit log, secrets/config, PHI-safe logging | — | — |

## 5. Data flow

1. **Launch** — Epic launches the SPA with `iss` + `launch`. Backend (confidential client)
   completes OAuth2; access token stored **server-side** only.
2. **Read context** — backend reads FHIR R4: `Patient`, `Condition` (problem list),
   `MedicationRequest`, `Observation` (labs).
3. **Frame the question** — backend derives a candidate clinical question (PICO-style) from
   coded concepts and **presents it to the clinician to confirm/edit**. Clinician-in-the-loop
   by design — avoids acting on a wrong auto-generated question. PHI stays server-side.
4. **Literature review** — backend queries PubMed via the engine, **filtered to the curated
   journal allowlist**, returns a screened study list for inclusion/exclusion (PRISMA-style).
5. **Extract** — clinician enters (or uploads a CSV of) structured effect data per included study
   (effect size, variance/CI, n, events). Interface built so an assisted "suggest values"
   step can slot in later (no rework).
6. **Analyze** — engine runs the meta-analysis (fixed + random effects, DerSimonian-Laird;
   Q, I², τ²) and returns structured numbers.
7. **Present** — SPA renders **forest plot, funnel plot**, pooled estimate + CI, heterogeneity.
   Clinician can **export/print** the summary. (Writing back to the chart is a *write* scope —
   **deferred**; v1 stays strictly read-only.)

## 6. Curated journals

A maintained **allowlist** (config file: NLM journal IDs / ISSNs) constrains results to
vetted peer-reviewed journals. Ships with a sensible default core-clinical set; structured so
the list can grow without code changes.

## 7. Security & PHI handling

- **Least-privilege scopes:** `launch`, `openid`, `fhirUser`, and read-only
  `patient/Patient.read`, `patient/Condition.read`, `patient/MedicationRequest.read`,
  `patient/Observation.read`.
- **No PHI to PubMed/NCBI** — only de-identified coded concepts/MeSH terms leave the PHI boundary.
- **Tokens server-side only** (BFF); never in browser storage, query strings, or logs.
- **TLS** for all transport; **encryption at rest** for anything persisted.
- **Audit logging** of FHIR access (who/which patient/when), stored minimally and secured.
- **No PHI in application logs or URLs**; session timeout enforced.

## 8. Error handling

- FHIR resource missing/empty → degrade gracefully (clinician can still frame a manual question).
- PubMed/E-utilities unavailable or rate-limited → retry/backoff, clear user-facing message, never block on it.
- Auth/token expiry → re-auth via SMART refresh flow.
- Invalid extraction input → validated with actionable errors before analysis runs.

## 9. Testing strategy

- **Engine unit tests:** PubMed parsing against saved fixtures; allowlist filtering;
  **meta-analysis math validated against canonical published datasets** (correctness is
  non-negotiable for a clinical tool).
- **Auth/integration tests:** SMART launch + token exchange against the **SMART Health IT
  sandbox** and the **Epic sandbox** (`fhir.epic.com`).
- **PHI-boundary test:** assert no PHI fields can reach the engine / outbound PubMed calls.

## 10. Out of scope for v1 (explicit)

Researcher portal & app-native auth · patient-facing view · cohort / Bulk Data `$export` ·
automated effect-size extraction from article text · write-back to the chart (DocumentReference).
All are later phases on the same shared engine.

## 11. Assumptions / decisions made (veto in review)

- Stack: Python/FastAPI + React; confidential **BFF** SMART client.
- Extraction is **manual/structured (CSV-capable)** for v1, interface ready for assisted-fill.
- Clinician **confirms** the derived clinical question (not fully automatic).
- v1 is **read-only**; no chart write-back.
