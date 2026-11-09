"""01_generate_rsa_keypair.py — Create an RSA-2048 keypair and serialize it.

RSA is an *asymmetric* algorithm: you get a PAIR of keys.
  - PRIVATE key: kept secret; used to SIGN tokens.
  - PUBLIC key:  shared freely; used to VERIFY tokens.

To move keys between systems we serialize them to PEM text:
  - Private key -> PKCS#8 PEM  ("-----BEGIN PRIVATE KEY-----")
  - Public key  -> SubjectPublicKeyInfo PEM ("-----BEGIN PUBLIC KEY-----")

This script generates a fresh 2048-bit keypair entirely in memory (no network,
no files) and prints both PEMs so you can see exactly what they look like.
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# --- Generate the keypair ------------------------------------------------
# public_exponent=65537 is the standard, recommended choice.
# key_size=2048 is the modern minimum for RSA.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()  # derived from the private key

# --- Serialize the PRIVATE key to PKCS#8 PEM -----------------------------
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),  # unencrypted for the demo
)

# --- Serialize the PUBLIC key to SubjectPublicKeyInfo PEM ----------------
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

print("=== PRIVATE KEY (PKCS#8 PEM) — keep this SECRET ===")
print(private_pem.decode())
print("=== PUBLIC KEY (SubjectPublicKeyInfo PEM) — safe to share ===")
print(public_pem.decode())

print("Key size (bits):", private_key.key_size)
