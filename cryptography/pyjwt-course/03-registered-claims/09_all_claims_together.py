"""09 · All seven registered claims, together.

This brings the whole module into one token:

    iss  – who issued it
    sub  – who it's about
    aud  – who it's for
    exp  – when it stops being valid
    nbf  – when it starts being valid
    iat  – when it was issued
    jti  – its unique id

We then decode with *every* matching validation parameter switched on, so PyJWT
checks the signature, `exp`, `nbf`, plus `iss`, `aud`, and `sub`.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/09_all_claims_together.py
"""

import uuid
from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"
ISSUER = "https://auth.example.com"
SUBJECT = "user-123"
AUDIENCE = "https://api.example.com"


def main() -> None:
    now = datetime.now(UTC)

    payload = {
        "iss": ISSUER,
        "sub": SUBJECT,
        "aud": AUDIENCE,
        "iat": now,
        "nbf": now - timedelta(seconds=5),       # already active
        "exp": now + timedelta(minutes=15),      # valid for 15 minutes
        "jti": str(uuid.uuid4()),
    }

    token = jwt.encode(payload, SECRET, algorithm="HS256")
    print("Encoded a token carrying all 7 registered claims.\n")

    # Decode with every check enabled. `exp`/`nbf` are automatic; `iss`,
    # `aud`, `sub` are opted in via parameters.
    decoded = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        issuer=ISSUER,
        audience=AUDIENCE,
        subject=SUBJECT,
    )

    print("[OK] Fully validated. Claims:")
    for name in ("iss", "sub", "aud", "iat", "nbf", "exp", "jti"):
        print(f"    {name:<4} = {decoded[name]}")


if __name__ == "__main__":
    main()
