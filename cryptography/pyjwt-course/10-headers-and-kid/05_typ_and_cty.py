"""05 · ``typ`` and ``cty`` — token type vs. content type.

Two header parameters describe *what kind of thing* the token is:

- ``typ`` (type) — the media type of the **whole JWT object**. Conventionally
  ``"JWT"``. RFC 8725 / RFC 9068 recommend using an *explicit* type to prevent
  cross-service token confusion. For OAuth2 access tokens, RFC 9068 mandates
  ``typ="at+jwt"``. Other examples: ``"dpop+jwt"``, ``"logout+jwt"``.

- ``cty`` (content type) — the media type of the **payload**. You only need this
  when the payload is itself something structured that a recipient must be told
  how to interpret — most famously a *nested* JWT (a JWT whose payload is another
  JWT), where you'd set ``cty="JWT"``.

Rule of thumb: ``typ`` is about the envelope; ``cty`` is about the contents.

This script issues an access-token-style JWT with ``typ="at+jwt"`` and shows a
verifier explicitly *requiring* that type — a good defensive habit.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/10-headers-and-kid/05_typ_and_cty.py
"""

import json

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"


def main() -> None:
    # An OAuth2-style access token: RFC 9068 says typ MUST be "at+jwt".
    access_token = jwt.encode(
        {"sub": "user-123", "scope": "read:profile"},
        SECRET,
        algorithm="HS256",
        headers={"typ": "at+jwt"},
    )
    print("Access token header:")
    print(json.dumps(jwt.get_unverified_header(access_token), indent=2))
    print()

    # A defensive verifier: only accept tokens that declare the expected type.
    header = jwt.get_unverified_header(access_token)
    expected_typ = "at+jwt"
    if header.get("typ") != expected_typ:
        raise ValueError(f"Wrong token type: expected {expected_typ!r}")
    claims = jwt.decode(access_token, SECRET, algorithms=["HS256"])
    print(f"✅ typ check passed; verified access-token claims: {claims}")
    print()

    # cty demo: a token whose payload is described as JSON content.
    typed_payload = jwt.encode(
        {"data": {"nested": True}},
        SECRET,
        algorithm="HS256",
        headers={"cty": "application/json"},
    )
    print("Token declaring its payload content type (cty):")
    print(json.dumps(jwt.get_unverified_header(typed_payload), indent=2))
    print()
    print("Takeaway: typ = type of the envelope; cty = type of the payload.")


if __name__ == "__main__":
    main()
