# Cannabis Canary — v1 Design Spec

**Date:** 2026-06-29
**Status:** Draft for user review
**Name:** Cannabis Canary© App (confirmed by user 2026-06-29; proposal had used *Cannabinoid Canary©*)
**Supersedes:** `2026-06-29-provider-smart-app-v1-design.md` (generic evidence app — replaced once the
real concept, a prospective cannabis social-history registry, was provided).
**Source of truth:** user's grant proposal (pasted 2026-06-29) + Figure A "Cannabis Use Form".

---

## 1. Purpose & background

Today most EHRs capture cannabis use as a **single yes/no checkbox**, despite 30+ states with medical
programs, 20+ conditions for which cannabis is recommended, and real clinical contraindications. Cannabis
Canary replaces that checkbox with a **structured cannabis social-history form + point-of-care decision
support**, and **prospectively captures** the data for a cohort study. The single most clinically important
output is a **daily THC dose in mg/day**.

This is **Phase I / provider-only v1** — the first App-Orchard-submittable artifact. Researcher (population/
cohort, Phase II) and patient roles are later phases on the same engine.

## 2. What v1 does (scope)

1. **Trigger** — when cannabis use is indicated (the "marijuana use = yes" event), a **CDS Hooks** card
   prompts the provider; clicking it launches the **SMART on FHIR** social-history form in patient context.
2. **Capture** the Cannabis Use instrument (Section 6) → stored in **our own registry** (Option 2).
3. **Compute mg THC/day** via the dosage calculator (Section 7) — the crown-jewel feature.
4. **Decision support** — when the provider flags **hyperemesis, fertility, or schizoaffective disorder**,
   show an evidence-based card (Section 8).
5. **Harm-reduction screen** — DUIC and alcohol co-use → offer counseling / refer (Section 9).
6. **Medical vs. recreational** — distinguish, capturing recommending provider + medical condition.
7. **Review tracking** — "last reviewed" timestamp + a recurring follow-up reminder (default 3 mo;
   configurable 6/12 mo or off).
8. **Visualize prospective data** — per-patient longitudinal trends (mg/day, potency, exposure status,
   adverse events, desire-to-quit, counseling) inside the app.

## 3. Definition of Done + human handoff gates

**Build-complete bar (the only part in our control):**
1. **Standards-only** — SMART App Launch + FHIR R4 + CDS Hooks. No Epic-proprietary APIs (keeps it Cerner-portable).
2. **Registered** at `fhir.epic.com` with least-privilege scopes.
3. **Passes Epic's documented security/technical requirements.**
4. **Correct PHI handling** — encryption in transit/at rest, minimum-necessary, no PHI to NCBI/PubMed.

> ⛔ **HUMAN HANDOFF GATES — when the four above are green, STOP.** These are *not code*:
> (a) **Epic developer-program membership**; (b) **third-party security assessment**;
> (c) **IRB approval** for the prospective cohort study + an **informed-consent mechanism**;
> (d) institutional/legal sign-off — **HIPAA/BAA**, executive buy-in, and review of **Conant v. Walters**
> (federal Schedule I considerations). Do not attempt to submit/launch the study or app automatically.

## 4. Architecture

**CDS Hooks (trigger + alerts) → SMART on FHIR app (the form) → own registry backend (storage) →
read-only FHIR (context).** Fully standards-based ⇒ Epic + Cerner compatible.

```
EHR (Epic / Cerner)
  │  cannabis-use event → CDS Hooks card  ──► launches ──┐
  ▼                                                       ▼
Read-only FHIR R4 (context):              SMART on FHIR app (React SPA in Hyperdrive)
  Patient (sex), Condition (problems),         │  session cookie; no tokens/PHI in browser
  MedicationRequest, Observation               ▼
  (urine drug screen)                     FastAPI backend = confidential SMART client (BFF)
                                               ├─ auth/   OAuth2, session, token storage
                                               ├─ fhir/   R4 reads + concept extraction (PHI boundary)
                                               ├─ registry/  REGISTRY DB — captured cannabis history (PHI custodian)
                                               ├─ dosage/    mg THC/day calculator (pure, heavily tested)
                                               ├─ cds/       CDS Hooks service (cards) + decision-support content
                                               └─ api/    endpoints the SPA calls
                                               ▼
                                          Shared evidence engine (no PHI): curated-PubMed lit review
                                          → powers decision-support card content
```

**We are a PHI custodian** (Option 2): the registry DB holds identifiable prospective data → full HIPAA,
encryption, audit, BAA, IRB. Storage target per proposal budget: S3-class object/db storage.

**PHI boundary:** only **de-identified coded concepts** cross into the shared evidence engine and to PubMed.
Registry PHI never leaves our secured backend.

### Proposed stack (veto in review)
Python + **FastAPI**; `authlib`/`httpx` (OAuth2/BFF); `fhir.resources` (R4); registry in **PostgreSQL**
(encrypted) with object storage for attachments; React SPA; `statsmodels`/`scipy` for the evidence engine;
charts client-side. CDS Hooks implemented per the HL7 CDS Hooks spec.

## 5. Components (each independently testable)

