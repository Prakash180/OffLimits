"""
07 · ECDSA · 04 — Signing & verifying with ES512  (mind the 512 vs 521!)
========================================================================

**ES512** = ECDSA using the **P-521** curve (SECP521R1) with **SHA-512**.

⚠️  THE CLASSIC GOTCHA  ⚠️
The JWT algorithm is spelled **ES512** but the underlying curve is **P-521**
(five-hundred-and-TWENTY-ONE), *not* P-512. There is no such thing as a P-512
curve. The "512" in the algorithm name refers to the **SHA-512 hash**, while
the curve is the oddly-sized 521-bit NIST curve.

So when you read "ES512":
    - hash      = SHA-512      (the 512)
    - curve     = SECP521R1    (P-521, the 521)

Mixing these up — e.g. searching for a "SECP512R1" that doesn't exist — is a
rite of passage. This script generates the *correct* SECP521R1 key.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def main() -> None:
    # NOTE: SECP521R1, not "SECP512R1" — the latter does not exist.
    private_key = ec.generate_private_key(ec.SECP521R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    print("Algorithm name : ES512")
    print("Hash function  : SHA-512  <- the '512' in the name")
    print("Curve actually : ", private_key.curve.name, " <- P-521, NOT P-512!")
    print("Key size (bits):", private_key.key_size)

    payload = {"sub": "carol", "note": "ES512 uses the P-521 curve"}

    token = jwt.encode(payload, private_pem, algorithm="ES512")
    print("\nES512 token:")
    print(token)

    print("\nJOSE header:", jwt.get_unverified_header(token))

    decoded = jwt.decode(token, public_pem, algorithms=["ES512"])
    print("Verified payload:", decoded)


if __name__ == "__main__":
    main()
