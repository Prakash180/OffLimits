"""02 · Round-tripping an RSA key through a JWK.

A JWK isn't a one-way export format — it's a faithful representation you can
convert *back* into a usable key. This is exactly what a verifier does: it
receives a JWK (as JSON), turns it into a public key, and verifies tokens with it.

The two functions:
- ``RSAAlgorithm.to_jwk(public_key)``  -> JWK JSON string.
- ``RSAAlgorithm.from_jwk(jwk_json)``  -> a cryptography public-key object.

This script:
    1. Generates an RSA keypair.
    2. Signs a token with the PRIVATE key (RS256).
    3. Exports the PUBLIC key to a JWK, then imports it back with ``from_jwk``.
    4. Verifies the token using the *round-tripped* key — proving it's identical.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/11-jwks-and-key-rotation/02_jwk_from_rsa_key.py
"""

import json

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


def main() -> None:
    # 1. Keypair.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # 2. Sign with the private key.
    token = jwt.encode({"user": "dave"}, private_key, algorithm="RS256")
    print("Token signed with RS256 private key:")
    print(token)
    print()

    # 3. Export public key -> JWK -> back to a key object.
    jwk_json = RSAAlgorithm.to_jwk(public_key)
    print("Public key as JWK:")
    print(json.dumps(json.loads(jwk_json), indent=2))
    print()

    roundtripped_key = RSAAlgorithm.from_jwk(jwk_json)

    # 4. Verify using the key we reconstructed from the JWK.
    claims = jwt.decode(token, roundtripped_key, algorithms=["RS256"])
    print(f"✅ Verified with round-tripped JWK key: {claims}")
    print("   to_jwk -> from_jwk preserves the key perfectly.")


if __name__ == "__main__":
    main()
