"""03 · options={"verify_exp": False}.

By default PyJWT rejects expired tokens. You can switch that single check off
with ``options={"verify_exp": False}`` while still verifying the signature and
everything else.

⚠️ Risk: accepting expired tokens defeats the purpose of `exp`. Stolen or
long-forgotten tokens become valid forever. Use this only for narrow,
deliberate cases (e.g. reading an expired token's claims to show a friendly
"your session ended" message) — never as a general policy.

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/03_options_verify_exp.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    now = datetime.now(UTC)

    # A token that expired an hour ago.
    expired = jwt.encode(
        {"sub": "user-123", "exp": now - timedelta(hours=1)},
        SECRET,
        algorithm="HS256",
    )

    # --- Default behaviour: rejected -------------------------------------
    try:
        jwt.decode(expired, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        print("[DEFAULT] Expired token rejected:", exc)

    # --- Opt out of the expiry check (signature STILL verified) ----------
    decoded = jwt.decode(
        expired,
        SECRET,
        algorithms=["HS256"],
        options={"verify_exp": False},
    )
    print("\n[verify_exp=False] Accepted the expired token:")
    print("    ", decoded)
    print("    ⚠️ Signature was still checked, but the deadline was ignored.")


if __name__ == "__main__":
    main()
