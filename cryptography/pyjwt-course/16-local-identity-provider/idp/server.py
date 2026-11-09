"""
idp.server — a local OAuth2 + OpenID Connect provider (FastAPI ``app``)
======================================================================

This is a *small but realistic* identity provider that runs entirely on your
machine. It implements the endpoints a real OIDC provider exposes and that the
rest of the course validates against:

    GET  /.well-known/openid-configuration   discovery document
    GET  /jwks.json                          public signing keys (JWKS)
    GET  /authorize                          authorization-code endpoint
    POST /token                              code -> tokens, refresh -> tokens
    GET  /userinfo                           claims for a valid access token

Design choices (kept deliberately simple, but shaped like production):

* All tokens are signed **RS256** with the IdP's private key, and the signing
  key's ``kid`` is placed in the JWT header so clients can pick the right key
  from the JWKS. (See ``idp.keys``.)
* The **access_token** is a JWT for the resource API (audience ``AUDIENCE``)
  carrying ``iss/aud/sub/exp/iat/scope`` — this is what ``/userinfo`` and the
  ``04_validate_with_jwks.py`` demo verify.
* The **id_token** is the OIDC identity JWT for the *client* (audience =
  ``client_id``) carrying ``nonce/email/name`` — proving who logged in.
* A **refresh_token** is an opaque random string stored in memory and swapped
  for fresh access tokens at ``/token``.
* Users and clients live in tiny in-memory registries. ``/authorize`` does an
  auto-login as a chosen user (a real provider would show a login screen).

Run it live with uvicorn (see this module's README), or drive it in-process
with ``fastapi.testclient.TestClient`` (what every numbered lesson script does).
"""

from __future__ import annotations

import secrets
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import jwt
from fastapi import FastAPI, Form, Header, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse

from idp.keys import KeyManager

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------
# The issuer is the IdP's identity. It is a FIXED string baked into every token
# (the ``iss`` claim) regardless of how the app is reached (uvicorn on :9000 or
# TestClient's http://testserver). Clients pin this exact value when validating.
ISSUER = "http://localhost:9000"

# The audience of ACCESS tokens: the resource API they are meant for. A resource
# server validates ``aud == AUDIENCE``. (id_tokens instead use aud == client_id.)
AUDIENCE = "api://local-resource"

ACCESS_TOKEN_TTL = timedelta(minutes=15)
ID_TOKEN_TTL = timedelta(minutes=15)
AUTH_CODE_TTL = timedelta(minutes=5)

# The IdP's signing keys (current + next), published as a JWKS. A single shared
# manager instance backs the whole app so rotation demos can mutate it live.
keys = KeyManager()

# ---------------------------------------------------------------------------
# In-memory registries (a real IdP uses a database / directory)
# ---------------------------------------------------------------------------
CLIENTS: dict[str, dict] = {
    "local-web-app": {
        "client_secret": "local-web-app-secret",
        "redirect_uris": ["http://localhost:8443/callback"],
    }
}

USERS: dict[str, dict] = {
    "alice": {
        "sub": "user-alice-0001",
        "email": "alice@local.test",
        "name": "Alice Liddell",
        "roles": ["reader", "writer"],
        "scopes": ["openid", "profile", "email", "api.read", "api.write"],
    }
}

# Short-lived authorization codes: code -> grant context.
AUTH_CODES: dict[str, dict] = {}
# Opaque refresh tokens: token -> grant context.
REFRESH_TOKENS: dict[str, dict] = {}

SUPPORTED_SCOPES = ["openid", "profile", "email", "api.read", "api.write"]

app = FastAPI(title="Local OIDC Identity Provider", version="1.0.0")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now() -> datetime:
    """Timezone-aware 'now' (UTC) — never use naive datetimes for JWT claims."""
    return datetime.now(UTC)


def _purge_expired_codes() -> None:
    """Drop auth codes whose short TTL has elapsed (housekeeping)."""
    now = time.time()
    for code in [c for c, g in AUTH_CODES.items() if g["expires_at"] < now]:
        AUTH_CODES.pop(code, None)


def _make_access_token(user: dict, scope: str) -> str:
    """Mint an RS256 access token (a JWT) for the resource API."""
    now = _now()
    signer = keys.signing_key
    return jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": user["sub"],
            "scope": scope,
            "roles": user["roles"],
            "jti": secrets.token_urlsafe(12),  # unique id -> every token differs
            "iat": now,
            "nbf": now,
            "exp": now + ACCESS_TOKEN_TTL,
        },
        signer.private_key,
        algorithm="RS256",
        headers={"kid": signer.kid},
    )


def _make_id_token(user: dict, client_id: str, nonce: str | None) -> str:
    """Mint an RS256 OIDC id_token for the client that initiated login."""
    now = _now()
    signer = keys.signing_key
    claims = {
        "iss": ISSUER,
        "aud": client_id,  # id_token audience is the CLIENT, not the API
        "sub": user["sub"],
        "email": user["email"],
        "name": user["name"],
        "iat": now,
        "exp": now + ID_TOKEN_TTL,
    }
    if nonce is not None:
        claims["nonce"] = nonce  # round-tripped to defeat replay
    return jwt.encode(
        claims,
        signer.private_key,
        algorithm="RS256",
        headers={"kid": signer.kid},
    )


def _issue_tokens(grant: dict, *, include_id_token: bool) -> dict:
    """Build the full token response for a granted login."""
    user = USERS[grant["username"]]
    scope = grant["scope"]
    access_token = _make_access_token(user, scope)

    refresh_token = secrets.token_urlsafe(32)
    REFRESH_TOKENS[refresh_token] = {
        "username": grant["username"],
        "client_id": grant["client_id"],
        "scope": scope,
    }

    body = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": int(ACCESS_TOKEN_TTL.total_seconds()),
        "refresh_token": refresh_token,
        "scope": scope,
    }
    if include_id_token and "openid" in scope.split():
        body["id_token"] = _make_id_token(
            user, grant["client_id"], grant.get("nonce")
        )
    return body


