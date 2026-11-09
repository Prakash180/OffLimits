"""05 · options={"require": [...]} — demand specific claims.

Validating a claim's *value* only happens when the claim exists. To guarantee a
claim is even **present**, list it under ``options={"require": [...]}``. If any
required claim is missing, PyJWT raises
:class:`jwt.MissingRequiredClaimError` *before* checking values.

This is the right way to enforce, e.g., "every token MUST have `exp`, `iss`,
and `sub`".

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/05_require_claims.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"
REQUIRED = ["exp", "iss", "sub"]


def main() -> None:
    now = datetime.now(UTC)

    # --- A complete token satisfies the requirement ----------------------
    complete = jwt.encode(
        {
            "iss": "https://auth.example.com",
            "sub": "user-123",
            "exp": now + timedelta(minutes=10),
        },
        SECRET,
        algorithm="HS256",
    )
    decoded = jwt.decode(
        complete,
        SECRET,
        algorithms=["HS256"],
        options={"require": REQUIRED},
    )
    print("[OK] All required claims present:", sorted(decoded.keys()))

    # --- A token missing `iss` is rejected -------------------------------
    missing_iss = jwt.encode(
        {"sub": "user-123", "exp": now + timedelta(minutes=10)},
        SECRET,
        algorithm="HS256",
    )
    try:
        jwt.decode(
            missing_iss,
            SECRET,
            algorithms=["HS256"],
            options={"require": REQUIRED},
        )
    except jwt.MissingRequiredClaimError as exc:
        print("\n[EXPECTED FAILURE] MissingRequiredClaimError:")
        print("    ", exc)
        print("    `require` guarantees presence; value checks come after.")


if __name__ == "__main__":
    main()
