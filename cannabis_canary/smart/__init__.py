"""SMART App Launch (BFF confidential client) + FHIR R4 reads.

Standards-only: SMART discovery via .well-known/smart-configuration, OAuth2
authorization-code with PKCE, plain FHIR R4 REST reads. No vendor-proprietary
calls — the same code path serves Epic and Cerner/Oracle Health.
"""
from cannabis_canary.smart.context import PatientContext, UdsResult, extract_context
from cannabis_canary.smart.fhir_client import FHIRClient
from cannabis_canary.smart.oauth import (
    TokenResponse,
    build_authorize_url,
    exchange_code,
    fetch_smart_configuration,
    make_pkce,
)

__all__ = [
    "PatientContext",
    "UdsResult",
    "extract_context",
    "FHIRClient",
    "TokenResponse",
    "build_authorize_url",
    "exchange_code",
    "fetch_smart_configuration",
    "make_pkce",
]
