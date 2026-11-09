"""
07 · ECDSA · 03 — Signing & verifying with ES384
=================================================

**ES384** = ECDSA using the **P-384** curve (SECP384R1) with **SHA-384**.

Step up from ES256: a larger curve and a larger hash, giving a higher security
margin at the cost of slightly larger keys and signatures. Cloud providers
often use ES384 for high-assurance signing keys.

The same iron rule applies — **the algorithm dictates the curve**:
ES384 must be paired with a SECP384R1 key. A P-256 key will NOT work.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def main() -> None:
    # ES384 is bound to the P-384 curve. Generate the matching key.
    private_key = ec.generate_private_key(ec.SECP384R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    print("Curve in use:", private_key.curve.name, "(key size:", private_key.key_size, "bits)")

    payload = {"sub": "bob", "tier": "high-assurance"}

    token = jwt.encode(payload, private_pem, algorithm="ES384")
    print("\nES384 token (curve P-384 + SHA-384):")
    print(token)

    print("\nJOSE header:", jwt.get_unverified_header(token))

    decoded = jwt.decode(token, public_pem, algorithms=["ES384"])
    print("Verified payload:", decoded)


if __name__ == "__main__":
    main()
