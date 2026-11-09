"""01_hs256.py — Signing and verifying a JWT with HS256.

HS256 = "HMAC using SHA-256". It is a *symmetric* (shared-secret) algorithm:
the SAME secret string is used to both create (sign) and verify the token.

Mental model:
    signature = HMAC_SHA256(secret, base64url(header) + "." + base64url(payload))

This is the most common "getting started" JWT algorithm because it needs
nothing more than a single secret string — no key pairs, no PEM files.
"""

import jwt

# A secret only the signer (and trusted verifiers) should know.
# In production this MUST be long, random, and stored securely. We use a
# 64+ byte secret so it satisfies even HS512's recommended key length.
SECRET = "super-secret-shared-key-keep-me-safe-please-and-make-it-nice-and-long"

payload = {"user": "ada", "role": "admin"}

# --- Encode (sign) -------------------------------------------------------
# jwt.encode(payload, key, algorithm) returns a compact JWT string.
token = jwt.encode(payload, SECRET, algorithm="HS256")
print("Encoded JWT (HS256):")
print(token)
print()

# --- Inspect the header WITHOUT verifying -------------------------------
# The header is just base64url-encoded JSON; anyone can read it.
header = jwt.get_unverified_header(token)
print("JOSE header:", header)
print("Algorithm in header (alg):", header["alg"])  # -> "HS256"
print()

# --- Decode (verify) -----------------------------------------------------
# We must pass the SAME secret and list the algorithm(s) we accept.
decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
print("Decoded payload:", decoded)
