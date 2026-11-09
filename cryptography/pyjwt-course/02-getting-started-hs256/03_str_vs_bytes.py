"""
03 · str vs bytes
=================

Two small-but-important PyJWT 2.x facts:

  1. encode() returns a `str` (in PyJWT 1.x it returned `bytes` — a common
     source of confusion when reading old tutorials).
  2. The SECRET KEY may be passed as either a `str` or `bytes`. PyJWT encodes a
     str key to UTF-8 bytes internally, so both forms produce/verify the same
     signature — as long as you're consistent.

This script demonstrates all of that.
"""

import jwt

print("=" * 60)
print("FACT 1 — encode() returns str")
print("=" * 60)
token = jwt.encode({"user": "alice"}, "a-demo-secret-at-least-32-bytes-long!!!!", algorithm="HS256")
print(f"type(token) = {type(token).__name__}")
assert isinstance(token, str), "In PyJWT 2.x, encode() must return str"
print("Confirmed: it's a str. (PyJWT 1.x returned bytes — old guides may differ.)")
print()

print("=" * 60)
print("FACT 2 — secret key can be str OR bytes")
print("=" * 60)
str_secret = "my-shared-secret-at-least-32-bytes-long!"
bytes_secret = b"my-shared-secret-at-least-32-bytes-long!"  # same bytes, just a bytes literal

token_from_str = jwt.encode({"user": "alice"}, str_secret, algorithm="HS256")
token_from_bytes = jwt.encode({"user": "alice"}, bytes_secret, algorithm="HS256")
print(f"token signed with str secret  : {token_from_str}")
print(f"token signed with bytes secret: {token_from_bytes}")
print(f"identical tokens? {token_from_str == token_from_bytes}")
print()

print("Cross-verify: decode the str-signed token using the BYTES secret...")
claims = jwt.decode(token_from_str, bytes_secret, algorithms=["HS256"])
print(f"  decoded fine: {claims}")
print("...and decode the bytes-signed token using the STR secret...")
claims = jwt.decode(token_from_bytes, str_secret, algorithms=["HS256"])
print(f"  decoded fine: {claims}")
print()

print("=" * 60)
print("WHY THIS MATTERS")
print("=" * 60)
print("A 'str' secret is encoded to UTF-8 bytes under the hood, so 'abc' and")
print("b'abc' are equivalent keys. Pick one convention and stay consistent.")
print("Heads up: code copied from PyJWT 1.x may do token.decode('utf-8') on the")
print("result of encode() — that breaks in 2.x because it's already a str.")
