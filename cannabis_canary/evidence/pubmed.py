"""NCBI E-utilities client (esearch + esummary) with curated-journal filtering.

Rate-limit aware: pass an NCBI api_key to raise the request allowance; callers
should treat failures as non-blocking (the app must never hard-depend on
PubMed availability).
"""
from __future__ import annotations

import urllib.parse
from dataclasses import dataclass

import httpx

from cannabis_canary.evidence.journals import DEFAULT_CURATED_JOURNALS

_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


@dataclass(frozen=True)
class StudySummary:
    pmid: str
    title: str
    journal: str
    source_abbrev: str
    pubdate: str
    authors: tuple[str, ...]

    @property
    def url(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


def build_search_url(term: str) -> str:
    """Human-facing PubMed search link (used in decision-support cards)."""
    return "https://pubmed.ncbi.nlm.nih.gov/?term=" + urllib.parse.quote(term)


def filter_curated(
    studies: list[StudySummary],
    allowlist: tuple[str, ...] = DEFAULT_CURATED_JOURNALS,
) -> list[StudySummary]:
    allowed = {j.lower() for j in allowlist}
    return [
        s
        for s in studies
        if s.journal.lower() in allowed or s.source_abbrev.lower() in allowed
    ]


class PubMedClient:
    def __init__(
        self,
        http: httpx.Client,
        api_key: str | None = None,
        allowlist: tuple[str, ...] = DEFAULT_CURATED_JOURNALS,
    ):
        self._http = http
        self._api_key = api_key
        self._allowlist = allowlist

    def _params(self, **params) -> dict:
        params["retmode"] = "json"
        if self._api_key:
            params["api_key"] = self._api_key
        return params

    def search(self, term: str, retmax: int = 20) -> list[str]:
        resp = self._http.get(
            f"{_EUTILS}/esearch.fcgi",
            params=self._params(db="pubmed", term=term, retmax=retmax),
        )
        resp.raise_for_status()
        return list(resp.json()["esearchresult"].get("idlist", []))

    def summaries(self, pmids: list[str]) -> list[StudySummary]:
        if not pmids:
            return []
        resp = self._http.get(
            f"{_EUTILS}/esummary.fcgi",
            params=self._params(db="pubmed", id=",".join(pmids)),
        )
        resp.raise_for_status()
        result = resp.json()["result"]
        studies = []
        for uid in result.get("uids", []):
            row = result[uid]
            studies.append(
                StudySummary(
                    pmid=uid,
                    title=row.get("title", ""),
                    journal=row.get("fulljournalname", ""),
                    source_abbrev=row.get("source", ""),
                    pubdate=row.get("pubdate", ""),
                    authors=tuple(a.get("name", "") for a in row.get("authors", [])),
                )
            )
        return studies

    def search_curated(self, term: str, retmax: int = 20) -> list[StudySummary]:
        """Live PubMed search screened to the curated journal allowlist."""
        return filter_curated(
            self.summaries(self.search(term, retmax=retmax)), self._allowlist
        )
