"""
02 · Your first decode
======================

Decoding verifies the signature AND returns the claims. You must supply:

  jwt.decode(token, key, algorithms=["HS256"])

  * token      — the compact JWT string.
  * key        — the SAME shared secret used to sign it.
  * algorithms — a list of algorithms you are willing to accept. REQUIRED.

If the signature checks out, you get the original claims dict back. If anything
is wrong (bad secret, tampered token, disallowed algorithm), decode() raises.
"""

import jwt

SECRET = "change-me-to-a-real-secret-min-32-bytes!"

# First, issue a token (same as script 01).
token = jwt.encode({"user": "alice"}, SECRET, algorithm="HS256")
print(f"Token to decode:\n{token}\n")

print("=" * 60)
print("DECODING + VERIFYING")
print("=" * 60)
# algorithms=["HS256"] tells PyJWT exactly which algorithm is allowed.
claims = jwt.decode(token, SECRET, algorithms=["HS256"])
print(f"Verified claims: {claims}")
print(f"claims type    : {type(claims).__name__}")
print()

print("Because the secret matched and the signature was valid, PyJWT returned")
print("the original payload. Decoding both VERIFIES and DESERIALIZES in one call.")
