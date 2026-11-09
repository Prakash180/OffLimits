"""
08 · RSA-PSS · 02 — PS384 and PS512
===================================

Just like PS256, the larger PSS variants pair RSA + PSS padding with a bigger
SHA-2 hash:

    PS384 = RSA + PSS + SHA-384
    PS512 = RSA + PSS + SHA-512

Crucially — unlike ECDSA, where the algorithm dictates the curve — **the RSA
key size is independent of the hash**. The *same* RSA-2048 key can produce
PS256, PS384, and PS512 signatures. You pick the hash strength via the
algorithm string; the key stays the same.

This script signs the same payload with both PS384 and PS512 using one key.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def main() -> None:
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

    payload = {"sub": "bob"}

    for alg in ("PS384", "PS512"):
        token = jwt.encode(payload, private_pem, algorithm=alg)
        header = jwt.get_unverified_header(token)
        decoded = jwt.decode(token, public_pem, algorithms=[alg])

        print("=" * 70)
        print(f"{alg}  (same RSA-2048 key, hash = SHA-{alg[2:]})")
        print("=" * 70)
        print("Header  :", header)
        print("Token   :", token)
        print("Verified:", decoded)
        print()

    print("One key, three hash strengths — the RSA key size is independent")
    print("of the chosen SHA-2 variant.")


if __name__ == "__main__":
    main()
