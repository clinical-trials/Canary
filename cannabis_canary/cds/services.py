"""CDS Hooks discovery + patient-view card.

The EHR calls the patient-view hook when a chart is opened; our card offers
to launch the Cannabis Canary© social-history form via a standard SMART link
(the EHR appends iss/launch when the provider clicks). This is the standards-
based realization of the proposal's "checkbox = yes → form opens" trigger.
"""
from __future__ import annotations

SERVICE_ID = "cannabis-canary-social-history"


def discovery() -> dict:
    return {
        "services": [
            {
                "hook": "patient-view",
                "id": SERVICE_ID,
                "title": "Cannabis Canary© — cannabis social history",
                "description": (
                    "Offers a structured cannabis social-history form with a "
                    "THC mg/day dosage calculator and point-of-care decision "
                    "support for documented contraindications."
                ),
                "prefetch": {"patient": "Patient/{{context.patientId}}"},
            }
        ]
    }


def patient_view_cards(app_base_url: str) -> list[dict]:
    return [
        {
            "summary": "Take a structured cannabis social history",
            "indicator": "info",
            "source": {"label": "Cannabis Canary©"},
            "links": [
                {
                    "label": "Open Cannabis Canary©",
                    "url": f"{app_base_url.rstrip('/')}/launch",
                    "type": "smart",
                }
            ],
        }
    ]
