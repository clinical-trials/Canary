"""Minimal FHIR R4 REST client — read-only, least-privilege.

Only the four resource types the v1 scopes allow: Patient, Condition,
MedicationRequest, Observation.
"""
from __future__ import annotations

import httpx


class FHIRClient:
    def __init__(self, base_url: str, access_token: str, http: httpx.Client):
        self._base = base_url.rstrip("/")
        self._http = http
        self._headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
        }

    def _get(self, path: str, params: dict | None = None) -> dict:
        resp = self._http.get(
            f"{self._base}/{path}", params=params, headers=self._headers
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _entries(bundle: dict) -> list[dict]:
        return [
            e["resource"]
            for e in bundle.get("entry", [])
            if "resource" in e
        ]

    def patient(self, patient_id: str) -> dict:
        return self._get(f"Patient/{patient_id}")

    def conditions(self, patient_id: str) -> list[dict]:
        return self._entries(self._get("Condition", {"patient": patient_id}))

    def medication_requests(self, patient_id: str) -> list[dict]:
        return self._entries(self._get("MedicationRequest", {"patient": patient_id}))

    def lab_observations(self, patient_id: str) -> list[dict]:
        return self._entries(
            self._get("Observation", {"patient": patient_id, "category": "laboratory"})
        )
