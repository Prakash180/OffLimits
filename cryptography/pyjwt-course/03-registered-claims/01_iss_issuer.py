"""01 · The `iss` (issuer) registered claim.

The `iss` claim identifies *who* issued the token. It is a free-form string —
typically a URL or a stable identifier for your auth server (e.g.
``"https://auth.example.com"``).

PyJWT does not validate `iss` automatically. You opt in by passing
``issuer="..."`` to :func:`jwt.decode`. When you do, PyJWT compares the token's
`iss` against the expected value and raises
:class:`jwt.InvalidIssuerError` on a mismatch.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/01_iss_issuer.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"
EXPECTED_ISSUER = "https://auth.example.com"


def main() -> None:
    # --- Encode a token that declares its issuer -------------------------
    token = jwt.encode(
        {"iss": EXPECTED_ISSUER, "sub": "user-123"},
        SECRET,
        algorithm="HS256",
    )
    print("Encoded token:", token)

    # --- Happy path: decode with the matching expected issuer ------------
    decoded = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        issuer=EXPECTED_ISSUER,  # opt in to issuer validation
    )
    print("\n[OK] Issuer matched. Decoded payload:")
    print("    ", decoded)

    # --- Failure path: expect a *different* issuer -----------------------
    # PyJWT compares token['iss'] to the value we pass; a mismatch raises.
    try:
        jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            issuer="https://evil.example.com",
        )
    except jwt.InvalidIssuerError as exc:
        print("\n[EXPECTED FAILURE] InvalidIssuerError raised:")
        print("    ", exc)
        print("    The token's `iss` did not match the expected issuer.")


if __name__ == "__main__":
    main()
