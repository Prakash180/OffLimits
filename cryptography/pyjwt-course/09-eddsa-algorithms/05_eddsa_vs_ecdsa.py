"""
09 · EdDSA · 05 — EdDSA vs ECDSA, head to head
==============================================

EdDSA and ECDSA are both elliptic-curve signature schemes, but they differ in
ways that matter for real systems:

  ┌────────────────────┬───────────────────────────┬──────────────────────────┐
  │                    │ ECDSA (ES256, ES384, …)    │ EdDSA (Ed25519/Ed448)    │
  ├────────────────────┼───────────────────────────┼──────────────────────────┤
  │ Randomness at sign │ REQUIRES secure RNG nonce  │ Deterministic (no RNG)   │
  │ Misuse risk        │ Bad nonce -> key leak      │ Resistant by design      │
  │ Curve choice       │ alg fixes the curve        │ curve fixed by key type  │
  │ JWT alg string     │ ES256 / ES384 / ES512 / …  │ "EdDSA" (both flavours)  │
  │ Speed              │ Fast                       │ Typically faster         │
  │ Determinism        │ No (randomised)            │ Yes                      │
  └────────────────────┴───────────────────────────┴──────────────────────────┘

The big practical win for EdDSA: removing the random-nonce requirement
eliminates an entire category of devastating implementation bugs.

This script signs & verifies a token with BOTH schemes so you can see them
working back to back.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def pem_pair_from(private_key) -> tuple[bytes, bytes]:
    priv = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return priv, pub


def main() -> None:
    payload = {"sub": "dave"}

    # --- ECDSA (ES256 on P-256) ---
    es_priv, es_pub = pem_pair_from(ec.generate_private_key(ec.SECP256R1()))
    es_token = jwt.encode(payload, es_priv, algorithm="ES256")
    es_decoded = jwt.decode(es_token, es_pub, algorithms=["ES256"])

    print("ECDSA  (ES256, needs secure RNG per signature):")
    print("  header :", jwt.get_unverified_header(es_token))
    print("  token  :", es_token)
    print("  verify :", es_decoded)

    # --- EdDSA (Ed25519) ---
    ed_priv, ed_pub = pem_pair_from(Ed25519PrivateKey.generate())
    ed_token = jwt.encode(payload, ed_priv, algorithm="EdDSA")
    ed_decoded = jwt.decode(ed_token, ed_pub, algorithms=["EdDSA"])

    print("\nEdDSA  (Ed25519, deterministic, misuse-resistant):")
    print("  header :", jwt.get_unverified_header(ed_token))
    print("  token  :", ed_token)
    print("  verify :", ed_decoded)

    print("\nBoth are elliptic-curve schemes; EdDSA removes the RNG footgun and")
    print("uses one alg string ('EdDSA') regardless of curve.")


if __name__ == "__main__":
    main()
