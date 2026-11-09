"""
07 · ECDSA · 01 — Generate an EC (Elliptic Curve) keypair
==========================================================

ECDSA (Elliptic Curve Digital Signature Algorithm) is a public-key signature
scheme — just like RSA — but built on *elliptic curve* math instead of large
integer factorisation. The headline benefit: **equivalent security with much
smaller keys** (a 256-bit EC key is roughly as strong as a 3072-bit RSA key).

In JWT land, the ECDSA family is: ES256, ES384, ES512, ES256K. Each one is
*bound to a specific curve* (more on that in later scripts). This first script
just teaches the mechanics of creating an EC keypair with the `cryptography`
library and serialising it to PEM — the text format PyJWT happily consumes.

We use the **P-256** curve here (named SECP256R1 in `cryptography`), which is
the curve required by the most common ECDSA JWT algorithm, ES256.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Generate the private key on a named curve.
    #    The private key is the secret signing key; the matching public
    #    key (derived from it) is what verifiers use to check signatures.
    # ------------------------------------------------------------------
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    print("=" * 70)
    print("Generated an EC keypair on curve:", private_key.curve.name)
    print("Key size (bits):", private_key.key_size)
    print("=" * 70)

    # ------------------------------------------------------------------
    # 2. Serialise the PRIVATE key to PEM.
    #    - PKCS8 is the modern, standard container for private keys.
    #    - NoEncryption() means we don't wrap it in a passphrase (fine
    #      for a teaching demo; encrypt at rest in production!).
    # ------------------------------------------------------------------
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # ------------------------------------------------------------------
    # 3. Serialise the PUBLIC key to PEM.
    #    - SubjectPublicKeyInfo is the standard public-key container.
    # ------------------------------------------------------------------
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    print("\n--- PRIVATE KEY (PEM, PKCS8) ---")
    print(private_pem.decode())
    print("--- PUBLIC KEY (PEM, SubjectPublicKeyInfo) ---")
    print(public_pem.decode())

    # Notice how short these PEM blocks are compared with an RSA key —
    # that compactness is ECDSA's signature super-power (script 07).
    print("Private PEM length:", len(private_pem), "bytes")
    print("Public  PEM length:", len(public_pem), "bytes")


if __name__ == "__main__":
    main()
