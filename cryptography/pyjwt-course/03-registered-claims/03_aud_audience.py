"""03 · The `aud` (audience) registered claim — single string form.

The `aud` claim names the *intended recipient(s)* of the token. A resource
server should reject any token that was not minted for it.

PyJWT validates `aud` only when you pass ``audience="..."`` to
:func:`jwt.decode`. A mismatch raises :class:`jwt.InvalidAudienceError`.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/03_aud_audience.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"
EXPECTED_AUDIENCE = "https://api.example.com"


def main() -> None:
    # `aud` here is a single string (the most common case).
    token = jwt.encode(
        {"aud": EXPECTED_AUDIENCE, "sub": "user-123"},
        SECRET,
        algorithm="HS256",
    )
    print("Encoded token:", token)

    # --- Happy path: audience matches ------------------------------------
    decoded = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        audience=EXPECTED_AUDIENCE,  # opt in to audience validation
    )
    print("\n[OK] Audience matched. Decoded payload:")
    print("    ", decoded)

    # --- Failure path: this token was not minted for us ------------------
    try:
        jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            audience="https://other-api.example.com",
        )
    except jwt.InvalidAudienceError as exc:
        print("\n[EXPECTED FAILURE] InvalidAudienceError raised:")
        print("    ", exc)
        print("    Always verify `aud` so tokens can't be replayed across services.")


if __name__ == "__main__":
    main()
