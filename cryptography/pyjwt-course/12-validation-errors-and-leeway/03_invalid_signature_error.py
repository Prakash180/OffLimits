"""03 · ``InvalidSignatureError`` — wrong key, tampered token.

The signature proves the token was produced by someone holding the signing key
*and* that not a single byte changed since. If you verify with the **wrong
secret** (or the token was altered), the recomputed signature won't match and
PyJWT raises ``InvalidSignatureError``.

Note ``InvalidSignatureError`` is a subclass of ``DecodeError`` — the signature
*decoded* fine, it just didn't *validate*.

Here we sign with one secret and verify with another.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/03_invalid_signature_error.py
"""

import jwt

RIGHT_SECRET = "the-real-signing-secret-padded-to-32-bytes!"
WRONG_SECRET = "an-attacker-guess-padded-to-at-least-32-byte"


def main() -> None:
    token = jwt.encode({"user": "heidi"}, RIGHT_SECRET, algorithm="HS256")
    print("Token signed with the correct secret.")
    print()

    # Verifying with the wrong secret -> signature mismatch.
    try:
        jwt.decode(token, WRONG_SECRET, algorithms=["HS256"])
    except jwt.InvalidSignatureError as e:
        print(f"❌ Caught {type(e).__name__}: {e}")
        print("   Meaning: signature didn't match -> wrong key or tampered token.")

    print()

    # Sanity: the right secret still works.
    claims = jwt.decode(token, RIGHT_SECRET, algorithms=["HS256"])
    print(f"✅ With the correct secret it verifies fine: {claims}")


if __name__ == "__main__":
    main()
