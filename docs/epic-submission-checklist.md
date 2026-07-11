# Epic App Orchard Submission Checklist — Cannabis Canary©

Last updated: 2026-07-03. This tracks the **4-criteria build-complete bar** (the part in
our control) and the **human handoff gates** (the part that is not code and must be done
by a person).

## Build-complete bar

### 1. Standards-only (SMART on FHIR / FHIR R4 / CDS Hooks) — ✅ BUILT
- SMART App Launch with `.well-known/smart-configuration` discovery, OAuth2
  authorization-code + PKCE (S256), confidential-client Basic auth (public+PKCE fallback).
- FHIR R4 REST reads only: `Patient`, `Condition`, `MedicationRequest`, `Observation`.
- CDS Hooks `patient-view` service with standard `smart`-type launch link.
- **No Epic-proprietary API calls anywhere** — verified by code review of `cannabis_canary/smart/`
  and `cannabis_canary/cds/`; this is also what makes the build Cerner-portable.
- Evidence: 74-test suite exercises launch → callback → reads → capture end-to-end
  against a mocked standards-compliant EHR.

### 2. Registered at fhir.epic.com with least-privilege scopes — ⏸ READY, HUMAN STEP
- Scopes (read-only, minimum necessary):
  `launch openid fhirUser patient/Patient.read patient/Condition.read
  patient/MedicationRequest.read patient/Observation.read`
- Redirect URI: the deployment's `/callback`; CDS discovery at `/cds-services`.
- **Creating the registration requires an Epic account** — a human logs into
  https://fhir.epic.com, creates the app, pastes the scopes/URIs above, and sets
  `CANARY_CLIENT_ID` / `CANARY_CLIENT_SECRET` in the deployment.

### 3. Epic security/technical requirements — ✅ BUILT (deployment items flagged)
In code:
- Tokens server-side only (BFF); opaque HttpOnly/Secure/SameSite session cookie.
- OAuth `state` verified (constant-time), PKCE S256, no tokens/PHI in URLs or logs.
- Security headers (CSP, nosniff, no-referrer); `Cache-Control: no-store` on PHI routes.
- CSRF mitigation on state-changing APIs (custom-header requirement).
- Audit log of every login/view/capture in the registry.
Deployment requirements (not code — must be true in the hosting environment):
- TLS everywhere; encryption at rest for the registry DB (e.g., encrypted RDS/PG volume).
- Production session store (Redis/DB) if multi-process; secrets via env/secret manager.
- Known hardening TODO: templates currently use inline JS/CSS (`'unsafe-inline'` in CSP);
  move to static files + nonces before production deployment.

### 4. Correct PHI handling — ✅ BUILT (governance items at the gates below)
- Registry DB is the sole PHI store; minimum-necessary fields.
- PHI boundary enforced in code: only de-identified concept terms reach the evidence
  engine / PubMed (`cannabis_canary/smart/context.py`).
- No PHI to NCBI, no PHI in logs, `no-store` on PHI routes.

## ⛔ HUMAN HANDOFF GATES — none of these are code; do not attempt to automate

1. **Epic developer-program membership** — join at https://fhir.epic.com (org account),
   accept terms, then perform the registration in item 2.
2. **Third-party security assessment** — commission an independent review; Epic's
   listing process commonly expects one for PHI-bearing apps.
3. **IRB approval + informed consent** — prospective data capture on patients is
   human-subjects research. Phase I (per the proposal) needs IRB approval, a consent
   mechanism, and institutional sign-off **before any real patient data is captured**.
4. **HIPAA/BAA + legal** — BAA with the hosting provider; institutional executive
   buy-in; counsel review including Conant v. Walters (federal Schedule I context).

## Remaining engineering niceties (post-v1, not blockers to the above)
- Replace inline JS/CSS with static assets + CSP nonces.
- Production deployment manifest (containerfile, PostgreSQL, Redis sessions).
- Cerner (Oracle Health) sandbox registration + smoke test (code is standards-only;
  needs the same human registration step on their portal).
- Optional: write-back of a completed-visit summary (needs write scopes — deferred by spec).
