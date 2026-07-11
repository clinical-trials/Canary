# App Orchard Listing Copy — DRAFT

> **DRAFT — NOT FOR SUBMISSION.** Pending legal/compliance review, Epic developer-program
> membership, third-party security assessment, and IRB approval (see human-handoff gates in
> `docs/superpowers/specs/2026-06-29-cannabis-canary-v1-design.md`). Every statement below
> describes designed v1 functionality only; it contains no outcome claims, statistics,
> testimonials, endorsements, institutional affiliations, or certification claims, and none may
> be added without verified evidence. Category names must be reconciled with Epic's current
> marketplace taxonomy at submission time.

---

## App name

Cannabis Canary©

## Tagline

Structured cannabis social history, with a standardized THC mg/day dose, at the point of care.

## Short description

Cannabis Canary© replaces the single yes/no cannabis checkbox with a structured social-history
form, a calculator that normalizes any cannabis product to a common mg THC/day dose, and
evidence-summary decision-support cards — delivered inside the EHR via SMART on FHIR and
CDS Hooks.

## Long description

Most EHR workflows capture cannabis use as a single checkbox, leaving clinicians without the
product, potency, dose, and risk-factor detail that increasingly matters as medical and
recreational use expands. Cannabis Canary© is designed to close that gap without leaving the
chart.

**Structured capture.** When cannabis use is indicated, a CDS Hooks card prompts the provider
and launches a SMART on FHIR form in patient context. The instrument captures exposure status,
start/quit dates, method of ingestion, product type, quantity and potency, medical
vs. recreational use (with recommending provider and condition treated), adverse events,
desire to quit, and counseling given.

**A standardized dose.** The dosage calculator normalizes any product — flower, concentrates,
edibles, tinctures, vape products, topicals, and other labeled products — to a single common
metric: **mg THC per day**, computed from grams/day and %THC for flower and concentrates, or
from labeled mg-per-unit and units/day for labeled products. Contextual help notes assist the
provider in entering product-label values and interpreting the result. The calculator surfaces
its documented accuracy limitations, including published label-potency variance.

**Point-of-care decision support.** When a provider flags cannabinoid hyperemesis, fertility
concerns, or schizoaffective disorder, the app shows an evidence-summary card with cited
sources. A harm-reduction screen for driving under the influence of cannabis and alcohol co-use
prompts counseling or referral. Cards are informational only: they cite their sources, never
auto-act, and do not replace clinical judgment.

**Follow-up and trends.** Each capture records a last-reviewed timestamp with a configurable
follow-up reminder (default 3 months). Per-patient longitudinal views chart mg/day, potency,
exposure status, adverse events, desire to quit, and counseling over time.

**Standards-based by design.** Cannabis Canary© uses SMART App Launch, FHIR R4, and CDS Hooks
only — no proprietary APIs — and requests least-privilege, read-only scopes (Patient, Condition,
MedicationRequest, Observation). Version 1 does not write back to the chart. Captured responses
are stored in the application's own encrypted registry backend, operated under HIPAA
obligations, and are also intended to support a prospective research registry; any research use
is contingent on IRB approval and an informed-consent mechanism, which are prerequisites to
launch, not features of the software.

Version 1 is provider-facing only, with an initial clinical focus on geriatric care.

## Category suggestions

To be confirmed against the marketplace's current taxonomy at submission; likely fits:

1. Clinical decision support
2. Clinical documentation / workflow
3. Research / registries

## Not claimed anywhere in this listing (keep it that way)

- No effect on clinical outcomes, safety, efficiency, or documentation quality
- No user counts, adoption figures, or site names
- No testimonials, endorsements, or institutional affiliations
- No regulatory status, certification, or completed security assessment
- No active, approved, or enrolling research study

---

> **DRAFT — NOT FOR SUBMISSION.** See header note.
