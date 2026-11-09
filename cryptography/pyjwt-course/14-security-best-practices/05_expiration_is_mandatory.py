"""
05 · Expiration is mandatory — tokens without `exp` live forever
================================================================

A JWT is a *bearer* credential: whoever holds it is treated as the subject.
If a token never expires and it leaks (logs, browser history, a proxy, a
breach), the attacker has permanent access. There is no server-side session to
revoke unless you build extra infrastructure.

Defenses shown here:

1. A token with NO ``exp`` validates forever — demonstrate it.
2. Add a short-lived ``exp``; an expired token is rejected with
   ``ExpiredSignatureError``.
3. Force the issue: ``options={"require": ["exp"]}`` makes a missing ``exp`` an
   error, so you can never accidentally mint an eternal token.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/05_expiration_is_mandatory.py
"""

import time
from datetime import UTC, datetime, timedelta

import jwt

SECRET = "a-strong-shared-secret-at-least-32-bytes-long!!"


def main() -> None:
    now = datetime.now(UTC)

    print("=" * 72)
    print("PROBLEM — a token with no `exp` is valid indefinitely")
    print("=" * 72)
    eternal = jwt.encode({"sub": "alice"}, SECRET, algorithm="HS256")
    decoded = jwt.decode(eternal, SECRET, algorithms=["HS256"])
    print(f"no-exp token decodes fine: {decoded}")
    print("If this leaks, it grants access until you rotate the signing key.\n")

    print("=" * 72)
    print("FIX 1 — set a short lifetime with a timezone-aware `exp`")
    print("=" * 72)
    short = jwt.encode(
        {"sub": "alice", "iat": now, "exp": now + timedelta(seconds=1)},
        SECRET,
        algorithm="HS256",
    )
    print("issued token with exp = now + 1 second")
    fresh = jwt.decode(short, SECRET, algorithms=["HS256"])
    print(f"immediately valid: {fresh}")

    # Wait for it to expire, then prove PyJWT rejects it.
    time.sleep(1.2)
    try:
        jwt.decode(short, SECRET, algorithms=["HS256"])
        print("UNEXPECTED: expired token still valid?!")
    except jwt.ExpiredSignatureError as exc:
        print(f"after expiry -> {type(exc).__name__}: {exc} (rejected)\n")

    print("=" * 72)
    print("FIX 2 — REQUIRE exp so a missing one is an error, not a silent forever")
    print("=" * 72)
    try:
        jwt.decode(
            eternal,
            SECRET,
            algorithms=["HS256"],
            options={"require": ["exp"], "verify_exp": True},
        )
        print("UNEXPECTED: no-exp token passed the require check?!")
    except jwt.MissingRequiredClaimError as exc:
        print(f"require=['exp'] on no-exp token -> {type(exc).__name__}: {exc}\n")

    print("=" * 72)
    print("GUIDANCE")
    print("=" * 72)
    print("- Always set `exp`. Keep access tokens SHORT (minutes), e.g. 5-15 min.")
    print("- Use refresh tokens for longevity (see module 15).")
    print("- Enforce with options={'require': ['exp']} so it can't be forgotten.")
    print("- Use leeway (a few seconds) only to tolerate small clock skew.")


if __name__ == "__main__":
    main()
