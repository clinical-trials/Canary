# Cannabis Canary© — Brand Guide

**Status:** Working draft (branch `feat/canary-branding`). Design assets are original work created
for this project. Nothing in this guide asserts a factual claim about outcomes, adoption,
certification, or endorsement — see "Honesty rules" below.

---

## 1. Brand story

Most electronic health records reduce cannabis use to a single yes/no checkbox. Cannabis Canary©
replaces that checkbox with a structured cannabis social-history instrument, a THC mg/day dosage
calculator, and point-of-care decision support — delivered inside the clinician's existing EHR
workflow via SMART on FHIR and CDS Hooks, and prospectively captured for a research registry.

The name carries two meanings, and both are load-bearing:

1. **The canary in the coal mine.** A sentinel that gives an early warning before harm occurs.
   The app surfaces contraindication signals — cannabinoid hyperemesis, fertility effects,
   schizoaffective risk — at the point of care, when a clinician can still act on them.
2. **The canary release.** In software, a canary release is a small, careful, closely watched
   rollout. That is exactly the posture of this product: a deliberate Phase I, provider-only
   deployment, standards-based, measured before it is scaled.

The brand personality follows from the metaphor: **a quiet, reliable sentinel.** The canary does
not shout, decorate, or entertain. It watches, it signals clearly when something matters, and it
stays out of the way the rest of the time.

## 2. Name usage rules

- The full product name is **Cannabis Canary©**.
- Use the **©** symbol on the **first mention** in any document, screen, or listing
  ("Cannabis Canary©"). Subsequent mentions in the same document may use "Cannabis Canary."
- Never abbreviate to "CC", "Canary app", "the Canary", or "CanCan" in external material.
  Internal shorthand in code and tickets (`cannabis-canary`, `cc-` prefixes) is fine.
- Do not restyle the name: no camel case ("CannabisCanary"), no hyphen, no all-caps except in
  contexts that force uppercase.
- The name always refers to the software product. Never use it in a way that implies it is a
  clinical service, a treatment, or a credentialed entity.
- Do not append unverified legal designations (®, ™ beyond the established ©, "patent pending",
  etc.). If trademark status changes, update this guide first.

## 3. Voice and tone

**Cannabis Canary© must read like a medical device, not a dispensary.** The audience is
clinicians — Phase I specifically targets geriatric providers — reading inside Epic's embedded
Hyperdrive browser between patients. They are time-poor, liability-aware, and allergic to hype.

### Voice attributes

| Attribute | Means | Does not mean |
|---|---|---|
| **Clinical** | Precise terms, units stated, sources cited | Jargon for its own sake |
| **Calm** | Neutral declaratives; alerts are informative, never alarmist | Flat or evasive |
| **Trustworthy** | Say what the software does; state limitations plainly | Overclaiming, vagueness |
| **Deferential** | Decision support informs; the clinician decides | Prescriptive commands |

### Tone rules

- Write in plain, complete sentences. Prefer "computes a daily THC dose in mg/day" over
  "smart dosing insights."
- State limitations where they matter. Example the product itself uses: label-potency variance
  (documented at ±15% in Colorado testing regulation) is surfaced to the provider as an accuracy
  limitation of the calculator, not hidden.
- Decision-support content is informational and cites its sources. Copy must never imply the app
  diagnoses, treats, or directs care. Preferred framing: "surfaces," "flags," "summarizes
  evidence," "prompts consideration of."
- No exclamation points in product UI or clinical copy. Ever.
- Numbers get units. "100 mg THC/day", never "100" or "a high dose."

### Vocabulary

**Use:** cannabis, cannabinoid, THC, CBD, mg/day, exposure, social history, structured capture,
decision support, contraindication, harm reduction, registry, prospective.

**Never use:** weed, pot, marijuana*, 420, "elevate/elevated" puns, "high" puns, "green" puns,
"budding," "blazing," "joint venture" wordplay, leaf/smoke emoji, or any dispensary-style
lifestyle framing.

\* "Marijuana" appears only when quoting an existing EHR field name (e.g., the legacy
"marijuana use" checkbox) or a statute that uses the term. Product copy says "cannabis."

## 4. Visual identity summary

- **Mark:** an abstract geometric canary — perched (vigilant, not in flight), facing forward,
  emitting a small signal. The bird is built from simple circles and triangles so it reads at
  16–32 px inside EHR chrome. Full details in `logo/README.md`.
- **No cannabis-leaf imagery, anywhere, ever.** It undermines clinical credibility and many
  hospital systems prohibit it. This is a hard rule, equal in force to the honesty rules.
- **Color:** calm cool-gray neutrals carry the interface; a restrained canary yellow is the accent.
  Yellow is a *signal* color here — used sparingly for the mark and highlights, never for body
  text (it cannot meet contrast requirements on white). See `tokens/colors.css` for the palette
  with verified WCAG AA contrast ratios.
- **Typography:** system font stack (no webfont downloads inside the Hyperdrive webview).
  Tabular numerals for dosage figures. See `tokens/tokens.json`.

## 5. Do's and don'ts

**Do**

- Lead with what the software actually does: structured capture, mg/day calculation,
  point-of-care decision support, longitudinal visualization.
- Use the sentinel/early-warning metaphor in narrative copy — it is the brand.
- Keep alert styling proportional to severity (info vs. warning) and reserve yellow accents for
  genuine signals.
- Cite sources in any copy that references evidence, and let the evidence engine's citations do
  the talking.
- Mark all outward-facing copy DRAFT until it clears legal/compliance review.

**Don't**

- Don't use cannabis-leaf imagery, smoke motifs, green-and-rasta palettes, or dispensary
  aesthetics of any kind.
- Don't use stoner wordplay or drug-culture references, even ironically.
- Don't invent statistics, testimonials, endorsements, institutional affiliations, user counts,
  outcome claims, or regulatory/certification status. If it is not in the design doc or otherwise
  verifiably true, it does not go in copy.
- Don't imply the app treats, diagnoses, prescribes, or replaces clinical judgment.
- Don't describe the registry or study as approved, active, or enrolling — IRB approval and
  related gates are explicit human-handoff items that have not occurred.
- Don't let the canary mark appear in flight, cartoonified with a face, or singing musical
  notes — the bird is a sentinel, not a mascot.

## 6. Honesty rules (non-negotiable)

Everything factual in brand and listing copy must be traceable to the design spec
(`docs/superpowers/specs/2026-06-29-cannabis-canary-v1-design.md`) or another verifiable source.
Design assets (logos, palette, tone) are creative work and ours to define; **facts are not.**
When in doubt, describe the mechanism ("computes mg THC/day from grams/day and %THC") rather than
the benefit ("improves outcomes") — mechanisms are checkable, benefit claims require evidence we
do not yet have.