# ---------------------------------------------------------------------------
# OIDC endpoints
# ---------------------------------------------------------------------------
@app.get("/.well-known/openid-configuration")
def discovery() -> dict:
    """OIDC discovery document — the provider's machine-readable manifest.

    Clients fetch this first to learn every endpoint URL and capability,
    instead of hard-coding them. Mirrors Azure/Google's same-named document.
    """
    return {
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/authorize",
        "token_endpoint": f"{ISSUER}/token",
        "userinfo_endpoint": f"{ISSUER}/userinfo",
        "jwks_uri": f"{ISSUER}/jwks.json",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "scopes_supported": SUPPORTED_SCOPES,
        "claims_supported": [
            "iss", "aud", "sub", "exp", "iat", "nbf",
            "email", "name", "roles", "scope", "nonce",
        ],
    }


@app.get("/jwks.json")
def jwks() -> dict:
    """Public JWKS — the IdP's verification keys (NEVER the private keys)."""
    return keys.jwks()


@app.get("/authorize")
def authorize(
    response_type: str = Query("code"),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query("openid profile email"),
    state: str | None = Query(None),
    nonce: str | None = Query(None),
    username: str = Query("alice"),  # auto-login; real IdP shows a login UI
    response_mode: str = Query("query"),  # "query" -> redirect, "json" -> body
):
    """Authorization-code endpoint: authenticate the user, mint a code.

    Validates the client, redirect URI, response_type and scope, then stores a
    short-lived authorization ``code`` bound to (client, user, scope, nonce).
    With ``response_mode=query`` it 302-redirects back to ``redirect_uri`` with
    ``?code=...&state=...`` (browser flow). With ``response_mode=json`` it
    returns the code as JSON — convenient for the in-process test client.
    """
    _purge_expired_codes()

    if response_type != "code":
        raise HTTPException(400, "unsupported_response_type")
    client = CLIENTS.get(client_id)
    if client is None:
        raise HTTPException(400, "unknown client_id")
    if redirect_uri not in client["redirect_uris"]:
        raise HTTPException(400, "invalid redirect_uri")
    if username not in USERS:
        raise HTTPException(400, "unknown user")

    granted = [s for s in scope.split() if s in SUPPORTED_SCOPES]
    if not granted:
        raise HTTPException(400, "invalid_scope")
    granted_scope = " ".join(granted)

    code = secrets.token_urlsafe(24)
    AUTH_CODES[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "username": username,
        "scope": granted_scope,
        "nonce": nonce,
        "expires_at": time.time() + AUTH_CODE_TTL.total_seconds(),
    }

    if response_mode == "json":
        return JSONResponse({"code": code, "state": state})

    params = {"code": code}
    if state is not None:
        params["state"] = state
    return RedirectResponse(
        url=f"{redirect_uri}?{urlencode(params)}", status_code=302
    )


@app.post("/token")
def token(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code: str | None = Form(None),
    redirect_uri: str | None = Form(None),
    refresh_token: str | None = Form(None),
):
    """Token endpoint: exchange a code OR a refresh_token for fresh tokens.

    Confidential clients authenticate with ``client_id`` + ``client_secret``.
    ``authorization_code`` returns access_token + id_token + refresh_token;
    ``refresh_token`` returns a brand-new access_token (and id_token).
    """
    client = CLIENTS.get(client_id)
    if client is None or not secrets.compare_digest(
        client["client_secret"], client_secret or ""
    ):
        raise HTTPException(401, "invalid_client")

    if grant_type == "authorization_code":
        _purge_expired_codes()
        grant = AUTH_CODES.pop(code or "", None)  # single-use: pop it
        if grant is None:
            raise HTTPException(400, "invalid_grant: bad or expired code")
        if grant["client_id"] != client_id:
            raise HTTPException(400, "invalid_grant: client mismatch")
        if grant["redirect_uri"] != redirect_uri:
            raise HTTPException(400, "invalid_grant: redirect_uri mismatch")
        return _issue_tokens(grant, include_id_token=True)

    if grant_type == "refresh_token":
        grant = REFRESH_TOKENS.pop(refresh_token or "", None)  # rotate it
        if grant is None:
            raise HTTPException(400, "invalid_grant: unknown refresh_token")
        if grant["client_id"] != client_id:
            raise HTTPException(400, "invalid_grant: client mismatch")
        return _issue_tokens(grant, include_id_token=True)

    raise HTTPException(400, "unsupported_grant_type")


@app.get("/userinfo")
def userinfo(authorization: str | None = Header(None)) -> dict:
    """Return identity claims for the bearer of a valid access token.

    Validates the access token the SAME way any resource server would: read the
    ``kid`` from the header, pick the key from our JWKS, then RS256-verify with
    the issuer + audience pinned.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    access_token = authorization.removeprefix("Bearer ").strip()

    try:
        kid = jwt.get_unverified_header(access_token).get("kid")
        signer = keys.get_published_key(kid)
        if signer is None:
            raise jwt.InvalidKeyError(f"unknown kid {kid!r}")
        claims = jwt.decode(
            access_token,
            signer.public_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(401, f"invalid_token: {exc}") from exc

    user = next((u for u in USERS.values() if u["sub"] == claims["sub"]), None)
    if user is None:
        raise HTTPException(401, "unknown subject")

    return {
        "sub": user["sub"],
        "email": user["email"],
        "name": user["name"],
        "roles": user["roles"],
        "scope": claims.get("scope", ""),
    }
