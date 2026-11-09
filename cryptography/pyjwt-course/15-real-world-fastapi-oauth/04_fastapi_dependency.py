"""
04 · FastAPI dependency — protecting a route with a Bearer token
================================================================

The idiomatic FastAPI auth pattern: a **dependency** that extracts the Bearer
token from the ``Authorization`` header, validates it, and returns the claims.
Any route that ``Depends`` on it is automatically protected; an invalid or
missing token yields ``401``.

We make the app importable and VERIFY it in-process:

* Preferred: ``fastapi.testclient.TestClient`` calls ``/me`` with a valid and an
  invalid token (no live server, no network).
* Fallback: if ``TestClient`` can't import (it needs ``httpx``), we call the
  dependency function directly with hand-built credentials. Either way the
  script exits 0 and prints clear results.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/15-real-world-fastapi-oauth/04_fastapi_dependency.py
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"
SECRET = "fastapi-demo-hs256-secret-32-bytes-long!!"

app = FastAPI(title="JWT-protected API")

# auto_error=False so we can return our own 401 with a helpful message.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """FastAPI dependency: extract + validate the Bearer token, return claims."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        claims = jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return claims


@app.get("/me")
def read_me(user: dict = Depends(get_current_user)) -> dict:
    """Protected route: only reachable with a valid Bearer token."""
    return {"sub": user["sub"], "scope": user.get("scope")}


def make_token(subject: str = "user-123", scope: str = "profile read") -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": ISSUER,
            "sub": subject,
            "aud": AUDIENCE,
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "scope": scope,
        },
        SECRET,
        algorithm="HS256",
    )


def verify_with_testclient() -> bool:
    """Try the real HTTP path via TestClient. Returns True if it ran."""
    try:
        from fastapi.testclient import TestClient
    except Exception as exc:  # noqa: BLE001 - httpx may be absent
        print(f"[info] TestClient unavailable ({type(exc).__name__}); using fallback.")
        return False

    client = TestClient(app)
    valid = make_token()

    print("--- via TestClient (in-process HTTP, no network) ---")
    r1 = client.get("/me", headers={"Authorization": f"Bearer {valid}"})
    print(f"valid token   -> {r1.status_code} {r1.json()}")

    r2 = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})
    print(f"invalid token -> {r2.status_code} {r2.json()}")

    r3 = client.get("/me")
    print(f"no token      -> {r3.status_code} {r3.json()}")
    return True


def verify_with_direct_calls() -> None:
    """Fallback: call the dependency function directly (no HTTP layer)."""
    print("--- via direct dependency calls (fallback) ---")
    valid = make_token()

    creds_valid = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid)
    claims = get_current_user(creds_valid)
    print(f"valid token   -> 200 {{'sub': {claims['sub']!r}, 'scope': {claims.get('scope')!r}}}")

    creds_bad = HTTPAuthorizationCredentials(scheme="Bearer", credentials="not-a-real-token")
    try:
        get_current_user(creds_bad)
        print("invalid token -> UNEXPECTEDLY ACCEPTED")
    except HTTPException as exc:
        print(f"invalid token -> {exc.status_code} {{'detail': {exc.detail!r}}}")

    try:
        get_current_user(None)
        print("no token      -> UNEXPECTEDLY ACCEPTED")
    except HTTPException as exc:
        print(f"no token      -> {exc.status_code} {{'detail': {exc.detail!r}}}")


def main() -> None:
    print("=" * 72)
    print("FastAPI Bearer-token dependency protecting GET /me")
    print("=" * 72)
    if not verify_with_testclient():
        verify_with_direct_calls()
    print("\nThe /me route is gated by Depends(get_current_user): no valid token,")
    print("no access. This is the production-standard FastAPI auth pattern.")


if __name__ == "__main__":
    main()
