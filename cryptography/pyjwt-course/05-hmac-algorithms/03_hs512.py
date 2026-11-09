"""03_hs512.py — Signing and verifying a JWT with HS512.

HS512 = "HMAC using SHA-512". The strongest member of the HMAC/SHA-2 family
supported by JWT. Same code, bigger hash, bigger signature.

When should you reach for HS512 over HS256? Honestly, HS256 is already
plenty for most apps. HS512 buys you a larger security margin and is handy
when policy/compliance asks for SHA-512, at the cost of a slightly longer
token.
"""

import jwt

# 64+ bytes: satisfies HS512's recommended 64-byte key length.
SECRET = "super-secret-shared-key-keep-me-safe-please-and-make-it-nice-and-long"
payload = {"user": "ada", "role": "admin"}

# --- Encode with HS512 ---------------------------------------------------
token = jwt.encode(payload, SECRET, algorithm="HS512")
print("Encoded JWT (HS512):")
print(token)
print()

header = jwt.get_unverified_header(token)
print("Algorithm in header (alg):", header["alg"])  # -> "HS512"
print()

# --- Decode with HS512 ---------------------------------------------------
decoded = jwt.decode(token, SECRET, algorithms=["HS512"])
print("Decoded payload:", decoded)
