"""05 · ``InvalidAudienceError`` — this token isn't meant for you.

The ``aud`` (audience) claim names the intended recipient(s). When you call
``jwt.decode(..., audience=...)``, PyJWT checks that your expected audience is
listed in the token's ``aud``. If it isn't, you get ``InvalidAudienceError``.

This stops a token minted for *Service A* from being replayed against
*Service B* — even though both might trust the same issuer/key.

Two cases shown:
    - mismatch (token aud = "service-a", we expect "service-b") -> error;
    - match -> success.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/05_invalid_audience_error.py
"""

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"


def main() -> None:
    token = jwt.encode({"user": "ivan", "aud": "service-a"}, SECRET, algorithm="HS256")
    print("Token issued for audience 'service-a'.")
    print()

    # We are service-b: the audiences don't match.
    print("Verifying as 'service-b' (wrong audience):")
    try:
        jwt.decode(token, SECRET, algorithms=["HS256"], audience="service-b")
    except jwt.InvalidAudienceError as e:
        print(f"  ❌ Caught {type(e).__name__}: {e}")
        print("     Meaning: token's 'aud' doesn't include us -> reject.")
    print()

    # Verifying with the correct audience succeeds.
    claims = jwt.decode(token, SECRET, algorithms=["HS256"], audience="service-a")
    print(f"✅ As 'service-a' it verifies: {claims}")


if __name__ == "__main__":
    main()
