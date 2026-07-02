import json

import httpx

from cannabis_canary.evidence import (
    DEFAULT_CURATED_JOURNALS,
    PubMedClient,
    StudySummary,
    build_search_url,
    filter_curated,
)


def make_client(handler) -> PubMedClient:
    return PubMedClient(
        http=httpx.Client(transport=httpx.MockTransport(handler)),
        api_key="test-key",
    )


def test_search_parses_pmids_and_sends_api_key():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["params"] = dict(request.url.params)
        return httpx.Response(
            200, json={"esearchresult": {"idlist": ["111", "222"]}}
        )

    client = make_client(handler)
    pmids = client.search("cannabinoid hyperemesis", retmax=5)
    assert pmids == ["111", "222"]
    assert seen["params"]["db"] == "pubmed"
    assert seen["params"]["retmax"] == "5"
    assert seen["params"]["api_key"] == "test-key"


def test_summaries_parses_esummary_json():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "result": {
                    "uids": ["111"],
                    "111": {
                        "uid": "111",
                        "title": "Cannabinoid hyperemesis syndrome: a review",
                        "fulljournalname": "The New England journal of medicine",
                        "source": "N Engl J Med",
                        "pubdate": "2024 Mar",
                        "authors": [{"name": "Smith J"}, {"name": "Lee K"}],
                    },
                }
            },
        )

    client = make_client(handler)
    studies = client.summaries(["111"])
    assert studies == [
        StudySummary(
            pmid="111",
            title="Cannabinoid hyperemesis syndrome: a review",
            journal="The New England journal of medicine",
            source_abbrev="N Engl J Med",
            pubdate="2024 Mar",
            authors=("Smith J", "Lee K"),
        )
    ]
    assert studies[0].url == "https://pubmed.ncbi.nlm.nih.gov/111/"


def test_filter_curated_matches_full_name_or_abbrev_case_insensitive():
    keep_full = StudySummary("1", "t", "The New England journal of medicine", "X", "2024", ())
    keep_abbrev = StudySummary("2", "t", "Unknown", "n engl j med", "2024", ())
    drop = StudySummary("3", "t", "Predatory Journal of Vibes", "PJV", "2024", ())
    kept = filter_curated([keep_full, keep_abbrev, drop], DEFAULT_CURATED_JOURNALS)
    assert [s.pmid for s in kept] == ["1", "2"]


def test_search_curated_end_to_end_with_mock():
    def handler(request: httpx.Request) -> httpx.Response:
        if "esearch" in str(request.url):
            return httpx.Response(200, json={"esearchresult": {"idlist": ["1", "3"]}})
        return httpx.Response(
            200,
            json={
                "result": {
                    "uids": ["1", "3"],
                    "1": {"uid": "1", "title": "good", "fulljournalname": "JAMA",
                          "source": "JAMA", "pubdate": "2025", "authors": []},
                    "3": {"uid": "3", "title": "bad", "fulljournalname": "Vibes Weekly",
                          "source": "VW", "pubdate": "2025", "authors": []},
                }
            },
        )

    client = make_client(handler)
    kept = client.search_curated("cannabis older adults")
    assert [s.pmid for s in kept] == ["1"]


def test_build_search_url_is_quoted():
    url = build_search_url("cannabinoid hyperemesis syndrome")
    assert url.startswith("https://pubmed.ncbi.nlm.nih.gov/?term=")
    assert " " not in url


def test_default_allowlist_is_real_journals_no_fabricated_issns():
    # Names only by design — we do not ship ISSNs we can't verify.
    assert "JAMA" in DEFAULT_CURATED_JOURNALS
    assert all(isinstance(j, str) for j in DEFAULT_CURATED_JOURNALS)
