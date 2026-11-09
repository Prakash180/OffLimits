"""
07 · ECDSA · 02 — Signing & verifying with ES256
=================================================

**ES256** = ECDSA using the **P-256** curve (SECP256R1) with **SHA-256**.

It is by far the most widely deployed ECDSA JWT algorithm — it's what most
OAuth2 / OpenID Connect providers reach for when they want elliptic-curve
tokens. The "256" refers to *both* the curve size (P-256) and the hash
(SHA-256); for ES256 they happen to line up neatly.

Key fact to memorise:  **ES256 REQUIRES a P-256 key.**  Hand PyJWT a key on a
different curve and signing will fail. We'll prove that gotcha in script 06.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def make_p256_pems() -> tuple[bytes, bytes]:
    """Generate a P-256 keypair and return (private_pem, public_pem)."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def main() -> None:
    private_pem, public_pem = make_p256_pems()

    payload = {"sub": "alice", "role": "admin", "iss": "es256-demo"}

    # SIGN: PyJWT accepts the PEM bytes directly and signs with the private key.
    token = jwt.encode(payload, private_pem, algorithm="ES256")
    print("=" * 70)
    print("ES256 token (curve P-256 + SHA-256):")
    print(token)
    print("=" * 70)

    # The JOSE header records the algorithm so verifiers know what to expect.
    header = jwt.get_unverified_header(token)
    print("\nDecoded JOSE header:", header)  # -> {'alg': 'ES256', 'typ': 'JWT'}

    # VERIFY: use the PUBLIC key. We must whitelist the expected algorithm.
    decoded = jwt.decode(token, public_pem, algorithms=["ES256"])
    print("Verified payload:", decoded)

    # The signature is short — ECDSA produces compact signatures.
    signature_b64 = token.split(".")[2]
    print("\nSignature segment length (base64url chars):", len(signature_b64))


if __name__ == "__main__":
    main()
