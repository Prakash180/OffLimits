"""02_rs256_sign_verify.py — Sign with the private key, verify with the public.

RS256 = "RSASSA-PKCS1-v1_5 using SHA-256".

The whole point of RSA for JWTs:
  - The Issuer SIGNS with its PRIVATE key (which it never shares).
  - Anyone holding the PUBLIC key can VERIFY, but cannot forge new tokens.

PyJWT accepts either PEM bytes/strings OR cryptography key objects. Here we
pass the cryptography key objects directly for simplicity.
"""

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

# --- One keypair -------------------------------------------------------
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

payload = {"user": "ada", "role": "admin"}

# --- Sign with the PRIVATE key ------------------------------------------
token = jwt.encode(payload, private_key, algorithm="RS256")
print("Encoded JWT (RS256):")
print(token)
print()

header = jwt.get_unverified_header(token)
print("Algorithm in header (alg):", header["alg"])  # -> "RS256"
print()

# --- Verify with the PUBLIC key -----------------------------------------
decoded = jwt.decode(token, public_key, algorithms=["RS256"])
print("Decoded payload:", decoded)
