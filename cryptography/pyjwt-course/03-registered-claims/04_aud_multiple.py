"""04 · The `aud` claim as a *list* of audiences.

RFC 7519 allows `aud` to be either a single string OR an array of strings. A
token can therefore be valid for several services at once.

Validation rule (set intersection): decoding succeeds if **any** audience the
caller accepts is present in the token's `aud`. You can pass ``audience=`` as a
single string or as a list/iterable of acceptable values.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/04_aud_multiple.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    # The token is intended for THREE audiences.
    token = jwt.encode(
        {
            "aud": [
                "https://api.example.com",
                "https://reports.example.com",
                "https://admin.example.com",
            ],
            "sub": "user-123",
        },
        SECRET,
        algorithm="HS256",
    )
    print("Encoded token (aud is a list of 3 values).")

    # --- Caller accepts a single value that IS in the list ---------------
    decoded = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        audience="https://reports.example.com",
    )
    print("\n[OK] Single accepted audience matched one entry in the list:")
    print("    ", decoded["aud"])

    # --- Caller passes a LIST of acceptable audiences --------------------
    # Succeeds because the intersection with the token's `aud` is non-empty.
    decoded = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        audience=["https://admin.example.com", "https://unrelated.example.com"],
    )
    print("\n[OK] Caller's accepted-list overlapped the token's audience list.")

    # --- No overlap -> failure -------------------------------------------
    try:
        jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            audience=["https://nope.example.com"],
        )
    except jwt.InvalidAudienceError as exc:
        print("\n[EXPECTED FAILURE] InvalidAudienceError raised:")
        print("    ", exc)
        print("    None of the accepted audiences appeared in the token's `aud`.")


if __name__ == "__main__":
    main()
