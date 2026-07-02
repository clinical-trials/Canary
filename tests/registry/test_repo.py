from datetime import datetime, timezone

import pytest

from cannabis_canary.instrument import parse_history
from cannabis_canary.registry import RegistryRepo, create_session_factory, init_db


@pytest.fixture()
def repo():
    factory, engine = create_session_factory("sqlite+pysqlite:///:memory:")
    init_db(engine)
    with factory() as session:
        yield RegistryRepo(session)


def make_history(grams=1.0, pct=10.0):
    return parse_history(
        {
            "exposure_status": "current-every-day",
            "dose_mode": "concentration",
            "grams_per_day": grams,
            "percent_thc": pct,
        }
    )


def test_save_and_list_history(repo):
    when = datetime(2026, 6, 29, 12, 0, tzinfo=timezone.utc)
    rec = repo.save_history(
        patient_id="pat-1", author_id="Practitioner/doc-9",
        history=make_history(), authored_at=when,
    )
    assert rec.id
    assert rec.thc_mg_per_day == 100.0

    rows = repo.list_for_patient("pat-1")
    assert len(rows) == 1
    assert rows[0].exposure_status == "current-every-day"
    assert rows[0].response_json["resourceType"] == "QuestionnaireResponse"
    assert repo.list_for_patient("someone-else") == []


def test_trend_points_ordered(repo):
    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 6, 1, tzinfo=timezone.utc)
    repo.save_history("pat-1", "doc", make_history(grams=2.0), authored_at=t2)
    repo.save_history("pat-1", "doc", make_history(grams=1.0), authored_at=t1)
    points = repo.trend_points("pat-1")
    assert [round(v) for _, v in points] == [100, 200]
    assert points[0][0] < points[1][0]


def test_latest_review_tracking(repo):
    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    repo.save_history("pat-1", "doc", make_history(), authored_at=t1)
    latest = repo.latest_for_patient("pat-1")
    assert latest is not None
    assert latest.authored_at.date().isoformat() == "2026-01-01"
    assert repo.latest_for_patient("nobody") is None


def test_audit_log(repo):
    repo.record_audit(actor="Practitioner/doc-9", action="view", patient_id="pat-1")
    repo.record_audit(actor="Practitioner/doc-9", action="capture", patient_id="pat-1")
    events = repo.audit_for_patient("pat-1")
    assert [e.action for e in events] == ["view", "capture"]
    assert all(e.at is not None for e in events)
