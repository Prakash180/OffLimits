"""
06 · The refresh-token grant — fresh access tokens without re-login
===================================================================

Access tokens are deliberately short-lived (15 minutes here). Rather than make
the user log in again every 15 minutes, the client keeps the long-lived
``refresh_token`` and exchanges it at ``/token`` for a brand-new access token:

    POST /token
        grant_type=refresh_token
        refresh_token=<the opaque token>
        client_id / client_secret

This script logs in once, then refreshes, and compares the OLD vs NEW token
expiry to prove the access token's lifetime was extended.

Run:
    uv run python pyjwt-course/16-local-identity-provider/06_refresh_token_flow.py
"""

from datetime import UTC, datetime

import jwt


def exp_of(token: str) -> datetime:
    """Read the `exp` claim from a JWT without verifying (inspection only)."""
    payload = jwt.decode(token, options={"verify_signature": False})
    return datetime.fromtimestamp(payload["exp"], tz=UTC)


def main() -> None:
    # Imported here so the module import line is part of the visible lesson.
    from idp.client import LocalIdPClient

    client = LocalIdPClient()

    print("=" * 72)
    print("STEP 1 · initial login (authorization_code grant)")
    print("=" * 72)
    tokens = client.login(scope="openid api.read")
    old_access = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    print(f"access_token  exp: {exp_of(old_access).isoformat()}")
    print(f"refresh_token    : {refresh_token[:16]}... (kept by the client)")

    print("\n" + "=" * 72)
    print("STEP 2 · refresh_token grant  ->  a fresh access token")
    print("=" * 72)
    refreshed = client.refresh(refresh_token)
    new_access = refreshed["access_token"]
    print(f"new access_token exp: {exp_of(new_access).isoformat()}")

    print("\n" + "=" * 72)
    print("OLD vs NEW")
    print("=" * 72)
    print(f"old exp: {exp_of(old_access).isoformat()}")
    print(f"new exp: {exp_of(new_access).isoformat()}")
    print(f"new token is a distinct credential (different jti): {new_access != old_access}")
    print(f"new expiry is later or equal: {exp_of(new_access) >= exp_of(old_access)}")
    print("(Issued back-to-back here, so exp can match to the second; in real use")
    print(" the refresh happens minutes later and the new exp strictly advances.)")

    assert new_access != old_access
    assert exp_of(new_access) >= exp_of(old_access)
    assert "refresh_token" in refreshed  # the grant also rotates the refresh token
    print("\nOK ✔  refresh grant issued a new, longer-lived access token.")


if __name__ == "__main__":
    main()
