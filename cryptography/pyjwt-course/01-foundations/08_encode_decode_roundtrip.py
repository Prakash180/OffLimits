"""
08 · Full encode -> decode round trip (HS256)
=============================================

Putting it all together: the simplest complete life cycle of a JWT.

  ENCODE:  dict of claims  + secret + algorithm  ->  compact token string
  DECODE:  token string    + secret + algorithms ->  dict of claims back

This script prints each stage so you can watch the data transform and return
unchanged, proving the round trip is lossless when the secret matches.
"""

import jwt

SECRET = "round-trip-secret-at-least-32-bytes-long"

# --- Stage 1: the claims we want to put in the token -------------------------
original_claims = {"user": "alice", "role": "admin", "count": 3}
print("=" * 60)
print("STAGE 1 — original claims (a plain Python dict)")
print("=" * 60)
print(original_claims)
print()

# --- Stage 2: encode -> a compact token string -------------------------------
# In PyJWT 2.x, encode() returns a `str` (not bytes). algorithm= is singular.
token = jwt.encode(original_claims, SECRET, algorithm="HS256")
print("=" * 60)
print("STAGE 2 — encoded token (str)")
print("=" * 60)
print(f"type  : {type(token).__name__}")
print(f"value : {token}")
print()

# --- Stage 3: decode -> claims dict back -------------------------------------
# On decode, algorithms= is a REQUIRED list naming the algorithm(s) you accept.
decoded_claims = jwt.decode(token, SECRET, algorithms=["HS256"])
print("=" * 60)
print("STAGE 3 — decoded claims (back to a dict)")
print("=" * 60)
print(f"type  : {type(decoded_claims).__name__}")
print(f"value : {decoded_claims}")
print()

# --- Stage 4: confirm the round trip is lossless -----------------------------
print("=" * 60)
print("STAGE 4 — round-trip check")
print("=" * 60)
print(f"original == decoded ? {original_claims == decoded_claims}")
print()
print("That's the core loop you'll use everywhere: encode to hand a token out,")
print("decode (with the same secret + pinned algorithm) to read it back safely.")
