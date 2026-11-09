"""
07 · ECDSA · 05 — Signing & verifying with ES256K  (Bitcoin's curve)
====================================================================

**ES256K** = ECDSA using the **secp256k1** curve with **SHA-256**.

The trailing **K** stands for *Koblitz* — the secp256k1 curve is a special
Koblitz curve famous for being the signing curve of **Bitcoin** and **Ethereum**.
It is a *different* curve from the NIST P-256 (SECP256R1) used by ES256, even
though both are 256-bit and both use SHA-256.

    ES256   ->  SECP256R1   (NIST "P-256", the random/prime curve)
    ES256K  ->  SECP256K1   (Koblitz curve, Bitcoin/Ethereum)

ES256K was added to the JOSE registry largely to support blockchain / DID
(decentralised identity) use cases. PyJWT supports it out of the box.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def main() -> None:
    # secp256k1 — the Koblitz curve. Note the 'K' suffix in SECP256K1.
    private_key = ec.generate_private_key(ec.SECP256K1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    print("Curve in use:", private_key.curve.name, "(Bitcoin / Ethereum curve)")

    payload = {"sub": "dave", "wallet": "0xDEADBEEF", "alg_note": "Koblitz curve"}

    token = jwt.encode(payload, private_pem, algorithm="ES256K")
    print("\nES256K token (secp256k1 + SHA-256):")
    print(token)

    print("\nJOSE header:", jwt.get_unverified_header(token))

    decoded = jwt.decode(token, public_pem, algorithms=["ES256K"])
    print("Verified payload:", decoded)


if __name__ == "__main__":
    main()
