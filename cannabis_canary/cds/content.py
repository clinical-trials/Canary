"""Decision-support card content for the three spec contraindications.

Honesty rules for this file:
- Guidance text is drawn from the clinical statements in the user's grant
  proposal (the project's source document) — not invented.
- We do NOT ship a static citation list; each card links to a LIVE PubMed
  search so providers see current literature. No fabricated references.
"""
from __future__ import annotations

from cannabis_canary.evidence import build_search_url

CONTRAINDICATION_TOPICS: dict[str, dict] = {
    "hyperemesis": {
        "summary": "Possible cannabinoid hyperemesis syndrome",
        "detail": (
            "Cannabinoid hyperemesis syndrome is recurrent nausea and vomiting "
            "that resolves after cannabis cessation or hot bathing. Reports "
            "describe repeated ED visits, hospitalizations, and clinic visits "
            "before diagnosis. Consider cessation counseling and follow-up."
        ),
        "pubmed_term": "cannabinoid hyperemesis syndrome",
    },
    "reproductive": {
        "summary": "Reproductive considerations with cannabis use",
        "detail": (
            "Exogenous cannabinoids show a dose-dependent effect on sperm "
            "motility and capacitation. Cannabis metabolites transfer into "
            "breast milk; the prevailing best-practice consensus is that "
            "mothers refrain from cannabis use during lactation. Review the "
            "current evidence for this patient's situation."
        ),
        "pubmed_term": "cannabis fertility sperm motility OR cannabis lactation breast milk",
    },
    "schizoaffective": {
        "summary": "Psychosis-spectrum risk with cannabis use",
        "detail": (
            "Among cannabis users at risk for psychosis, frequent use, "
            "early-onset use, and continued use after clinical presentation "
            "have been associated with transition to psychosis. For patients "
            "with diagnosed or family history of schizophrenia spectrum or "
            "bipolar disorder, counsel and consider dissuading use."
        ),
        "pubmed_term": "cannabis psychosis schizoaffective risk",
    },
}


def contraindication_cards(topics: list[str]) -> list[dict]:
    """CDS cards for flagged contraindications; unknown topics are skipped."""
    cards = []
    for topic in topics:
        spec = CONTRAINDICATION_TOPICS.get(topic)
        if spec is None:
            continue
        cards.append(
            {
                "summary": spec["summary"],
                "indicator": "warning",
                "detail": spec["detail"],
                "source": {
                    "label": "Cannabis Canary© — verify against current literature",
                },
                "links": [
                    {
                        "label": "Current evidence on PubMed",
                        "url": build_search_url(spec["pubmed_term"]),
                        "type": "absolute",
                    }
                ],
            }
        )
    return cards
