"""
09 · EdDSA · 02 — Ed448 sign & verify
=====================================

Ed448 is the higher-security sibling of Ed25519:

    Ed448  — Curve448, ~224-bit security, 57-byte public keys, 114-byte sigs

You'd reach for Ed448 when you want a comfortable security margin beyond the
~128-bit level of Ed25519 (think very-long-lived signatures). It is slower and
produces larger signatures, but is still far more compact than RSA.

Just like Ed25519, the JWT algorithm string is **"EdDSA"** — the *key* (an
Ed448 key here) decides the underlying curve.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PrivateKey


def main() -> None:
    private_key = Ed448PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    payload = {"sub": "bob", "curve": "Ed448"}

    # Same "EdDSA" alg string as Ed25519 — the key type makes it Ed448.
    token = jwt.encode(payload, private_pem, algorithm="EdDSA")
    print("EdDSA / Ed448 token:")
    print(token)

    print("\nJOSE header:", jwt.get_unverified_header(token))

    decoded = jwt.decode(token, public_pem, algorithms=["EdDSA"])
    print("Verified payload:", decoded)

    print("\nSignature segment length (base64url chars):", len(token.split('.')[2]))
    print("(Larger than Ed25519's, but still tiny next to RSA.)")


if __name__ == "__main__":
    main()
