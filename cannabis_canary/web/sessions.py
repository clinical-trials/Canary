"""Server-side sessions: opaque random cookie -> server-held dict.

Access tokens NEVER leave the server (BFF requirement). In-memory store is for
dev/tests and single-process deployments; production should swap in Redis or a
DB-backed store behind the same three methods.
"""
from __future__ import annotations

import secrets

COOKIE_NAME = "cc_sid"


class MemorySessionStore:
    def __init__(self) -> None:
        self._data: dict[str, dict] = {}

    def create(self) -> tuple[str, dict]:
        sid = secrets.token_urlsafe(32)
        session: dict = {}
        self._data[sid] = session
        return sid, session

    def get(self, sid: str | None) -> dict | None:
        if sid is None:
            return None
        return self._data.get(sid)

    def destroy(self, sid: str) -> None:
        self._data.pop(sid, None)
