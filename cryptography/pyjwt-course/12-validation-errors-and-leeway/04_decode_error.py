"""04 · ``DecodeError`` — the token is malformed.

Before PyJWT can even *check* a signature, the string has to *look* like a JWT:
three base64url segments joined by dots, with a valid JSON header and payload.
Hand it ``"not.a.jwt"`` or other garbage and it fails structurally with
``DecodeError`` — distinct from a signature that's present but wrong
(``InvalidSignatureError``) or a token that's well-formed but expired
(``ExpiredSignatureError``).

This script throws several kinds of malformed input at ``decode``.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/04_decode_error.py
"""

import jwt

SECRET = "teaching-secret-key"

# A grab-bag of structurally broken "tokens".
BAD_TOKENS = {
    "not enough segments": "not.a.jwt",
    "totally not a token": "hello world",
    "header not base64url/JSON": "@@@.@@@.@@@",
    "empty string": "",
}


def main() -> None:
    for label, bad in BAD_TOKENS.items():
        try:
            jwt.decode(bad, SECRET, algorithms=["HS256"])
        except jwt.DecodeError as e:
            print(f"❌ {label!r:30} -> DecodeError: {e}")
        except jwt.InvalidTokenError as e:
            # Still in the family; show it explicitly if a subtype fires.
            print(f"❌ {label!r:30} -> {type(e).__name__}: {e}")
        else:
            print(f"?? {label!r:30} -> unexpectedly decoded")

    print()
    print("✅ DecodeError = 'this isn't a valid JWT structurally', before any crypto.")


if __name__ == "__main__":
    main()
