"""
04 · Symmetric vs. asymmetric — one shared secret vs. a key pair
================================================================

JWT signing algorithms split into two worlds:

* **Symmetric (HMAC / HS256)** — ONE secret is used to BOTH sign and verify.
  Everyone who can verify can also forge. Great when issuer == verifier.

* **Asymmetric (RSA/ECDSA/EdDSA — RS256/ES256/EdDSA)** — a PRIVATE key signs,
  a PUBLIC key verifies. You can hand the public key to the whole world and they
  can verify your tokens but can NEVER mint new ones. Essential for third-party
  verification (e.g. Microsoft Entra ID publishes public keys via JWKS).

This script demonstrates both with PyJWT and prints a tradeoff table.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/04_symmetric_vs_asymmetric.py
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def make_rsa_keypair() -> tuple[str, str]:
    """Generate an RSA-2048 key pair, returned as PEM strings."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return private_pem, public_pem


def main() -> None:
    payload = {"sub": "alice", "role": "admin"}

    print("=" * 70)
    print("SYMMETRIC (HS256) — same secret signs AND verifies")
    print("=" * 70)
    shared_secret = "the-one-shared-secret-at-least-32-bytes-long!!"
    sym_token = jwt.encode(payload, shared_secret, algorithm="HS256")
    print(f"signed with secret : {shared_secret!r}")
    print(f"token              : {sym_token[:50]}...")
    sym_decoded = jwt.decode(sym_token, shared_secret, algorithms=["HS256"])
    print(f"verified with SAME secret -> {sym_decoded}")
    print("Anyone who can verify (has the secret) can also forge new tokens.\n")

    print("=" * 70)
    print("ASYMMETRIC (RS256) — private key signs, public key verifies")
    print("=" * 70)
    private_pem, public_pem = make_rsa_keypair()
    asym_token = jwt.encode(payload, private_pem, algorithm="RS256")
    print("signed with PRIVATE key (kept secret by issuer)")
    print(f"token              : {asym_token[:50]}...")
    asym_decoded = jwt.decode(asym_token, public_pem, algorithms=["RS256"])
    print(f"verified with PUBLIC key (shareable) -> {asym_decoded}")

    # Prove the public key CANNOT sign — the whole point of asymmetric crypto.
    try:
        jwt.encode(payload, public_pem, algorithm="RS256")
        print("UNEXPECTED: public key was able to sign?!")
    except Exception as ex:  # noqa: BLE001 - demonstrating the failure
        print(f"public key tries to SIGN -> rejected: {type(ex).__name__}")
        print("Public key verifies only; it can never mint tokens.\n")

    print("=" * 70)
    print("TRADEOFF TABLE")
    print("=" * 70)
    rows = [
        ("Keys", "1 shared secret", "private + public pair"),
        ("Who can sign", "anyone with secret", "only private-key holder"),
        ("Who can verify", "anyone with secret", "anyone with public key"),
        ("Distribute to verifiers", "secret (risky!)", "public key (safe)"),
        ("Speed", "very fast", "slower (big-number math)"),
        ("3rd-party verify", "no (secret leaks)", "yes (publish JWKS)"),
        ("Key size", "32+ random bytes", "2048-bit RSA / 256-bit EC"),
        ("JWT algs", "HS256/384/512", "RS*/ES*/PS*/EdDSA"),
    ]
    print(f"{'Property':<24}{'Symmetric (HMAC)':<22}{'Asymmetric (pubkey)'}")
    print("-" * 70)
    for prop, sym, asym in rows:
        print(f"{prop:<24}{sym:<22}{asym}")

    print("\nRule of thumb: same service issues+verifies -> HS256 is fine.")
    print("Others must verify your tokens -> use RS256/ES256/EdDSA + JWKS.")


if __name__ == "__main__":
    main()
