"""07 · ``PyJWKClient`` explained (and reproduced without a network).

In production you rarely build a ``PyJWKSet`` by hand. Instead you point
``jwt.PyJWKClient`` at a provider's ``jwks_uri`` and it does the heavy lifting:

    - fetches the JWKS over HTTPS,
    - caches it (so you're not hitting the network on every request),
    - given a token, reads its ``kid`` and returns the matching signing key.

The canonical usage looks like this (NOT executed here — no network):

    # --- real-world PyJWKClient usage (reference only) -------------------
    # from jwt import PyJWKClient
    # jwks_client = PyJWKClient("https://issuer.example.com/.well-known/jwks.json")
    # signing_key = jwks_client.get_signing_key_from_jwt(token)
    # claims = jwt.decode(
    #     token,
    #     signing_key.key,
    #     algorithms=["RS256"],
    #     audience="my-api",
    #     issuer="https://issuer.example.com/",
    # )
    # --------------------------------------------------------------------

Since we have no network, this script reproduces ``get_signing_key_from_jwt``
manually against a LOCAL ``PyJWKSet`` — proving the client is just convenience
around the exact flow you already learned:

    get_unverified_header -> kid -> lookup in PyJWKSet -> signing_key.key -> decode

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/11-jwks-and-key-rotation/07_pyjwkclient_explained.py
"""

import json

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


def public_jwk(public_key, kid: str) -> dict:
    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return jwk


def get_signing_key_from_jwt_local(jwks_set: jwt.PyJWKSet, token: str) -> jwt.PyJWK:
    """A from-scratch reimplementation of PyJWKClient.get_signing_key_from_jwt.

    The real method does the same three steps — only its key source is an
    HTTPS-fetched, cached JWKS instead of our in-memory PyJWKSet.
    """
    kid = jwt.get_unverified_header(token)["kid"]   # 1. read kid (unverified)
    return jwks_set[kid]                            # 2. look it up in the set


def main() -> None:
    # Provider publishes a JWKS with two keys.
    key_a = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_b = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks = {
        "keys": [
            public_jwk(key_a.public_key(), "key-a"),
            public_jwk(key_b.public_key(), "key-b"),
        ]
    }
    jwks_set = jwt.PyJWKSet.from_dict(jwks)

    # A token signed by key-a.
    token = jwt.encode(
        {"sub": "frank", "scope": "read"},
        key_a,
        algorithm="RS256",
        headers={"kid": "key-a"},
    )

    print("Manual stand-in for PyJWKClient.get_signing_key_from_jwt:")
    signing_key = get_signing_key_from_jwt_local(jwks_set, token)
    print(f"  resolved signing key kid={signing_key.key_id!r}")

    # 3. Final verified decode — identical to the real-world snippet above.
    claims = jwt.decode(token, signing_key.key, algorithms=["RS256"])
    print(f"  ✅ verified claims: {claims}")
    print()
    print("PyJWKClient = (fetch JWKS over HTTPS + cache) wrapped around THIS flow.")
    print("See the commented snippet at the top of this file for real usage.")


if __name__ == "__main__":
    main()
