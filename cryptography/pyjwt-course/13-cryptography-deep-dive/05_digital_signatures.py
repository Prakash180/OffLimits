"""
05 · Digital signatures with raw RSA — the engine behind RS256
===============================================================

Before JWTs existed, there were digital signatures. RS256 is simply:

    RSA signature over SHA-256(  base64url(header) + "." + base64url(payload)  )

Here we strip JWT away entirely and use the ``cryptography`` library directly:

* **Sign** a message with the RSA *private* key (PKCS#1 v1.5 padding + SHA-256).
* **Verify** the signature with the RSA *public* key.
* Show that tampering with the message makes verification FAIL.

Mantra: **sign = private, verify = public.** RS256 wraps exactly this in the
JOSE format.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/05_digital_signatures.py
"""

import jwt
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def main() -> None:
    print("=" * 70)
    print("STEP 1 — Generate an RSA key pair")
    print("=" * 70)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    print(f"private key: RSA-{private_key.key_size}  (kept secret by the signer)")
    print(f"public key : RSA-{public_key.key_size}  (shareable with verifiers)\n")

    message = b"Transfer $50 from Alice to Bob"

    print("=" * 70)
    print("STEP 2 — SIGN with the PRIVATE key (PKCS#1 v1.5 + SHA-256)")
    print("=" * 70)
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),  # the padding RS256 uses (PS256 uses PSS instead)
        hashes.SHA256(),  # the '256' in RS256
    )
    print(f"message   : {message!r}")
    print(f"signature : {len(signature)} bytes (matches RSA key size: 2048/8 = 256)")
    print(f"hex(first 32 bytes): {signature[:32].hex()}...\n")

    print("=" * 70)
    print("STEP 3 — VERIFY with the PUBLIC key (genuine message)")
    print("=" * 70)
    try:
        public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
        print("verify(signature, original message) -> VALID ✔")
    except InvalidSignature:
        print("UNEXPECTED: genuine signature failed to verify")
    print()

    print("=" * 70)
    print("STEP 4 — Tamper with the message, verification must FAIL")
    print("=" * 70)
    tampered = b"Transfer $5000 from Alice to Bob"
    print(f"tampered message: {tampered!r}")
    try:
        public_key.verify(signature, tampered, padding.PKCS1v15(), hashes.SHA256())
        print("UNEXPECTED: tampered message verified?!")
    except InvalidSignature:
        print("verify(signature, tampered message) -> INVALID ✔ (forgery caught)\n")

    print("=" * 70)
    print("STEP 5 — Same primitive, now as a JWT RS256 token")
    print("=" * 70)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    token = jwt.encode({"amount": 50, "to": "bob"}, private_pem, algorithm="RS256")
    decoded = jwt.decode(token, public_pem, algorithms=["RS256"])
    print(f"RS256 token : {token[:55]}...")
    print(f"RS256 decode: {decoded}")
    print("\nRS256 is just 'RSA-sign the SHA-256 of header.payload'. Same engine.")


if __name__ == "__main__":
    main()
