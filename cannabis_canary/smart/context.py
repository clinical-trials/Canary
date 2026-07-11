"""PHI boundary: reduce raw FHIR resources to the de-identified context the
rest of the app needs (sex, birth year, problem names, urine-drug-screen hits).

Nothing produced here carries names, MRNs, or FHIR ids — this is what may
cross into the analysis/evidence side.
"""
from __future__ import annotations

from dataclasses import dataclass

_UDS_MARKERS = ("cannabinoid", "cannabis", "thc", "drug screen", "drugs of abuse")


@dataclass(frozen=True)
class UdsResult:
    display: str
    value: str | None
    effective: str | None


@dataclass(frozen=True)
class PatientContext:
    sex: str | None
    birth_year: int | None
    problems: tuple[str, ...]
    uds_results: tuple[UdsResult, ...]


def _code_text(resource: dict) -> str:
    code = resource.get("code", {})
    if code.get("text"):
        return code["text"]
    for coding in code.get("coding", []):
        if coding.get("display"):
            return coding["display"]
    return ""


def _observation_value(obs: dict) -> str | None:
    if "valueString" in obs:
        return obs["valueString"]
    if "valueCodeableConcept" in obs:
        return obs["valueCodeableConcept"].get("text")
    if "valueQuantity" in obs:
        q = obs["valueQuantity"]
        value, unit = q.get("value"), q.get("unit", "")
        return f"{value} {unit}".strip() if value is not None else None
    return None


def extract_context(
    patient: dict,
    conditions: list[dict],
    observations: list[dict],
) -> PatientContext:
    birth_date = patient.get("birthDate")
    birth_year = int(birth_date[:4]) if birth_date else None

    problems = tuple(t for t in (_code_text(c) for c in conditions) if t)

    uds = tuple(
        UdsResult(
            display=_code_text(o),
            value=_observation_value(o),
            effective=o.get("effectiveDateTime"),
        )
        for o in observations
        if any(m in _code_text(o).lower() for m in _UDS_MARKERS)
    )

    return PatientContext(
        sex=patient.get("gender"),
        birth_year=birth_year,
        problems=problems,
        uds_results=uds,
    )
