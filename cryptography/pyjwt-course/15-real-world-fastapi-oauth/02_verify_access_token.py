"""
02 · Verifying an access token — the resource server's job
==========================================================

A *resource server* (your API) receives an access token and must validate it
before trusting any claim. A correct verifier:

1. Pins the algorithm: ``algorithms=["HS256"]`` (or RS256).
2. Checks the signature (PyJWT does this with the key).
3. Enforces ``aud`` — the token must be FOR this API (``audience=...``).
4. Enforces ``iss`` — the token must be FROM our trusted issuer (``issuer=...``).
5. Enforces ``exp``/``nbf`` — automatically, and we ``require`` the key ones.

We show a valid token passing and a battery of bad tokens being rejected with
specific, catchable PyJWT exceptions.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/15-real-world-fastapi-oauth/02_verify_access_token.py
"""

from datetime import UTC, datetime, timedelta

import jwt

ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"
SECRET = "auth-server-hs256-secret-at-least-32-bytes!!"


def issue(subject: str, **overrides) -> str:
    now = datetime.now(UTC)
    claims = {
        "iss": ISSUER,
        "sub": subject,
        "aud": AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=15),
        "scope": "read",
    }
    claims.update(overrides)
    return jwt.encode(claims, SECRET, algorithm="HS256")


def verify_access_token(token: str) -> dict:
    """Validate signature + iss + aud + exp; return trusted claims or raise."""
    return jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],  # pin the algorithm — never trust the header
        audience=AUDIENCE,  # reject tokens minted for another API
        issuer=ISSUER,  # reject tokens from another issuer
        options={"require": ["exp", "iss", "aud", "sub"]},
    )


def main() -> None:
    print("=" * 72)
    print("VALID token -> accepted")
    print("=" * 72)
    good = issue("user-123")
    print(f"claims: {verify_access_token(good)}\n")

    print("=" * 72)
    print("INVALID tokens -> each rejected with a specific exception")
    print("=" * 72)

    cases = {
        "wrong audience": issue("user-123", aud="https://other-api.example.com"),
        "wrong issuer": issue("user-123", iss="https://evil.example.com"),
        "expired": issue(
            "user-123",
            iat=datetime.now(UTC) - timedelta(hours=2),
            exp=datetime.now(UTC) - timedelta(hours=1),
        ),
        "tampered signature": issue("user-123")[:-3] + "xyz",
        "wrong secret": jwt.encode(
            {
                "iss": ISSUER,
                "sub": "mallory",
                "aud": AUDIENCE,
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            "attacker-secret-attacker-secret-attacker!",
            algorithm="HS256",
        ),
    }

    for label, token in cases.items():
        try:
            verify_access_token(token)
            print(f"  {label:20} -> UNEXPECTEDLY ACCEPTED")
        except jwt.InvalidTokenError as exc:
            print(f"  {label:20} -> rejected: {type(exc).__name__}")

    print("\nEvery untrusted token is rejected. Trust only verified claims.")


if __name__ == "__main__":
    main()
