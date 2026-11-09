"""04 · Loading a JWKS with ``jwt.PyJWKSet.from_dict``.

You *could* parse a JWKS by hand and call ``RSAAlgorithm.from_jwk`` on each entry
— but PyJWT gives you a purpose-built class. ``jwt.PyJWKSet.from_dict(jwks)``
takes the raw JWKS dict and returns a ``PyJWKSet`` whose ``.keys`` is a list of
``PyJWK`` objects. Each ``PyJWK`` lazily turns its JWK into a real key, exposed as
``.key`` (ready to hand straight to ``jwt.decode``).

This script builds a local JWKS, loads it with ``from_dict``, and shows two ways
to reach a key:
- iterating ``jwks_set.keys`` and reading each ``.key_id`` / ``.key``;
- indexing by kid with ``jwks_set[kid]``.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/11-jwks-and-key-rotation/04_pyjwkset_from_dict.py
"""

import json

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


def public_jwk(public_key, kid: str) -> dict:
    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return jwk


def main() -> None:
    key_a = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_b = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    jwks = {
        "keys": [
            public_jwk(key_a.public_key(), "key-a"),
            public_jwk(key_b.public_key(), "key-b"),
        ]
    }

    # Load the whole set in one call.
    jwks_set = jwt.PyJWKSet.from_dict(jwks)
    print(f"Loaded a PyJWKSet with {len(jwks_set.keys)} PyJWK(s).")
    print()

    # Way 1: iterate .keys
    print("Iterating jwks_set.keys:")
    for pyjwk in jwks_set.keys:
        print(f"  kid={pyjwk.key_id!r:10} -> key object {type(pyjwk.key).__name__}")
    print()

    # Way 2: index by kid (PyJWKSet supports __getitem__).
    chosen = jwks_set["key-b"]
    print(f"jwks_set['key-b'] -> PyJWK with kid={chosen.key_id!r}")
    print(f"  chosen.key is a usable verification key: {type(chosen.key).__name__}")
    print()
    print("✅ PyJWKSet.from_dict parses a JWKS and exposes ready-to-use PyJWK keys.")


if __name__ == "__main__":
    main()
