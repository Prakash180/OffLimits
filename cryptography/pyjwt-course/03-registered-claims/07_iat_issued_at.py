"""07 · The `iat` (issued at) registered claim.

`iat` records *when* the token was created (a NumericDate). It is primarily
**informational** — you can use it to compute a token's age or to reject very
old tokens with your own logic.

Behaviour notes for PyJWT 2.13:
  * `iat` is decoded and made available in the payload.
  * PyJWT treats `iat` like a "not before" hint: an `iat` in the FUTURE makes
    the token immature and raises `ImmatureSignatureError`.
  * You can switch that check off with ``options={"verify_iat": False}`` and/or
    enforce your own freshness policy by comparing `iat` to "now".

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/07_iat_issued_at.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    now = datetime.now(UTC)

    # --- Normal: iat = now -----------------------------------------------
    token = jwt.encode({"sub": "user-123", "iat": now}, SECRET, algorithm="HS256")
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    issued = datetime.fromtimestamp(decoded["iat"], tz=UTC)
    print("[OK] Decoded `iat`:", decoded["iat"], "->", issued.isoformat())

    # --- iat far in the FUTURE: PyJWT rejects it as immature -------------
    future = jwt.encode(
        {"sub": "user-123", "iat": now + timedelta(days=365)},
        SECRET,
        algorithm="HS256",
    )
    try:
        jwt.decode(future, SECRET, algorithms=["HS256"])
    except jwt.ImmatureSignatureError as exc:
        print("\n[EXPECTED FAILURE] A future `iat` is treated as not-yet-valid:")
        print("    ", exc)

    # --- Read it anyway by disabling just the iat check ------------------
    decoded_future = jwt.decode(
        future,
        SECRET,
        algorithms=["HS256"],
        options={"verify_iat": False},
    )
    print("\n[verify_iat=False] Decoded the future-iat token:")
    print("     iat:", decoded_future["iat"])

    # --- Enforce your own freshness policy on top ------------------------
    # Example: flag anything claiming to be issued more than 1 day ahead.
    age = decoded_future["iat"] - now.timestamp()
    if age > timedelta(days=1).total_seconds():
        print("\n[CUSTOM POLICY] `iat` is implausibly far in the future")
        print(f"    (about {age / 86400:.0f} days ahead of now).")


if __name__ == "__main__":
    main()
