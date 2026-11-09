"""
07 · Secret strength for HMAC
=============================

HS256 security rests ENTIRELY on the secret being unguessable. A weak secret
(like "password" or "secret") can be brute-forced or dictionary-attacked
offline, letting anyone forge valid tokens.

Guidelines:
  * Use a HIGH-ENTROPY random secret, not a memorable word.
  * For HS256 (HMAC-SHA256) aim for at least 256 bits (32 bytes) of entropy —
    matching the hash output size.
  * Generate it with a CRYPTOGRAPHICALLY SECURE source:
        - secrets.token_urlsafe(n)  -> URL-safe text, ~1.3*n chars for n bytes
        - secrets.token_hex(n)      -> hex text, 2*n chars for n bytes
        - os.urandom(n)             -> raw random bytes
  * NEVER use random.random()/random.choice() — those are NOT secure.

This script generates strong secrets and uses one to sign a token.
"""

import os
import secrets

import jwt

print("=" * 60)
print("GENERATING STRONG SECRETS (cryptographically secure)")
print("=" * 60)
# 32 bytes = 256 bits of entropy, a good match for SHA-256.
urlsafe_secret = secrets.token_urlsafe(32)
hex_secret = secrets.token_hex(32)
raw_secret = os.urandom(32)  # bytes, also usable directly as a key

print(f"secrets.token_urlsafe(32): {urlsafe_secret}")
print(f"  length: {len(urlsafe_secret)} chars")
print(f"secrets.token_hex(32)    : {hex_secret}")
print(f"  length: {len(hex_secret)} chars")
print(f"os.urandom(32)           : {raw_secret!r}")
print(f"  length: {len(raw_secret)} bytes")
print()

print("=" * 60)
print("USING A STRONG SECRET TO SIGN")
print("=" * 60)
token = jwt.encode({"user": "alice"}, urlsafe_secret, algorithm="HS256")
print(f"token: {token}")
claims = jwt.decode(token, urlsafe_secret, algorithms=["HS256"])
print(f"verified: {claims}")
print()

print("=" * 60)
print("ENTROPY MATTERS — DON'T DO THIS")
print("=" * 60)
weak = "secret"
print(f"A weak secret like {weak!r} is in every wordlist; tokens signed with it")
print("can be forged via offline brute force. The math of HMAC is strong, but")
print("it can't protect a guessable key.")
print("Rule: >= 32 random bytes, from `secrets`/`os.urandom`, stored outside code.")
