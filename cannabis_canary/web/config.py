"""App settings. All secrets/config come from environment variables — nothing
sensitive is ever committed."""
from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_SCOPES = (
    "launch openid fhirUser "
    "patient/Patient.read patient/Condition.read "
    "patient/MedicationRequest.read patient/Observation.read"
)


@dataclass(frozen=True)
class Settings:
    client_id: str
    redirect_uri: str
    app_base_url: str
    client_secret: str | None = None
    scopes: str = DEFAULT_SCOPES
    database_url: str = "sqlite+pysqlite:///./canary.db"
    ncbi_api_key: str | None = None
    review_interval_months: int = 3

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            client_id=os.environ["CANARY_CLIENT_ID"],
            client_secret=os.environ.get("CANARY_CLIENT_SECRET"),
            redirect_uri=os.environ["CANARY_REDIRECT_URI"],
            app_base_url=os.environ["CANARY_APP_BASE_URL"],
            scopes=os.environ.get("CANARY_SCOPES", DEFAULT_SCOPES),
            database_url=os.environ.get(
                "CANARY_DATABASE_URL", "sqlite+pysqlite:///./canary.db"
            ),
            ncbi_api_key=os.environ.get("NCBI_API_KEY"),
            review_interval_months=int(os.environ.get("CANARY_REVIEW_MONTHS", "3")),
        )
