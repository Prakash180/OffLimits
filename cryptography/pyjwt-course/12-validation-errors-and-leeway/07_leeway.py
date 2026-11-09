"""07 · ``leeway`` — tolerating small clock skew.

Real clocks drift. A token that expired 5 seconds ago might be perfectly fine to
accept if the issuer's clock was simply a hair ahead of yours. PyJWT's ``leeway``
argument adds a grace window (in seconds, or a ``timedelta``) to the time-based
checks (``exp`` and ``nbf``), so *just*-expired or *just*-premature tokens are
still accepted.

This script issues a token that expired 5 seconds ago and decodes it two ways:
    - WITHOUT leeway  -> ExpiredSignatureError;
    - WITH leeway=10  -> accepted (5s < 10s grace).

⚠️ Keep leeway small (a few seconds to a minute). It directly extends how long an
expired token remains usable.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/07_leeway.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"


def main() -> None:
    now = datetime.now(UTC)

    # Expired just 5 seconds ago.
    token = jwt.encode(
        {"user": "mallory", "exp": now - timedelta(seconds=5)},
        SECRET,
        algorithm="HS256",
    )
    print("Token expired 5 seconds ago.")
    print()

    # Side A: no leeway -> rejected.
    print("A) decode WITHOUT leeway:")
    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as e:
        print(f"   ❌ {type(e).__name__}: {e}")
    print()

    # Side B: 10 seconds of leeway -> accepted.
    print("B) decode WITH leeway=10 seconds:")
    claims = jwt.decode(token, SECRET, algorithms=["HS256"], leeway=10)
    print(f"   ✅ accepted within grace window: {claims}")
    print()

    print("✅ leeway absorbs small clock skew — use sparingly (seconds, not hours).")


if __name__ == "__main__":
    main()
