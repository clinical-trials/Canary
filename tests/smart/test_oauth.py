import base64
import hashlib
from urllib.parse import parse_qs, urlparse

import httpx

from cannabis_canary.smart.oauth import (
    build_authorize_url,
    exchange_code,
    fetch_smart_configuration,
    make_pkce,
)

SMART_CONFIG = {
    "authorization_endpoint": "https://ehr.example.org/oauth2/authorize",
    "token_endpoint": "https://ehr.example.org/oauth2/token",
    "capabilities": ["launch-ehr", "client-confidential-symmetric"],
}


def test_fetch_smart_configuration_uses_well_known():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        return httpx.Response(200, json=SMART_CONFIG)

    http = httpx.Client(transport=httpx.MockTransport(handler))
    config = fetch_smart_configuration("https://fhir.example.org/r4", http)
    assert seen["url"] == "https://fhir.example.org/r4/.well-known/smart-configuration"
    assert config["token_endpoint"] == SMART_CONFIG["token_endpoint"]


def test_pkce_challenge_is_s256_of_verifier():
    verifier, challenge = make_pkce()
    expected = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    assert challenge == expected
    assert len(verifier) >= 43  # RFC 7636 minimum


def test_build_authorize_url_contains_required_smart_params():
    url = build_authorize_url(
        authorize_endpoint="https://ehr.example.org/oauth2/authorize",
        client_id="my-client",
        redirect_uri="https://app.example.org/callback",
        scopes="launch openid fhirUser patient/Patient.read",
        state="state123",
        aud="https://fhir.example.org/r4",
        code_challenge="challenge123",
        launch="launch-token",
    )
    q = parse_qs(urlparse(url).query)
    assert q["response_type"] == ["code"]
    assert q["client_id"] == ["my-client"]
    assert q["state"] == ["state123"]
    assert q["aud"] == ["https://fhir.example.org/r4"]
    assert q["code_challenge_method"] == ["S256"]
    assert q["launch"] == ["launch-token"]
    assert "launch" in q["scope"][0]


def test_exchange_code_posts_confidential_basic_auth_and_parses_token():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization", "")
        seen["body"] = parse_qs(request.content.decode())
        return httpx.Response(
            200,
            json={
                "access_token": "tok-abc",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "patient/Patient.read",
                "patient": "pat-42",
            },
        )

    http = httpx.Client(transport=httpx.MockTransport(handler))
    token = exchange_code(
        token_endpoint="https://ehr.example.org/oauth2/token",
        code="authcode",
        redirect_uri="https://app.example.org/callback",
        client_id="my-client",
        client_secret="s3cret",
        code_verifier="verifier",
        http=http,
    )
    assert token.access_token == "tok-abc"
    assert token.patient == "pat-42"
    assert token.expires_in == 3600
    expected_basic = base64.b64encode(b"my-client:s3cret").decode()
    assert seen["auth"] == f"Basic {expected_basic}"
    assert seen["body"]["grant_type"] == ["authorization_code"]
    assert seen["body"]["code_verifier"] == ["verifier"]
    assert "client_secret" not in seen["body"]


def test_exchange_code_public_client_sends_client_id_in_body():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = parse_qs(request.content.decode())
        return httpx.Response(200, json={"access_token": "t", "token_type": "Bearer"})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    exchange_code(
        token_endpoint="https://ehr.example.org/oauth2/token",
        code="c", redirect_uri="https://a/cb", client_id="pub-client",
        client_secret=None, code_verifier="v", http=http,
    )
    assert seen["auth"] is None
    assert seen["body"]["client_id"] == ["pub-client"]
