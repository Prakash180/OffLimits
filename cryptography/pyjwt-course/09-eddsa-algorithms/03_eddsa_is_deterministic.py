"""
09 · EdDSA · 03 — EdDSA is DETERMINISTIC
========================================

A defining property of EdDSA: signing is **deterministic**. The per-signature
"nonce" is derived deterministically from the private key and the message
(via a hash), so there is *no* reliance on an external random number generator
at signing time.

Consequences:
    - Signing the SAME payload twice with the SAME Ed25519 key produces the
      EXACT SAME token, byte-for-byte.
    - This sidesteps a whole class of catastrophic ECDSA failures, where a
      bad/repeated random nonce can leak the private key (famously, the 2010
      Sony PS3 ECDSA break).

Contrast:
    - ECDSA (ES256 etc.)  -> needs a fresh secure random nonce per signature.
    - RSASSA-PSS (PS256)  -> randomised (random salt) -> tokens differ.
    - EdDSA               -> deterministic -> tokens identical.

We sign the same payload twice with Ed25519 and show the tokens match.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> None:
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    payload = {"sub": "carol", "msg": "sign me twice"}

    token_a = jwt.encode(payload, private_pem, algorithm="EdDSA")
    token_b = jwt.encode(payload, private_pem, algorithm="EdDSA")

    print("=" * 70)
    print("Ed25519 — sign identical payload twice")
    print("=" * 70)
    print("token A:", token_a)
    print("token B:", token_b)
    print("\nTokens identical? ", token_a == token_b, " <- expect True (deterministic)")

    # Both verify, of course.
    jwt.decode(token_a, public_pem, algorithms=["EdDSA"])
    jwt.decode(token_b, public_pem, algorithms=["EdDSA"])
    print("Both verify correctly. ✔")

    print("\nDeterminism removes the 'must have good RNG at sign time' footgun")
    print("that plagues classic ECDSA.")


if __name__ == "__main__":
    main()
