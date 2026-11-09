"""05 · The `exp` (expiration time) registered claim.

`exp` is a NumericDate (seconds since the Unix epoch) after which the token
MUST be rejected. PyJWT verifies `exp` *by default* whenever the claim is
present — no extra parameter needed.

If the current time is at/after `exp`, PyJWT raises
:class:`jwt.ExpiredSignatureError` (a subclass of ``InvalidTokenError``).

Best practice: build the value from a timezone-aware datetime.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/05_exp_expiration.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    now = datetime.now(UTC)

    # --- Token valid for one more hour -----------------------------------
    fresh = jwt.encode(
        {"sub": "user-123", "exp": now + timedelta(hours=1)},
        SECRET,
        algorithm="HS256",
    )
    decoded = jwt.decode(fresh, SECRET, algorithms=["HS256"])
    print("[OK] Token with future `exp` decoded fine.")
    print("     exp (epoch seconds):", decoded["exp"])

    # --- Token that already expired one hour ago -------------------------
    stale = jwt.encode(
        {"sub": "user-123", "exp": now - timedelta(hours=1)},
        SECRET,
        algorithm="HS256",
    )
    try:
        jwt.decode(stale, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        print("\n[EXPECTED FAILURE] ExpiredSignatureError raised:")
        print("    ", exc)
        print("    `exp` is checked automatically; no decode parameter required.")


if __name__ == "__main__":
    main()
