"""Curated peer-reviewed journal allowlist.

Names only (PubMed full names + common abbreviations) — deliberately no ISSNs,
which we will not ship unverified. Deployments can extend/replace the list via
a JSON config file (a plain JSON array of journal-name strings).
"""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CURATED_JOURNALS: tuple[str, ...] = (
    # Full PubMed journal names
    "The New England journal of medicine",
    "JAMA",
    "JAMA internal medicine",
    "JAMA psychiatry",
    "Lancet (London, England)",
    "The lancet. Psychiatry",
    "BMJ (Clinical research ed.)",
    "Annals of internal medicine",
    "Addiction (Abingdon, England)",
    "Drug and alcohol dependence",
    "Journal of the American Geriatrics Society",
    "Obstetrics and gynecology",
    "Pediatrics",
    # Common abbreviations (PubMed "source" field)
    "N Engl J Med",
    "Lancet",
    "Lancet Psychiatry",
    "BMJ",
    "Ann Intern Med",
    "Addiction",
    "Drug Alcohol Depend",
    "J Am Geriatr Soc",
    "Obstet Gynecol",
)


def load_allowlist(path: str | Path | None = None) -> tuple[str, ...]:
    """Load a journal allowlist from a JSON array file, or the default."""
    if path is None:
        return DEFAULT_CURATED_JOURNALS
    data = json.loads(Path(path).read_text())
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise ValueError("journal allowlist file must be a JSON array of strings")
    return tuple(data)
