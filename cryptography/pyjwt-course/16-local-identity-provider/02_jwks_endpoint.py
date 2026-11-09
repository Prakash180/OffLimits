"""
02 · The JWKS endpoint — how clients learn the provider's public keys
=====================================================================

A provider signs tokens with a PRIVATE key and publishes the matching PUBLIC
key as a JWK (JSON Web Key) in a JWKS (JSON Web Key Set) at ``jwks_uri``.

Each JWK carries:

* ``kty`` — key type (``RSA`` here).
* ``n`` / ``e`` — the RSA public modulus and exponent (the actual key material).
* ``kid`` — key id; the JWT header's ``kid`` points at exactly one of these.
* ``use`` / ``alg`` — intended use (``sig``) and algorithm (``RS256``).

Our IdP publishes TWO keys at once (``current`` + ``next``) so that validation
keeps working across a key rotation (see script 08).

Run:
    uv run python pyjwt-course/16-local-identity-provider/02_jwks_endpoint.py
"""

import json

from idp.client import LocalIdPClient


def main() -> None:
    client = LocalIdPClient()
    jwks = client.jwks()

    print("=" * 72)
    print("JWKS  (GET /jwks.json)  — public verification keys only")
    print("=" * 72)

    for i, jwk in enumerate(jwks["keys"], start=1):
        preview = dict(jwk)
        # The modulus `n` is huge; truncate it for readable output.
        preview["n"] = preview["n"][:32] + "...(truncated)"
        print(f"\nKey #{i}:")
        print(json.dumps(preview, indent=2))

    print("\n" + "=" * 72)
    print("FIELD-BY-FIELD")
    print("=" * 72)
    print("• kty=RSA   the key is an RSA key")
    print("• n, e      the public modulus + exponent (the verifiable key material)")
    print("• kid       the id a token's header names so clients pick THIS key")
    print("• use=sig   this key is for signature verification")
    print("• alg=RS256 RSASSA-PKCS1-v1_5 using SHA-256")

    kids = [k["kid"] for k in jwks["keys"]]
    print(f"\nPublished kids: {kids}")
    print("Two keys are advertised so a freshly-rotated key is already trusted")
    print("by clients that cached the JWKS a moment ago.")

    assert len(jwks["keys"]) == 2
    assert all(k["kty"] == "RSA" and k["use"] == "sig" for k in jwks["keys"])
    print("\nOK ✔  JWKS contains two well-formed RSA signing keys.")


if __name__ == "__main__":
    main()
