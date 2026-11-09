"""
08 · RSA-PSS · 01 — Signing & verifying with PS256
==================================================

The **PS** family (PS256, PS384, PS512) is RSA signing using the modern
**RSASSA-PSS** padding scheme ("Probabilistic Signature Scheme").

    PS256 = RSA + PSS padding + SHA-256

It uses the *same* RSA keypair you'd use for RS256 — the only difference is the
padding/encoding step inside the signature. PSS is the cryptographically
preferred padding for new systems (RS* uses the older PKCS#1 v1.5 padding).

This script generates a fresh RSA-2048 keypair and does a PS256 round-trip.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def main() -> None:
    # RSA-2048 is the practical minimum modern size. PSS works with any RSA key.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    payload = {"sub": "alice", "scheme": "RSASSA-PSS"}

    # SIGN with the private key using PS256.
    token = jwt.encode(payload, private_pem, algorithm="PS256")
    print("=" * 70)
    print("PS256 token (RSA + PSS padding + SHA-256):")
    print(token)
    print("=" * 70)

    print("\nJOSE header:", jwt.get_unverified_header(token))  # alg == 'PS256'

    # VERIFY with the public key.
    decoded = jwt.decode(token, public_pem, algorithms=["PS256"])
    print("Verified payload:", decoded)


if __name__ == "__main__":
    main()
