"""Registry — the secured store for prospectively captured cannabis histories.

This is the PHI custodian side of Cannabis Canary© ("Option 2" in the spec):
identifiable data lives HERE, never in the analysis/evidence engine and never
in outbound PubMed queries. Encryption at rest and TLS are deployment
requirements (see docs/epic-submission-checklist.md); every access is audited.
"""
from cannabis_canary.registry.db import create_session_factory, init_db
from cannabis_canary.registry.models import AuditEvent, CannabisHistoryRecord
from cannabis_canary.registry.repo import RegistryRepo

__all__ = [
    "create_session_factory",
    "init_db",
    "AuditEvent",
    "CannabisHistoryRecord",
    "RegistryRepo",
]
