"""
01 · Anatomy of a JWT
=====================

A JSON Web Token (JWT) is *not* one opaque blob — it is three distinct pieces
of text joined by dots:

        header  .  payload  .  signature

This script takes a real token, splits it on the '.' separators, and labels
each of the three parts so you can see the structure with your own eyes.

Key idea: a JWT is a *string* with a very specific shape. Before any crypto
happens, it is just `xxxxx.yyyyy.zzzzz`.
"""

import jwt

# We build a token so the script is fully self-contained (no network needed).
# Don't worry about encode() yet — module 02 covers it in depth.
SECRET = "super-secret-teaching-key-at-least-32b!"
token = jwt.encode({"user": "alice", "role": "admin"}, SECRET, algorithm="HS256")

print("=" * 60)
print("THE RAW TOKEN")
print("=" * 60)
print(token)
print()

# A JWT in "compact serialization" form is always three base64url segments
# separated by '.' characters. Splitting on '.' gives us those segments.
parts = token.split(".")

print("=" * 60)
print("SPLITTING ON '.'")
print("=" * 60)
print(f"Number of segments: {len(parts)}  (always 3 for a signed JWT)")
print()

# Label each segment. The order is ALWAYS header, payload, signature.
header_segment, payload_segment, signature_segment = parts

print("[1] HEADER segment   (metadata: which algorithm signed this token)")
print(f"    {header_segment}")
print()
print("[2] PAYLOAD segment  (the claims: data about the user/session)")
print(f"    {payload_segment}")
print()
print("[3] SIGNATURE segment (cryptographic proof over header.payload)")
print(f"    {signature_segment}")
print()

print("=" * 60)
print("TAKEAWAY")
print("=" * 60)
print("A JWT is literally: <header>.<payload>.<signature>")
print("The first two parts are encoded JSON; the third is an encoded MAC/")
print("signature. Next script: decode the base64url parts back into JSON.")
