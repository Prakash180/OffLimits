"""05_wrong_public_key_fails.py — A mismatched public key rejects the token.

A signature only verifies against the public key that PAIRS with the private
key that produced it. If you try to verify a token using an unrelated public
key, PyJWT raises InvalidSignatureError.

This is exactly what protects you from forgeries: an attacker's key pair
produces signatures that your trusted public key will reject.
"""

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.exceptions import InvalidSignatureError

# --- Keypair A: the legitimate signer ------------------------------------
private_a = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_a = private_a.public_key()

# --- Keypair B: an unrelated key pair ------------------------------------
private_b = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_b = private_b.public_key()

# Sign a token with A's private key.
token = jwt.encode({"sub": "alice"}, private_a, algorithm="RS256")

# --- Verify with the CORRECT public key (A) ------------------------------
print("Verifying with the matching public key (A):")
print(" ", jwt.decode(token, public_a, algorithms=["RS256"]), "\n")

# --- Verify with the WRONG public key (B) --------------------------------
print("Verifying with the WRONG public key (B):")
try:
    jwt.decode(token, public_b, algorithms=["RS256"])
except InvalidSignatureError as exc:
    print(f"  Rejected -> {type(exc).__name__}: {exc}")

print()
print("Only the public key paired with the signing private key can verify.")
print("This is what makes signature forgery infeasible.")
