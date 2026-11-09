"""
07 · ECDSA · 06 — Each ES algorithm is BOUND to one specific curve
==================================================================

This is the single most important operational fact about ECDSA in JWTs:

    ES256   <->  SECP256R1  (P-256)
    ES384   <->  SECP384R1  (P-384)
    ES512   <->  SECP521R1  (P-521)
    ES256K  <->  SECP256K1  (secp256k1)

You cannot mix and match. If you generate a **P-256** key and try to sign with
**ES384**, PyJWT (via the cryptography backend) rejects it, because ES384's
SHA-384 + P-384 contract is violated. The RFC 7518 spec ties each algorithm to
exactly one curve so that verifiers know precisely what to validate.

This script demonstrates the failure *and* the success, catching the error so
the script still exits 0.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def pem_pair(curve: ec.EllipticCurve) -> tuple[bytes, bytes]:
    key = ec.generate_private_key(curve)
    priv = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return priv, pub


def main() -> None:
    payload = {"sub": "erin"}

    # A P-256 key — correct for ES256, WRONG for ES384.
    p256_priv, _ = pem_pair(ec.SECP256R1())

    print("=" * 70)
    print("Attempt 1: sign with ES384 using a P-256 key  (EXPECTED TO FAIL)")
    print("=" * 70)
    try:
        jwt.encode(payload, p256_priv, algorithm="ES384")
        print("!! Unexpected success — this should not happen.")
    except Exception as exc:  # noqa: BLE001 — we want to teach via the message
        print("Caught", type(exc).__name__, ":", exc)
        print("Reason: ES384 demands a P-384 (SECP384R1) key; we gave it P-256.")

    print("\n" + "=" * 70)
    print("Attempt 2: sign with ES384 using the CORRECT P-384 key  (SUCCEEDS)")
    print("=" * 70)
    p384_priv, p384_pub = pem_pair(ec.SECP384R1())
    token = jwt.encode(payload, p384_priv, algorithm="ES384")
    decoded = jwt.decode(token, p384_pub, algorithms=["ES384"])
    print("Token:", token)
    print("Verified payload:", decoded)

    print("\nLesson: match the curve to the algorithm — always.")


if __name__ == "__main__":
    main()
