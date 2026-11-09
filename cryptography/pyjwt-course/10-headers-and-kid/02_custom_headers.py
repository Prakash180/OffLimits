"""02 · Custom header parameters.

The default header has just ``alg`` and ``typ``, but the JOSE spec lets you add
*any* header parameters you like. You pass them via the ``headers=`` argument to
``jwt.encode()``. The most important real-world one is ``kid`` (key ID), which
tells the verifier *which key* signed the token — the foundation of JWKS and key
rotation (covered in module 11).

Other common header params shown here:
- ``kid`` — key identifier, used to select a verification key.
- ``cty`` — content type, describes the *payload's* media type (e.g. nested JWT).
- a fully custom param (``"custom"``) — anything you want; verifiers ignore
  params they don't understand.

Note: PyJWT always sets ``alg`` itself from the ``algorithm=`` argument, so you
don't (and shouldn't) put ``alg`` in ``headers=``.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/10-headers-and-kid/02_custom_headers.py
"""

import json

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"


def main() -> None:
    custom_headers = {
        "kid": "key-1",            # which key signed this token
        "cty": "application/json",  # what the payload contains
        "custom": "x",             # arbitrary app-specific metadata
    }

    token = jwt.encode(
        {"some": "payload"},
        SECRET,
        algorithm="HS256",
        headers=custom_headers,
    )
    print("Encoded token with custom headers:")
    print(token)
    print()

    # Read them back. PyJWT merged our custom headers with the defaults
    # (alg + typ), so all five keys appear.
    header = jwt.get_unverified_header(token)
    print("Decoded header:")
    print(json.dumps(header, indent=2))
    print()

    assert header["kid"] == "key-1"
    assert header["cty"] == "application/json"
    assert header["custom"] == "x"
    assert header["alg"] == "HS256"  # PyJWT added this automatically
    print("✅ Custom headers round-tripped: kid, cty, custom (+ alg, typ).")


if __name__ == "__main__":
    main()
