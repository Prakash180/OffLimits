"""
03 · Access + refresh tokens — short-lived access, long-lived refresh
=====================================================================

Access tokens should be SHORT-lived (minutes) so a leaked one expires quickly.
But you don't want users logging in every 15 minutes. The standard answer:

* **Access token**  — short TTL (e.g. 15 min), sent on every API call.
* **Refresh token** — long TTL (e.g. 30 days), sent ONLY to the auth server to
  mint a new access token when the old one expires.

We distinguish them with a ``token_type`` claim and (in real systems) often a
separate signing key/audience. The ``refresh()`` function validates a refresh
token and issues a fresh access token — refusing to accept an *access* token in
the refresh slot (a common confused-deputy mistake).

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/15-real-world-fastapi-oauth/03_access_and_refresh_tokens.py
"""

from datetime import UTC, datetime, timedelta

import jwt

ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"
ACCESS_SECRET = "access-token-signing-secret-32-bytes-long!!"
REFRESH_SECRET = "refresh-token-signing-secret-32-bytes-long!"  # separate key!

ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=30)


def issue_access_token(subject: str, scope: str) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": ISSUER,
            "sub": subject,
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + ACCESS_TTL,
            "scope": scope,
            "token_type": "access",
        },
        ACCESS_SECRET,
        algorithm="HS256",
    )


def issue_refresh_token(subject: str, scope: str) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": ISSUER,
            "sub": subject,
            "iat": now,
            "exp": now + REFRESH_TTL,
            "scope": scope,
            "token_type": "refresh",
        },
        REFRESH_SECRET,  # signed with the REFRESH key, not the access key
        algorithm="HS256",
    )


def refresh(refresh_token: str) -> str:
    """Validate a refresh token and mint a NEW access token."""
    claims = jwt.decode(
        refresh_token,
        REFRESH_SECRET,
        algorithms=["HS256"],
        issuer=ISSUER,
        options={"require": ["exp", "sub", "token_type"]},
    )
    # Defense: ensure this is actually a refresh token, not an access token.
    if claims.get("token_type") != "refresh":
        raise jwt.InvalidTokenError("not a refresh token")
    return issue_access_token(claims["sub"], claims["scope"])


def main() -> None:
    print("=" * 72)
    print("LOGIN — issue an access + refresh token pair")
    print("=" * 72)
    access = issue_access_token("user-123", "profile read")
    refresh_tok = issue_refresh_token("user-123", "profile read")
    print(f"access  (15 min): {access[:45]}...")
    print(f"refresh (30 day): {refresh_tok[:45]}...\n")

    print("=" * 72)
    print("REFRESH — exchange a valid refresh token for a new access token")
    print("=" * 72)
    new_access = refresh(refresh_tok)
    new_claims = jwt.decode(
        new_access, ACCESS_SECRET, algorithms=["HS256"], audience=AUDIENCE
    )
    print(f"new access token: {new_access[:45]}...")
    print(f"new access claims: sub={new_claims['sub']} scope={new_claims['scope']!r}")
    print(f"different from old access token? {new_access != access}\n")

    print("=" * 72)
    print("ABUSE 1 — an ACCESS token cannot be used to refresh")
    print("=" * 72)
    try:
        refresh(access)  # access token signed with ACCESS_SECRET, wrong key
        print("UNEXPECTED: access token accepted as refresh!")
    except jwt.InvalidTokenError as exc:
        print(f"refresh(access_token) -> rejected: {type(exc).__name__}\n")

    print("=" * 72)
    print("ABUSE 2 — a tampered/forged refresh token is rejected")
    print("=" * 72)
    try:
        refresh(refresh_tok[:-3] + "abc")
        print("UNEXPECTED: tampered refresh accepted!")
    except jwt.InvalidTokenError as exc:
        print(f"refresh(tampered) -> rejected: {type(exc).__name__}")

    print("\nPattern: short access TTL limits blast radius; refresh token (kept")
    print("safe, separate key) renews access without re-authenticating the user.")


if __name__ == "__main__":
    main()
