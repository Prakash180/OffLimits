"""04_private_signs_public_verifies.py — Only the public key is needed to verify.

This is the defining superpower of asymmetric signing:

  * You SIGN with the PRIVATE key.
  * You VERIFY with the PUBLIC key.
  * The public key CANNOT be used to sign.

So you can hand your public key to the whole world, and they can confirm your
tokens are genuine — yet none of them can mint a token that appears to come
from you. That is impossible with HMAC, where verify == sign.

We prove both halves below.
"""

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

payload = {"iss": "auth.example.com", "sub": "user-123"}

# --- 1) Private key signs; public key verifies (the normal flow) ---------
token = jwt.encode(payload, private_key, algorithm="RS256")
decoded = jwt.decode(token, public_key, algorithms=["RS256"])
print("Verified with PUBLIC key only:", decoded)
print("(The verifier never needs — and never sees — the private key.)\n")

# --- 2) You CANNOT sign with just the public key -------------------------
# Signing requires the private key. Handing jwt.encode a public key fails.
try:
    jwt.encode(payload, public_key, algorithm="RS256")
    print("Unexpected: signing with the public key succeeded?!")
except Exception as exc:  # cryptography/PyJWT raises when no private material
    print("Attempt to SIGN with the public key failed, as expected:")
    print(f"  {type(exc).__name__}: {exc}")

print()
print("Conclusion: distributing the public key is safe; it only enables")
print("verification, never forgery.")
