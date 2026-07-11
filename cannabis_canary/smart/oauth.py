"""SMART App Launch OAuth2 plumbing (RFC 6749 + RFC 7636 PKCE).

Tokens live server-side only (BFF pattern): nothing in this module ever hands
an access token to the browser.
"""
from __future__ import annotations

import base64
import hashlib
import secrets
import urllib.parse
from dataclasses import dataclass

import httpx


def fetch_smart_configuration(iss: str, http: httpx.Client) -> dict:
    """SMART discovery: GET {iss}/.well-known/smart-configuration."""
    resp = http.get(f"{iss.rstrip('/')}/.well-known/smart-configuration")
    resp.raise_for_status()
    return resp.json()


def make_pkce() -> tuple[str, str]:
    """RFC 7636 S256: return (code_verifier, code_challenge)."""
    verifier = secrets.token_urlsafe(64)[:100]
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    return verifier, challenge


def build_authorize_url(
    authorize_endpoint: str,
    client_id: str,
    redirect_uri: str,
    scopes: str,
    state: str,
    aud: str,
    code_challenge: str,
    launch: str | None = None,
) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
        "aud": aud,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if launch is not None:
        params["launch"] = launch
    return f"{authorize_endpoint}?{urllib.parse.urlencode(params)}"


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    token_type: str
    expires_in: int | None = None
    scope: str | None = None
    patient: str | None = None
    id_token: str | None = None
    fhir_user: str | None = None


def exchange_code(
    token_endpoint: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str | None,
    code_verifier: str,
    http: httpx.Client,
) -> TokenResponse:
    """Authorization-code exchange.

    Confidential client (client_secret set): HTTP Basic auth per RFC 6749 §2.3.1.
    Public client: client_id goes in the body, PKCE carries the proof.
    """
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    headers = {}
    if client_secret is not None:
        credentials = base64.b64encode(
            f"{client_id}:{client_secret}".encode()
        ).decode()
        headers["Authorization"] = f"Basic {credentials}"
    else:
        body["client_id"] = client_id

    resp = http.post(token_endpoint, data=body, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return TokenResponse(
        access_token=data["access_token"],
        token_type=data.get("token_type", "Bearer"),
        expires_in=data.get("expires_in"),
        scope=data.get("scope"),
        patient=data.get("patient"),
        id_token=data.get("id_token"),
        fhir_user=data.get("fhirUser"),
    )
