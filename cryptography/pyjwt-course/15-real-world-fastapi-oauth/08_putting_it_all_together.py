"""
08 · Capstone — the full request auth lifecycle, end to end
===========================================================

This ties the whole course together. We follow one realistic request through
every stage of a token's life:

    MINT  -> TRANSMIT -> RECEIVE -> VERIFY -> AUTHORIZE -> SERVE

* **Mint**      — the auth server issues an RS256 access token with realistic
  claims (iss, sub, aud, exp, scope, roles) and a ``kid`` header.
* **Transmit**  — the client sends it as an ``Authorization: Bearer <token>``
  header string (we literally build that header line).
* **Receive**   — the API extracts the raw token from the header.
* **Verify**    — the API selects the key by ``kid`` from its JWKS and validates
  signature + iss + aud + exp.
* **Authorize** — the API checks the required scope/role for the endpoint.
* **Serve**     — only now does it return data.

Every stage prints what it did, so you can watch trust being established.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/15-real-world-fastapi-oauth/08_putting_it_all_together.py
"""

import json
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"
KID = "auth-key-2026-06"


class AuthError(Exception):
    """401 — token missing/invalid."""


class PermissionDenied(Exception):
    """403 — valid token but insufficient scope/role."""


# --------------------------------------------------------------------------
# AUTH SERVER
# --------------------------------------------------------------------------
def auth_server_mint(private_pem: str, subject: str, scope: str, roles: list[str]) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": ISSUER,
            "sub": subject,
            "aud": AUDIENCE,
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=15),
            "scope": scope,
            "roles": roles,
        },
        private_pem,
        algorithm="RS256",
        headers={"kid": KID},
    )


# --------------------------------------------------------------------------
# RESOURCE SERVER (API)
# --------------------------------------------------------------------------
def extract_bearer(authorization_header: str) -> str:
    scheme, _, token = authorization_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError("malformed Authorization header")
    return token


def select_key(jwks: dict, token: str):
    kid = jwt.get_unverified_header(token)["kid"]
    for key in jwt.PyJWKSet.from_dict(jwks).keys:
        if key.key_id == kid:
            return key.key
    raise AuthError(f"unknown kid {kid!r}")


def verify(token: str, jwks: dict) -> dict:
    try:
        return jwt.decode(
            token,
            select_key(jwks, token),
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except jwt.InvalidTokenError as exc:
        raise AuthError(f"token verification failed: {exc}") from exc


def authorize(claims: dict, *, scope: str, role: str) -> None:
    if scope not in set(claims.get("scope", "").split()):
        raise PermissionDenied(f"missing scope {scope!r}")
    if role not in claims.get("roles", []):
        raise PermissionDenied(f"missing role {role!r}")


def handle_request(authorization_header: str, jwks: dict) -> dict:
    """The API endpoint: the full receive->verify->authorize->serve pipeline."""
    token = extract_bearer(authorization_header)
    print(f"  [RECEIVE]   extracted token: {token[:32]}...")
    claims = verify(token, jwks)
    print(f"  [VERIFY]    signature+iss+aud+exp OK; sub={claims['sub']}")
    authorize(claims, scope="write:reports", role="editor")
    print(f"  [AUTHORIZE] scope+role OK ({claims['scope']!r}, {claims['roles']})")
    return {"report_id": 42, "status": "created", "owner": claims["sub"]}


def main() -> None:
    # Provider key + JWKS (the API knows the public keys, not the private one).
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    jwk = json.loads(RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update({"kid": KID, "use": "sig", "alg": "RS256"})
    jwks = {"keys": [jwk]}

    print("=" * 72)
    print("SCENARIO A — an EDITOR creates a report (happy path)")
    print("=" * 72)
    print("[MINT]      auth server issues token for editor 'alice'")
    token = auth_server_mint(private_pem, "alice", "profile write:reports", ["editor"])
    header_line = f"Authorization: Bearer {token}"
    print(f"[TRANSMIT]  client sends header: {header_line[:48]}...")
    result = handle_request(header_line.removeprefix("Authorization: "), jwks)
    print(f"  [SERVE]     200 OK -> {result}\n")

    print("=" * 72)
    print("SCENARIO B — a READER tries to create a report (403)")
    print("=" * 72)
    print("[MINT]      auth server issues token for reader 'bob'")
    bob = auth_server_mint(private_pem, "bob", "profile read:reports", ["viewer"])
    try:
        handle_request(f"Bearer {bob}", jwks)
    except PermissionDenied as exc:
        print(f"  [AUTHORIZE] 403 Forbidden -> {exc}\n")

    print("=" * 72)
    print("SCENARIO C — a forged/garbage token (401)")
    print("=" * 72)
    try:
        handle_request("Bearer not.a.realtoken", jwks)
    except AuthError as exc:
        print(f"  [VERIFY]    401 Unauthorized -> {exc}\n")

    print("=" * 72)
    print("LIFECYCLE: mint -> transmit -> receive -> verify -> authorize -> serve")
    print("Identity (verify) and permission (authorize) are SEPARATE gates. You")
    print("passed both only in Scenario A. That is production JWT auth in full.")
    print("=" * 72)


if __name__ == "__main__":
    main()
