from cannabis_canary.cds import (
    CONTRAINDICATION_TOPICS,
    contraindication_cards,
    discovery,
    patient_view_cards,
)


def test_discovery_lists_patient_view_service():
    doc = discovery()
    services = doc["services"]
    assert len(services) == 1
    svc = services[0]
    assert svc["hook"] == "patient-view"
    assert svc["id"] == "cannabis-canary-social-history"
    assert "prefetch" in svc


def test_patient_view_card_links_to_smart_launch():
    cards = patient_view_cards(app_base_url="https://canary.example.org")
    assert len(cards) == 1
    card = cards[0]
    assert card["indicator"] == "info"
    assert card["source"]["label"].startswith("Cannabis Canary")
    link = card["links"][0]
    assert link["type"] == "smart"
    assert link["url"] == "https://canary.example.org/launch"


def test_contraindication_topics_cover_spec():
    assert set(CONTRAINDICATION_TOPICS) == {
        "hyperemesis", "reproductive", "schizoaffective",
    }


def test_contraindication_cards_have_guidance_and_pubmed_link():
    cards = contraindication_cards(["hyperemesis", "schizoaffective"])
    assert len(cards) == 2
    for card in cards:
        assert card["indicator"] == "warning"
        assert card["summary"]
        assert card["detail"]
        link = card["links"][0]
        assert link["type"] == "absolute"
        assert link["url"].startswith("https://pubmed.ncbi.nlm.nih.gov/?term=")


def test_unknown_topic_ignored():
    assert contraindication_cards(["unknown-topic"]) == []
