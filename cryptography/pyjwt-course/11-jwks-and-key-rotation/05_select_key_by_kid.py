"""05 · Selecting the right key by ``kid`` from a PyJWKSet.

Now we combine module 10's pattern with module 11's tools. The verifier holds a
``PyJWKSet`` (its local copy of the provider's JWKS). When a token arrives:

    1. ``get_unverified_header(token)`` -> read the ``kid``.
    2. Index the set: ``jwks_set[kid]`` -> the matching ``PyJWK``.
    3. ``jwt.decode(token, pyjwk.key, algorithms=["RS256"])`` -> verified claims.

This is the real JWKS verification flow, just with the JWKS coming from a local
dict instead of an HTTPS fetch. The selection logic is byte-for-byte what
``PyJWKClient`` does internally (see script 07).

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/11-jwks-and-key-rotation/05_select_key_by_kid.py
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
    # Provider side: two keys, both published in the JWKS.
    key_a = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_b = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks = {
        "keys": [
            public_jwk(key_a.public_key(), "key-a"),
            public_jwk(key_b.public_key(), "key-b"),
        ]
    }

    # Issue a token signed by key-b, advertising kid=key-b in the header.
    token = jwt.encode(
        {"user": "erin"}, key_b, algorithm="RS256", headers={"kid": "key-b"}
    )

    # Verifier side: load the public JWKS.
    jwks_set = jwt.PyJWKSet.from_dict(jwks)

    # 1. Read kid (unverified) to choose a key.
    kid = jwt.get_unverified_header(token)["kid"]
    print(f"Token advertises kid={kid!r}")

    # 2. Select the matching PyJWK.
    signing_key = jwks_set[kid]
    print(f"Selected PyJWK kid={signing_key.key_id!r} from the set of "
          f"{len(jwks_set.keys)} keys")

    # 3. Verify with that key.
    claims = jwt.decode(token, signing_key.key, algorithms=["RS256"])
    print(f"✅ Verified claims: {claims}")
    print()

    # Sanity check: the *other* key must NOT validate this token.
    other = jwks_set["key-a"]
    try:
        jwt.decode(token, other.key, algorithms=["RS256"])
    except jwt.InvalidSignatureError:
        print("Cross-check: key-a correctly FAILS to verify a key-b token "
              "(InvalidSignatureError).")


if __name__ == "__main__":
    main()
