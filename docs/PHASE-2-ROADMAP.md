# Cannabis Canary© — Phase 2 Roadmap (living backlog)

v1 is provider-only structured cannabis social-history capture + THC mg/day dosage
(consumed and estimated-effective) + point-of-care decision support. The items below are
**deliberately out of v1 scope** and tracked here for later phases. Clinician suggestions
are collected as GitHub issues (labels: `phase-2`, `clinician-suggestion`).

## Tracked directions

1. **Capture CBD alongside THC (dual-cannabinoid dosing).**
   The instrument and calculator already model THC; extend to CBD (its own potency field,
   mg/day, and PK). Rationale: CBD has a distinct safety profile and modifies THC exposure.

2. **Drug-interaction flag (CYP450 / polypharmacy).**
   THC and CBD are metabolised by cytochrome-P450 enzymes (CYP2C9, CYP2C19, CYP3A4); CBD
   inhibits several (CYP3A4, CYP2C9, CYP2C19, CYP2B6) and can raise THC levels. Surface
   interactions against the patient's active medications (read from FHIR `MedicationRequest`),
   with an emphasis on high-risk pairs — e.g. **warfarin / anticoagulants (CYP2C9 → bleeding
   risk)** — and a **polypharmacy** review view.
   Evidence to build on: Bansal et al. (Drug Metab Dispos 2020/2022), Doohan et al.
   (AAPS J 2021), Zamarripa et al. (JAMA Netw Open 2023), Gorbenko et al. (Clin Pharmacol
   Ther 2024).

3. **Bioavailability factor sign-off (carry-over from v1).**
   The per-route factors in `cannabis_canary/dosage/bioavailability.py` (smoked 0.25,
   oral/sublingual 0.08, topical 0.00, per-rectum/patch unset) are cited (Permanente Journal
   TPP/19.200; Upadhyay et al. J Cannabis Res 2023) but remain **PENDING CLINICAL SIGN-OFF**.

4. **Clinician-suggested directions (open).**
   Collected via GitHub issues; triaged into this list. Examples we expect: additional
   drug-interaction pairs, extra product types/routes, fields, and workflow changes.

## How suggestions flow

The clinician-review demo (`docs/demo/index.html`, published to GitHub Pages) has a
"Suggest a direction" button that opens a pre-labelled GitHub issue. Maintainers triage
issues labelled `clinician-suggestion` into the tracked list above.

> None of these change v1's scope or the human-handoff gates (Epic membership, third-party
> security review, IRB, legal). They are future phases on the same shared engine.
