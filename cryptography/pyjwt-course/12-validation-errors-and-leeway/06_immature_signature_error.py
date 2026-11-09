"""06 · ``ImmatureSignatureError`` — the token isn't valid YET.

The ``nbf`` (not before) claim is the mirror image of ``exp``: a Unix timestamp
*before* which the token must be rejected. It's used for tokens that should only
activate in the future (scheduled access, delayed grants). Decode such a token
too early and PyJWT raises ``ImmatureSignatureError``.

We set ``nbf`` one hour in the future and try to use it immediately.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/06_immature_signature_error.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"


def main() -> None:
    now = datetime.now(UTC)

    # nbf one hour in the FUTURE -> not valid until then.
    token = jwt.encode(
        {"user": "judy", "nbf": now + timedelta(hours=1)},
        SECRET,
        algorithm="HS256",
    )
    print("Issued a token with nbf 1 hour in the future.")
    print()

    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ImmatureSignatureError as e:
        print(f"❌ Caught {type(e).__name__}: {e}")
        print("   Meaning: 'nbf' hasn't been reached yet -> token not active.")

    print()
    print("✅ nbf gates a token's START time, just as exp gates its END time.")


if __name__ == "__main__":
    main()
