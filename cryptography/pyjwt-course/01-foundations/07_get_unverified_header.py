"""
07 · Reading the header with get_unverified_header
==================================================

Sometimes you need to look at the JOSE header BEFORE you can verify the token —
most importantly to read:
  * 'alg' — which algorithm was used (so you know how to verify), and
  * 'kid' — the Key ID, telling you WHICH public key to fetch from a JWKS.

PyJWT exposes `jwt.get_unverified_header(token)` for exactly this. It only
parses the header segment; it does NOT verify the signature.

As always: anything "unverified" is a HINT used to set up verification, never a
trust decision by itself.
"""

import jwt

SECRET = "teaching-secret-at-least-32-bytes-long!!"

# We can attach custom header fields via the `headers=` argument to encode().
token = jwt.encode(
    {"user": "alice"},
    SECRET,
    algorithm="HS256",
    headers={"kid": "key-2024-09"},  # pretend this names a signing key
)

print("=" * 60)
print("THE TOKEN")
print("=" * 60)
print(token)
print()

print("=" * 60)
print("get_unverified_header(token)")
print("=" * 60)
header = jwt.get_unverified_header(token)
print(f"Full header dict: {header}")
print(f"  alg -> {header['alg']}   (algorithm used to sign)")
print(f"  typ -> {header['typ']}   (media type, usually 'JWT')")
print(f"  kid -> {header['kid']}   (which key signed it; used to look up a key)")
print()

print("=" * 60)
print("TYPICAL FLOW IN REAL SYSTEMS")
print("=" * 60)
print("1. get_unverified_header(token) -> read 'kid' and 'alg'.")
print("2. Use 'kid' to fetch the matching public key from a JWKS endpoint.")
print("3. jwt.decode(token, that_key, algorithms=[expected_alg]) -> VERIFY.")
print()
print("The header read is unverified, but step 3 (with the real key) is where")
print("trust is actually established.")
