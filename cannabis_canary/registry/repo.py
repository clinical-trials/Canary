"""Repository layer — the only place that reads/writes registry tables."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from cannabis_canary.instrument import CannabisHistory, to_questionnaire_response
from cannabis_canary.registry.models import AuditEvent, CannabisHistoryRecord


class RegistryRepo:
    def __init__(self, session: Session):
        self._session = session

    def save_history(
        self,
        patient_id: str,
        author_id: str,
        history: CannabisHistory,
        authored_at: datetime,
    ) -> CannabisHistoryRecord:
        record = CannabisHistoryRecord(
            patient_id=patient_id,
            author_id=author_id,
            authored_at=authored_at,
            exposure_status=history.exposure_status,
            thc_mg_per_day=history.thc_mg_per_day,
            response_json=to_questionnaire_response(
                history,
                authored=authored_at.isoformat(),
                subject_ref=f"Patient/{patient_id}",
            ),
        )
        self._session.add(record)
        self._session.commit()
        return record

    def list_for_patient(self, patient_id: str) -> list[CannabisHistoryRecord]:
        stmt = (
            select(CannabisHistoryRecord)
            .where(CannabisHistoryRecord.patient_id == patient_id)
            .order_by(CannabisHistoryRecord.authored_at)
        )
        return list(self._session.scalars(stmt))

    def latest_for_patient(self, patient_id: str) -> CannabisHistoryRecord | None:
        rows = self.list_for_patient(patient_id)
        return rows[-1] if rows else None

    def trend_points(self, patient_id: str) -> list[tuple[datetime, float]]:
        """(authored_at, thc_mg_per_day) for records that have a computed dose."""
        return [
            (r.authored_at, r.thc_mg_per_day)
            for r in self.list_for_patient(patient_id)
            if r.thc_mg_per_day is not None
        ]

    def record_audit(
        self,
        actor: str,
        action: str,
        patient_id: str,
        detail: str | None = None,
    ) -> None:
        self._session.add(
            AuditEvent(actor=actor, action=action, patient_id=patient_id, detail=detail)
        )
        self._session.commit()

    def audit_for_patient(self, patient_id: str) -> list[AuditEvent]:
        stmt = (
            select(AuditEvent)
            .where(AuditEvent.patient_id == patient_id)
            .order_by(AuditEvent.at, AuditEvent.id)
        )
        return list(self._session.scalars(stmt))
