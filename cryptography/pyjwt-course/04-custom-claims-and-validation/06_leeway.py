"""06 · leeway — tolerating small clock differences.

Servers' clocks are never perfectly in sync. A token that expired "0.5 seconds
ago" according to your clock may still be valid by the issuer's. ``leeway``
gives time-based checks (`exp`, `nbf`, `iat`) a grace window so honest tokens
near a boundary aren't rejected over millisecond skew.

You can pass ``leeway`` as a number of seconds or as a
:class:`datetime.timedelta`.

⚠️ Keep leeway small (seconds, not minutes). It widens the window in which an
expired token is still accepted.

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/06_leeway.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    now = datetime.now(UTC)

    # Expired 10 seconds ago — just over the edge.
    just_expired = jwt.encode(
        {"sub": "user-123", "exp": now - timedelta(seconds=10)},
        SECRET,
        algorithm="HS256",
    )

    # --- Without leeway: rejected ----------------------------------------
    try:
        jwt.decode(just_expired, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        print("[NO LEEWAY] Rejected (expired 10s ago):", exc)

    # --- With 30s leeway: accepted ---------------------------------------
    decoded = jwt.decode(
        just_expired,
        SECRET,
        algorithms=["HS256"],
        leeway=timedelta(seconds=30),
    )
    print("\n[leeway=30s] Accepted despite being 10s past exp:")
    print("    ", decoded)

    # --- But leeway is finite: 40s past exp with 30s leeway still fails ---
    more_expired = jwt.encode(
        {"sub": "user-123", "exp": now - timedelta(seconds=40)},
        SECRET,
        algorithm="HS256",
    )
    try:
        jwt.decode(more_expired, SECRET, algorithms=["HS256"], leeway=timedelta(seconds=30))
    except jwt.ExpiredSignatureError as exc:
        print("\n[leeway=30s] Still rejected when 40s past exp:", exc)


if __name__ == "__main__":
    main()
