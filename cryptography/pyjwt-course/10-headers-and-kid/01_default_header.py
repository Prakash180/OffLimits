"""01 · The default JOSE header.

Every JWT begins with a *header* — a small JSON object, base64url-encoded, that
tells a verifier **how** to process the token. When you call ``jwt.encode()``
without specifying any extra headers, PyJWT writes a minimal default:

    {"alg": "HS256", "typ": "JWT"}

- ``alg`` — the signing algorithm. PyJWT *requires* this and uses it (after you
  whitelist it in ``decode(algorithms=[...])``) to know how to verify.
- ``typ`` — the media type of the token itself. ``"JWT"`` is the conventional
  default.

This script signs a token and reads the header back with
``jwt.get_unverified_header`` — which decodes the header **without** checking the
signature (perfectly safe here, the header is public anyway).

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/10-headers-and-kid/01_default_header.py
"""

import json

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"


def main() -> None:
    # Encode with NO explicit headers — PyJWT supplies the defaults.
    token = jwt.encode({"some": "payload"}, SECRET, algorithm="HS256")
    print("Encoded token:")
    print(token)
    print()

    # get_unverified_header decodes ONLY the first segment (the header).
    # It does not validate the signature — and it doesn't need the secret.
    header = jwt.get_unverified_header(token)
    print("Default header (decoded):")
    print(json.dumps(header, indent=2))
    print()

    # Prove the defaults are exactly what we expect.
    assert header["alg"] == "HS256", "alg should default to the chosen algorithm"
    assert header["typ"] == "JWT", "typ should default to 'JWT'"
    print("✅ Confirmed default header: {'alg': 'HS256', 'typ': 'JWT'}")


if __name__ == "__main__":
    main()
