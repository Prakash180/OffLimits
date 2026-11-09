"""
01 · Issuing an access token — the authorization server's job
=============================================================

An OAuth2 *authorization server* mints access tokens after a user authenticates.
A realistic access token carries standard registered claims:

* ``iss`` (issuer)   — who minted it (your auth server URL).
* ``sub`` (subject)  — the user/principal id.
* ``aud`` (audience) — which API/resource the token is FOR.
* ``iat`` (issued at), ``nbf`` (not before), ``exp`` (expiry) — the time window.
* ``scope``          — space-delimited OAuth2 permissions.
* plus app claims (e.g. ``roles``).

This module's verifier (script 02) checks these. We show both an HS256 issuer
(shared secret) and an RS256 issuer (private key), since real systems use both.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/15-real-world-fastapi-oauth/01_issue_access_token.py
"""

from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"
HS_SECRET = "auth-server-hs256-secret-at-least-32-bytes!!"


def issue_access_token_hs256(
    subject: str, scope: str, ttl_seconds: int = 900
) -> str:
    """Issue an HS256 access token with realistic OAuth2 claims."""
    now = datetime.now(UTC)
    claims = {
        "iss": ISSUER,
        "sub": subject,
        "aud": AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(seconds=ttl_seconds),
        "scope": scope,
        "token_type": "access",
    }
    return jwt.encode(claims, HS_SECRET, algorithm="HS256")


def issue_access_token_rs256(
    private_pem: str, subject: str, scope: str, kid: str, ttl_seconds: int = 900
) -> str:
    """Issue an RS256 access token; include a 'kid' so verifiers pick the key."""
    now = datetime.now(UTC)
    claims = {
        "iss": ISSUER,
        "sub": subject,
        "aud": AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(seconds=ttl_seconds),
        "scope": scope,
        "token_type": "access",
    }
    return jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": kid})


def main() -> None:
    print("=" * 72)
    print("HS256 access token (shared-secret issuer)")
    print("=" * 72)
    hs = issue_access_token_hs256("user-123", scope="profile email read:reports")
    print(f"token: {hs}")
    # Decode just to display the claims we minted (verification covered in 02).
    print("claims:", jwt.decode(hs, HS_SECRET, algorithms=["HS256"], audience=AUDIENCE))
    print()

    print("=" * 72)
    print("RS256 access token (private-key issuer, with kid header)")
    print("=" * 72)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    rs = issue_access_token_rs256(private_pem, "user-123", "profile admin", kid="key-1")
    print(f"token: {rs[:60]}...")
    print(f"header: {jwt.get_unverified_header(rs)}")
    print("claims:", jwt.decode(rs, public_pem, algorithms=["RS256"], audience=AUDIENCE))

    print("\nNext: script 02 verifies these tokens, enforcing iss/aud/exp.")


if __name__ == "__main__":
    main()
