"""
09 · EdDSA · 01 — Ed25519 sign & verify
=======================================

**EdDSA** (Edwards-curve Digital Signature Algorithm) is the newest signature
family in the JWT world and, for most new systems, the best default. It comes
in two flavours defined by their curve:

    Ed25519  — built on Curve25519,  ~128-bit security, 32-byte keys
    Ed448    — built on Curve448,    ~224-bit security, 57-byte keys

⚠️  In JWT, BOTH flavours use the SAME algorithm string: **"EdDSA"**.
There is no "Ed25519" alg value in the JOSE header — the header just says
`"alg": "EdDSA"`, and the *key type* (the curve baked into the key) determines
whether Ed25519 or Ed448 is actually used.

This script generates an Ed25519 keypair and does a round-trip.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> None:
    # Ed25519 keys take no parameters — the curve is fixed by definition.
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

    payload = {"sub": "alice", "curve": "Ed25519"}

    # Sign with algorithm="EdDSA" — note the header alg will be "EdDSA".
    token = jwt.encode(payload, private_pem, algorithm="EdDSA")
    print("=" * 70)
    print("EdDSA / Ed25519 token:")
    print(token)
    print("=" * 70)

    header = jwt.get_unverified_header(token)
    print("\nJOSE header:", header, " <- note alg is 'EdDSA', not 'Ed25519'")

    decoded = jwt.decode(token, public_pem, algorithms=["EdDSA"])
    print("Verified payload:", decoded)


if __name__ == "__main__":
    main()
