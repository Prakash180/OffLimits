"""
05 · Scopes & authorization — OAuth2 `scope` and a require_scope guard
======================================================================

Authentication answers "who are you?"; **authorization** answers "are you
allowed to do this?". OAuth2 encodes permissions in a ``scope`` claim: a single
space-delimited string, e.g. ``"profile read:reports write:reports"``.

A resource server splits that string into a set and checks whether the required
scope is present. We build a ``require_scope()`` guard and demonstrate allow
(token has the scope) and deny (it doesn't).

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/15-real-world-fastapi-oauth/05_scopes_and_authorization.py
"""

from datetime import UTC, datetime, timedelta

import jwt

ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"
SECRET = "scopes-demo-hs256-secret-32-bytes-long!!!"


class PermissionDenied(Exception):
    """Raised when a verified token lacks a required scope (HTTP 403)."""


def issue(subject: str, scope: str) -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": ISSUER,
            "sub": subject,
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "scope": scope,  # OAuth2: space-delimited permissions
        },
        SECRET,
        algorithm="HS256",
    )


def verify(token: str) -> dict:
    return jwt.decode(
        token, SECRET, algorithms=["HS256"], audience=AUDIENCE, issuer=ISSUER
    )


def token_scopes(claims: dict) -> set[str]:
    """Parse the space-delimited 'scope' claim into a set."""
    return set(claims.get("scope", "").split())


def require_scope(claims: dict, needed: str) -> None:
    """Authorization guard: raise PermissionDenied unless `needed` is granted."""
    granted = token_scopes(claims)
    if needed not in granted:
        raise PermissionDenied(
            f"requires scope {needed!r}; token has {sorted(granted)}"
        )


def main() -> None:
    print("=" * 72)
    print("A reader token vs. an editor token")
    print("=" * 72)
    reader = issue("alice", "profile read:reports")
    editor = issue("bob", "profile read:reports write:reports")
    reader_claims = verify(reader)
    editor_claims = verify(editor)
    print(f"alice scopes: {sorted(token_scopes(reader_claims))}")
    print(f"bob   scopes: {sorted(token_scopes(editor_claims))}\n")

    print("=" * 72)
    print("GET /reports  requires scope 'read:reports'")
    print("=" * 72)
    for name, claims in (("alice", reader_claims), ("bob", editor_claims)):
        try:
            require_scope(claims, "read:reports")
            print(f"  {name}: ALLOWED ✔")
        except PermissionDenied as exc:
            print(f"  {name}: DENIED  — {exc}")
    print()

    print("=" * 72)
    print("POST /reports  requires scope 'write:reports'")
    print("=" * 72)
    for name, claims in (("alice", reader_claims), ("bob", editor_claims)):
        try:
            require_scope(claims, "write:reports")
            print(f"  {name}: ALLOWED ✔")
        except PermissionDenied as exc:
            print(f"  {name}: DENIED  — {exc}")

    print("\nAuthN proves identity; AuthZ (scopes) decides what that identity may")
    print("do. In FastAPI, wrap require_scope in a dependency per protected route.")


if __name__ == "__main__":
    main()
