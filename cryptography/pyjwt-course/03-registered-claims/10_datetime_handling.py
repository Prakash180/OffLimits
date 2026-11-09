"""10 · How PyJWT handles datetimes for the time-based claims.

The time claims (`exp`, `nbf`, `iat`) are defined by RFC 7519 as **NumericDate**
values: the number of seconds since 1970-01-01T00:00:00Z (the Unix epoch),
ignoring leap seconds.

You almost never compute that number by hand. PyJWT accepts a
:class:`datetime.datetime` object directly and converts it to epoch seconds for
you. A plain ``int`` epoch works too. This script proves all three are
equivalent.

Always use timezone-AWARE datetimes (``datetime.now(timezone.utc)``); a naive
datetime is interpreted as UTC by PyJWT but is ambiguous in your own code.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/10_datetime_handling.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    now = datetime.now(UTC)
    exp_dt = now + timedelta(hours=1)

    # --- (a) pass a datetime object --------------------------------------
    token_dt = jwt.encode({"sub": "u", "exp": exp_dt}, SECRET, algorithm="HS256")
    decoded_dt = jwt.decode(token_dt, SECRET, algorithms=["HS256"])
    print("(a) datetime input -> stored as epoch int:", decoded_dt["exp"])
    print("    type in decoded payload:", type(decoded_dt["exp"]).__name__)

    # --- (b) pass the equivalent int epoch directly ----------------------
    exp_epoch = int(exp_dt.timestamp())
    token_int = jwt.encode({"sub": "u", "exp": exp_epoch}, SECRET, algorithm="HS256")
    decoded_int = jwt.decode(token_int, SECRET, algorithms=["HS256"])
    print("\n(b) int epoch input -> stored unchanged:", decoded_int["exp"])

    # --- They describe the same instant ----------------------------------
    print("\nBoth represent the same expiry second:", decoded_dt["exp"] == decoded_int["exp"])

    # --- Round-trip back to a human-readable datetime --------------------
    restored = datetime.fromtimestamp(decoded_dt["exp"], tz=UTC)
    print("Restored expiry:", restored.isoformat())

    # --- All three time claims accept datetimes simultaneously ----------
    full = jwt.encode(
        {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=5),
        },
        SECRET,
        algorithm="HS256",
    )
    decoded_full = jwt.decode(full, SECRET, algorithms=["HS256"])
    print("\nAll time claims as ints:", {k: decoded_full[k] for k in ("iat", "nbf", "exp")})


if __name__ == "__main__":
    main()
