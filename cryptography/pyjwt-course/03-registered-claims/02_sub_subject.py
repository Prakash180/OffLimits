"""02 · The `sub` (subject) registered claim.

The `sub` claim identifies the *principal* the token is about — usually the
user ID. It should be unique and stable within the issuer's namespace.

Since PyJWT 2.x you can validate it by passing ``subject="..."`` to
:func:`jwt.decode`. A mismatch raises :class:`jwt.InvalidSubjectError`; if the
token has no `sub` at all while you require one, PyJWT raises
:class:`jwt.MissingRequiredClaimError`.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/02_sub_subject.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"
EXPECTED_SUBJECT = "user-123"


def main() -> None:
    token = jwt.encode(
        {"sub": EXPECTED_SUBJECT, "iss": "https://auth.example.com"},
        SECRET,
        algorithm="HS256",
    )
    print("Encoded token:", token)

    # --- Happy path: subject matches -------------------------------------
    decoded = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        subject=EXPECTED_SUBJECT,  # opt in to subject validation
    )
    print("\n[OK] Subject matched. Decoded payload:")
    print("    ", decoded)

    # --- Failure path: wrong expected subject ----------------------------
    try:
        jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            subject="user-999",
        )
    except jwt.exceptions.InvalidSubjectError as exc:
        print("\n[EXPECTED FAILURE] InvalidSubjectError raised:")
        print("    ", exc)

    # --- Failure path: token has no `sub` but we REQUIRE one -------------
    # Important: passing `subject=` alone validates the VALUE when `sub` is
    # present, but it does NOT force the claim to exist. To demand presence,
    # combine it with options={"require": [...]}.
    no_sub = jwt.encode({"iss": "https://auth.example.com"}, SECRET, algorithm="HS256")
    try:
        jwt.decode(
            no_sub,
            SECRET,
            algorithms=["HS256"],
            subject=EXPECTED_SUBJECT,
            options={"require": ["sub"]},
        )
    except jwt.MissingRequiredClaimError as exc:
        print("\n[EXPECTED FAILURE] MissingRequiredClaimError raised:")
        print("    ", exc)
        print("    `subject=` checks the value; `require` guarantees presence.")


if __name__ == "__main__":
    main()
