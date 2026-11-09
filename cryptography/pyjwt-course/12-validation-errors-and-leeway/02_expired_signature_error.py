"""02 · ``ExpiredSignatureError`` — the token's time is up.

The ``exp`` (expiration time) claim is a Unix timestamp after which the token must
be rejected. PyJWT checks it automatically during ``decode`` (when ``exp`` is
present) and raises ``ExpiredSignatureError`` once the current time passes it.

We make this happen *deliberately* by issuing a token that already expired one
hour ago, then decoding it.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/02_expired_signature_error.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"


def main() -> None:
    now = datetime.now(UTC)  # always timezone-aware!

    # exp one hour in the PAST -> already expired.
    token = jwt.encode(
        {"user": "grace", "exp": now - timedelta(hours=1)},
        SECRET,
        algorithm="HS256",
    )
    print("Issued a token that expired 1 hour ago.")
    print()

    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as e:
        print(f"❌ Caught {type(e).__name__}: {e}")
        print("   Meaning: the 'exp' timestamp is in the past. Reject the token.")
    else:
        print("Unexpected: token verified (it should have been expired).")

    print()
    print("✅ PyJWT enforces 'exp' for you — no manual time math needed.")


if __name__ == "__main__":
    main()
