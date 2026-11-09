"""02_hs384.py — Signing and verifying a JWT with HS384.

HS384 = "HMAC using SHA-384". Identical workflow to HS256, but the underlying
hash function is SHA-384 instead of SHA-256. The only thing that changes in
your code is the `algorithm=` / `algorithms=` value.

A larger hash produces a larger signature (see 04_compare_signature_sizes.py),
which gives a wider security margin at a small size cost.
"""

import jwt

# 64+ bytes: long enough for HS384's recommended 48-byte key length.
SECRET = "super-secret-shared-key-keep-me-safe-please-and-make-it-nice-and-long"
payload = {"user": "ada", "role": "admin"}

# --- Encode with HS384 ---------------------------------------------------
token = jwt.encode(payload, SECRET, algorithm="HS384")
print("Encoded JWT (HS384):")
print(token)
print()

# The header now records HS384 as the algorithm.
header = jwt.get_unverified_header(token)
print("Algorithm in header (alg):", header["alg"])  # -> "HS384"
print()

# --- Decode with HS384 ---------------------------------------------------
# Note: you MUST list "HS384" in algorithms=, not "HS256".
decoded = jwt.decode(token, SECRET, algorithms=["HS384"])
print("Decoded payload:", decoded)
