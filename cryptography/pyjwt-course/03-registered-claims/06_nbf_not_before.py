"""06 · The `nbf` (not before) registered claim.

`nbf` is a NumericDate before which the token MUST NOT be accepted. It is the
mirror image of `exp`: it makes a token *start* being valid at a future moment
(handy for scheduled / time-locked credentials).

PyJWT verifies `nbf` automatically when present. If "now" is earlier than
`nbf`, it raises :class:`jwt.ImmatureSignatureError`.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/06_nbf_not_before.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    now = datetime.now(UTC)

    # --- nbf in the FUTURE -> token is not valid yet ---------------------
    future_token = jwt.encode(
        {"sub": "user-123", "nbf": now + timedelta(minutes=10)},
        SECRET,
        algorithm="HS256",
    )
    try:
        jwt.decode(future_token, SECRET, algorithms=["HS256"])
    except jwt.ImmatureSignatureError as exc:
        print("[EXPECTED FAILURE] ImmatureSignatureError raised:")
        print("    ", exc)
        print("    The token will only become valid 10 minutes from now.")

    # --- nbf in the PAST -> token is active ------------------------------
    active_token = jwt.encode(
        {"sub": "user-123", "nbf": now - timedelta(minutes=10)},
        SECRET,
        algorithm="HS256",
    )
    decoded = jwt.decode(active_token, SECRET, algorithms=["HS256"])
    print("\n[OK] Token with past `nbf` decoded fine.")
    print("     nbf (epoch seconds):", decoded["nbf"])


if __name__ == "__main__":
    main()
