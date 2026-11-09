"""04 · options={"verify_aud": False}.

When a token carries an `aud` claim, PyJWT verifies it *if* you pass
``audience=``. But if you pass neither `audience=` nor disable the check, a
token containing `aud` can raise on decode in some flows. Setting
``options={"verify_aud": False}`` explicitly skips audience validation.

⚠️ Risk: skipping `aud` lets a token minted for another service be accepted by
yours (token "audience confusion"). Only skip it when you have another reason
to trust the token's intended target.

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/04_options_verify_aud.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    token = jwt.encode(
        {"sub": "user-123", "aud": "https://api.example.com"},
        SECRET,
        algorithm="HS256",
    )

    # --- Verifying audience normally: must match -------------------------
    ok = jwt.decode(token, SECRET, algorithms=["HS256"], audience="https://api.example.com")
    print("[CHECKED] Correct audience accepted:", ok["aud"])

    try:
        jwt.decode(token, SECRET, algorithms=["HS256"], audience="https://other.example.com")
    except jwt.InvalidAudienceError as exc:
        print("[CHECKED] Wrong audience rejected:", exc)

    # --- Skip the audience check entirely --------------------------------
    skipped = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        options={"verify_aud": False},
    )
    print("\n[verify_aud=False] Decoded without checking `aud`:")
    print("    ", skipped)
    print("    ⚠️ Any audience is now accepted — beware token confusion.")


if __name__ == "__main__":
    main()
