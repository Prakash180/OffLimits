"""
08 · RSA-PSS · 04 — PSS vs PKCS#1 v1.5  (PS* vs RS*)
===================================================

Two padding schemes, one RSA key. Which should you choose?

  ┌─────────────┬──────────────────────────┬─────────────────────────────┐
  │             │ RS*  (PKCS#1 v1.5)        │ PS*  (RSASSA-PSS)           │
  ├─────────────┼──────────────────────────┼─────────────────────────────┤
  │ Padding     │ PKCS#1 v1.5 (1993)        │ PSS (provably secure)        │
  │ Randomness  │ Deterministic             │ Probabilistic (random salt)  │
  │ Status      │ Legacy, still widely used │ Modern, recommended for new  │
  │ Security    │ Adequate, older proofs    │ Stronger security reduction  │
  │ Same key?   │ ────────  yes, both schemes share one RSA keypair  ──── │
  └─────────────┴──────────────────────────┴─────────────────────────────┘

Guidance: for NEW systems prefer **PS256/PS384/PS512**. Keep **RS256** when you
must interoperate with older verifiers that don't understand PSS (still the
default in much of the OAuth/OIDC ecosystem).

This script signs one payload with RS256 and PS256 using the SAME key and
verifies both.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def main() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    payload = {"sub": "dave"}

    rs = jwt.encode(payload, private_pem, algorithm="RS256")
    ps = jwt.encode(payload, private_pem, algorithm="PS256")

    print("RS256 (PKCS#1 v1.5, deterministic, legacy):")
    print("  ", rs)
    print("   verified ->", jwt.decode(rs, public_pem, algorithms=["RS256"]))

    print("\nPS256 (RSASSA-PSS, randomised, modern):")
    print("  ", ps)
    print("   verified ->", jwt.decode(ps, public_pem, algorithms=["PS256"]))

    print("\nSame RSA key, two padding schemes. Prefer PS* for new designs.")


if __name__ == "__main__":
    main()
