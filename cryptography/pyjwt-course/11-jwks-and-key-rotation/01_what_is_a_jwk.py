"""01 · What is a JWK?

A **JWK** (JSON Web Key, RFC 7517) is just a JSON representation of a
cryptographic key. Instead of a PEM blob, a key becomes a JSON object whose
fields depend on the key type (``kty``):

For an RSA public key you'll see:
- ``kty`` — key type, ``"RSA"``.
- ``n``   — the modulus (base64url).
- ``e``   — the public exponent (base64url, usually ``"AQAB"`` = 65537).
- optional metadata like ``kid`` (key id), ``use`` (``"sig"``), ``alg``.

Why bother? Because JSON is web-native. A server can publish its public keys as a
JWK **Set** at an HTTPS URL, and any client can fetch and parse them with nothing
but a JSON parser — no PEM/ASN.1 tooling required. That's the whole basis of
JWKS.

PyJWT can produce a JWK straight from a cryptography public-key object via
``jwt.algorithms.RSAAlgorithm.to_jwk``. This script generates a keypair and
prints the resulting JWK.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/11-jwks-and-key-rotation/01_what_is_a_jwk.py
"""

import json

from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


def main() -> None:
    # Generate an RSA keypair locally (no network, no files).
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # Convert the PUBLIC key into a JWK. to_jwk returns a JSON *string*.
    jwk_json = RSAAlgorithm.to_jwk(public_key)
    jwk = json.loads(jwk_json)

    print("RSA public key as a JWK:")
    print(json.dumps(jwk, indent=2))
    print()

    # Explain the fields we got back.
    print("Field-by-field:")
    print(f"  kty = {jwk['kty']!r}   (key type — RSA)")
    print(f"  e   = {jwk['e']!r}   (public exponent, base64url; 'AQAB' == 65537)")
    print(f"  n   = <{len(jwk['n'])} base64url chars>  (the 2048-bit modulus)")
    print()
    print("✅ A JWK is just a key expressed as JSON — web-native and easy to publish.")


if __name__ == "__main__":
    main()
