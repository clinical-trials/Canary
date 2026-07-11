"""Evidence engine — curated-journal PubMed literature access.

De-identified side of the PHI boundary: ONLY clinical concept terms are ever
sent to NCBI. Never patient identifiers, never free text from the chart.
"""
from cannabis_canary.evidence.journals import DEFAULT_CURATED_JOURNALS, load_allowlist
from cannabis_canary.evidence.pubmed import (
    PubMedClient,
    StudySummary,
    build_search_url,
    filter_curated,
)

__all__ = [
    "DEFAULT_CURATED_JOURNALS",
    "load_allowlist",
    "PubMedClient",
    "StudySummary",
    "build_search_url",
    "filter_curated",
]
