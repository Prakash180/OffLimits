"""
07 · ECDSA · 07 — ECDSA vs RSA: tiny keys, equivalent security
==============================================================

Why bother with elliptic curves at all? **Size and speed.**

A 256-bit EC key (P-256) offers roughly the same security level as a
**3072-bit** RSA key (~128-bit security). Even compared with a 2048-bit RSA key
(~112-bit security, *weaker* than P-256), the EC key and its signatures are
dramatically smaller. Smaller keys & signatures mean:

    - smaller tokens on the wire
    - less storage / bandwidth
    - faster signing on constrained devices

This script measures it concretely: PEM sizes for the public keys, and the
signature segment length of an actual JWT signed with each scheme.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa


def ec_pems() -> tuple[bytes, bytes]:
    key = ec.generate_private_key(ec.SECP256R1())
    return (
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
        key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )


def rsa_pems() -> tuple[bytes, bytes]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return (
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
        key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ),
    )


def sig_len(token: str) -> int:
    """Length of the base64url signature segment of a JWT."""
    return len(token.split(".")[2])


def main() -> None:
    ec_priv, ec_pub = ec_pems()
    rsa_priv, rsa_pub = rsa_pems()

    payload = {"sub": "frank"}

    es256 = jwt.encode(payload, ec_priv, algorithm="ES256")
    rs256 = jwt.encode(payload, rsa_priv, algorithm="RS256")

    # Sanity: both verify.
    jwt.decode(es256, ec_pub, algorithms=["ES256"])
    jwt.decode(rs256, rsa_pub, algorithms=["RS256"])

    print("=" * 70)
    print("PUBLIC KEY PEM SIZE")
    print("=" * 70)
    print(f"  EC P-256   : {len(ec_pub):>5} bytes")
    print(f"  RSA-2048   : {len(rsa_pub):>5} bytes")
    print(f"  RSA is {len(rsa_pub) / len(ec_pub):.1f}x larger for *weaker* security.")

    print("\n" + "=" * 70)
    print("JWT SIGNATURE SEGMENT SIZE (base64url chars)")
    print("=" * 70)
    print(f"  ES256 sig  : {sig_len(es256):>5}")
    print(f"  RS256 sig  : {sig_len(rs256):>5}")

    print("\n" + "=" * 70)
    print("WHOLE TOKEN SIZE")
    print("=" * 70)
    print(f"  ES256 token: {len(es256):>5} chars")
    print(f"  RS256 token: {len(rs256):>5} chars")

    print(
        "\nTakeaway: P-256 matches ~3072-bit RSA security, yet keys, signatures,"
        "\nand tokens are all far smaller. That is the ECDSA value proposition."
    )


if __name__ == "__main__":
    main()
