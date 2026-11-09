"""03 · Building a JWKS document.

A **JWKS** (JSON Web Key *Set*, RFC 7517) is simply a JSON object with one field,
``keys``, whose value is a list of JWKs:

    {"keys": [ <jwk1>, <jwk2>, ... ]}

This is what identity providers publish at their ``jwks_uri`` (e.g.
``https://.../discovery/v2.0/keys``). Having *multiple* keys in the set is the
whole point: it lets a provider serve an old key and a new key simultaneously
during rotation, so tokens signed by either remain verifiable.

Each key needs a unique ``kid`` so tokens can reference it. ``to_jwk`` doesn't add
a ``kid`` for us, so we attach one to each JWK ourselves.

This script generates two RSA keypairs and assembles a two-key JWKS, entirely
locally.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/11-jwks-and-key-rotation/03_build_a_jwks.py
"""

import json

from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


def public_jwk(public_key, kid: str) -> dict:
    """Convert an RSA public key to a JWK dict and tag it with kid/use/alg."""
    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    # Add the metadata a real JWKS carries.
    jwk["kid"] = kid
    jwk["use"] = "sig"   # this key is for signatures (not encryption)
    jwk["alg"] = "RS256"
    return jwk


def main() -> None:
    # Two independent keypairs.
    key_a = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_b = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    jwks = {
        "keys": [
            public_jwk(key_a.public_key(), kid="key-a"),
            public_jwk(key_b.public_key(), kid="key-b"),
        ]
    }

    print("JWKS document ({'keys': [...]}):")
    print(json.dumps(jwks, indent=2))
    print()

    print(f"Number of keys in the set: {len(jwks['keys'])}")
    print(f"kids present: {[k['kid'] for k in jwks['keys']]}")
    print()
    print("✅ A JWKS is just a list of JWKs under a 'keys' field, each with its own kid.")


if __name__ == "__main__":
    main()
