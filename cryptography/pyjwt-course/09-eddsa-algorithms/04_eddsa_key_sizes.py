"""
09 · EdDSA · 04 — EdDSA key sizes: tiny and fast
================================================

EdDSA keys are astonishingly small. An Ed25519 **public key is just 32 raw
bytes** — the actual point on Curve25519. Compare that with a 2048-bit RSA
public key (256-byte modulus) or even a P-256 EC key.

This script prints:
    - the raw (Encoding.Raw) Ed25519 public key and its length (32 bytes)
    - the PEM-wrapped Ed25519 public key (slightly larger due to ASN.1 framing)
    - a side-by-side size comparison against EC P-256 and RSA-2048 PEMs

Small keys + deterministic signing + no big-integer math = EdDSA is also one of
the **fastest** signature schemes, which is why it's popular for high-volume
token issuance and constrained devices.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> None:
    ed_key = Ed25519PrivateKey.generate()
    ed_pub = ed_key.public_key()

    # RAW encoding gives the bare 32-byte public key point.
    ed_pub_raw = ed_pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    ed_pub_pem = ed_pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    print("=" * 70)
    print("Ed25519 PUBLIC KEY")
    print("=" * 70)
    print("Raw bytes length:", len(ed_pub_raw), "bytes  (the bare curve point)")
    print("Raw bytes (hex) :", ed_pub_raw.hex())
    print("\nPEM form:")
    print(ed_pub_pem.decode())

    # --- size comparison against EC P-256 and RSA-2048 (PEM public keys) ---
    ec_pub_pem = (
        ec.generate_private_key(ec.SECP256R1())
        .public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    rsa_pub_pem = (
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        .public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

    print("=" * 70)
    print("PUBLIC-KEY PEM SIZE COMPARISON")
    print("=" * 70)
    print(f"  Ed25519  : {len(ed_pub_pem):>5} bytes  (raw key only 32 bytes!)")
    print(f"  EC P-256 : {len(ec_pub_pem):>5} bytes")
    print(f"  RSA-2048 : {len(rsa_pub_pem):>5} bytes")

    print("\nEdDSA: smallest keys, fastest signing, hard to misuse.")


if __name__ == "__main__":
    main()