| Unit | Does what | Depends on |
|------|-----------|-----------|
| `cds/hooks` | Serves CDS Hooks cards (trigger + contraindication alerts) | FHIR ctx, content |
| `smartapp/auth` | SMART App Launch (confidential BFF), session/token mgmt | authlib |
| `smartapp/fhir` | R4 reads (Patient/Condition/MedicationRequest/Observation) + concept extraction | fhir.resources |
| `registry` | Persist & retrieve captured cannabis-history responses (the PHI store) | PostgreSQL |
| `dosage` | Compute mg THC/day (pure functions, exhaustively tested) | — |
| `instrument` | Cannabis Use form definition (FHIR Questionnaire) + validation | — |
| `evidence` | Curated-PubMed literature → decision-support content | E-utilities, statsmodels |
| `reminder` | Last-reviewed + recurring follow-up scheduling | registry |
| `viz` (web) | Per-patient longitudinal charts | api |
| `common/audit`,`common/security` | Audit log, secrets, PHI-safe logging | — |

## 6. Cannabis Use instrument (v1 capture schema)

FHIR **`Questionnaire`** (definition) + **`QuestionnaireResponse`** (each capture), stored in registry.

| Field | Type | Value set / notes |
|------|------|-------------------|
| Exposure status | coded | Never / Former (quit) / Current–some days / Current–every day |
| Start date | date | |
| Quit date | date (nullable) | |
| Method of ingestion | coded | **Oral, Sublingual, Topical, Smoked, Per rectum** (from proposal) |
| Type of product | coded | **Cream, Edible/gummy, Smoked joint, Wax, Shatter, Vape pen, Vaporizer, Transdermal patch, Tincture, Oil** |
| Grams/day | numeric | calculator input |
| Potency (%THC) | numeric | calculator input |
| %CBD / mg THC per unit | numeric | from product label (for labeled products) |
| **mg THC/day** | **computed** | dosage calculator — see Section 7 (formula pending sign-off) |
| Adverse events | structured report | date + free-text description + optional coding (one or more AE entries) |
| Medical use | boolean | if yes → recommending physician + medical condition |
| Recommending physician | text | |
| Medical condition treated | text (codable) | |
| DUIC | boolean | driving under influence of cannabis |
| Mix ROH & THC | boolean | alcohol co-use |
| Desire to quit | boolean | |
| Counseling given | boolean | |
| Hyperemesis | boolean | → decision support |
| Reproductive issue (motility/breast milk) | boolean | → decision support |
| Schizoaffective disorder present | boolean | → decision support |
| Comment | text | |
| Last reviewed | timestamp + action | drives reminder |

## 7. Dosage calculator (crown-jewel feature) — **formula CONFIRMED 2026-06-29**

Normalizes any product/method to a common **mg THC/day**. (Figure A's "10 mg/day" was a grams-vs-mg unit slip.)
- Flower/concentrate: `mg THC/day = grams_per_day × 1000 × (%THC ÷ 100)` (1.0 g @ 10% = **100 mg/day**)
- Labeled products: `mg THC/day = mg_THC_per_unit × units_per_day` (from label)
- "Independent of method of ingestion" = single common output metric; inputs differ by product type.
- **Provider help notes:** the calculator/form surfaces contextual guidance to help the provider enter
  product-label values and interpret the computed dose (per user request).

**Testing is non-negotiable here:** golden-value unit tests across every product type; the calculator is a
pure module so it can be validated in isolation. Note Colorado ±15% label-potency variance as a documented
accuracy limitation surfaced to the user.

## 8. Decision support (hyperemesis · fertility · schizoaffective)

When a contraindication is flagged, show an **evidence-based card** ("UpToDate-style"), with content drawn
from the **curated-PubMed evidence engine** and the proposal's citations. Cards are informational, cite
sources, and never auto-act. Schizoaffective/psychosis card reflects the risk literature (frequent/early-onset
use; the cited preventable-harm context).

## 9. Harm-reduction screen

DUIC and alcohol co-use → prompt **counseling at point of care or referral**, logged as `counseling given`.

## 10. Security, PHI & study context

- **Least-privilege read scopes** for context: `Patient.read`, `Condition.read`, `MedicationRequest.read`,
  `Observation.read` (urine drug screen, sex); plus CDS Hooks. No write-back to chart in v1.
- **Registry is the PHI store** → encryption at rest, field-level where appropriate, full audit, BAA.
- **No PHI to PubMed/NCBI** — only de-identified concepts.
- **Study mechanics** (control vs. intervention arm assignment, provider-satisfaction survey) are part of the
  *study*, not the core capture app; v1 exposes the data the study needs but keeps arm logic minimal/config-driven.

## 11. Out of scope for v1

Researcher/population portal (Phase II cohort analytics) · patient-facing view & PRO capture · FHIR write-back
to the chart · automated extraction of values from notes · provider-satisfaction survey tooling (study
instrument, separable).

## 12. Resolved decisions (2026-06-29)

1. **mg/day formula** — ✅ confirmed (Section 7); provider help notes added.
2. **Product-type value set** — ✅ proposal list + Tincture + Oil.
3. **Adverse events** — ✅ date + free-text description + optional coding.
4. **App name** — ✅ "Cannabis Canary©".

All v1 design questions are resolved; spec is ready for implementation planning.
