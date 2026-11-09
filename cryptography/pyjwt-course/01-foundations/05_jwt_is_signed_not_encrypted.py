"""
05 · A JWT is SIGNED, not ENCRYPTED
===================================

The single most common JWT misconception: "the token is encrypted, so I can
put secrets in it." FALSE.

A standard signed JWT (JWS) is:
  * INTEGRITY-protected — the signature proves it wasn't altered.
  * NOT confidential    — the payload is just base64url-encoded JSON that
                          ANYONE can read without any key.

This script proves it: we read the payload of a token using nothing but
base64 decoding — no secret, no library verification.

LESSON: Never put passwords, API keys, credit-card numbers, or any secret in a
JWT payload. Assume the whole world can read it.
"""

import base64
import json

import jwt

SECRET = "only-the-server-knows-this-32-byte-key!!"
# Imagine a careless developer stuffing a secret into the payload:
token = jwt.encode(
    {"user": "alice", "password": "hunter2", "ssn": "123-45-6789"},
    SECRET,
    algorithm="HS256",
)

print("=" * 60)
print("THE TOKEN (looks scrambled / 'encrypted', right?)")
print("=" * 60)
print(token)
print()

print("=" * 60)
print("READING THE PAYLOAD WITH NO SECRET AT ALL")
print("=" * 60)
payload_segment = token.split(".")[1]
payload_bytes = base64.urlsafe_b64decode(
    payload_segment + "=" * ((-len(payload_segment)) % 4)
)
payload = json.loads(payload_bytes)
print(f"Decoded payload: {payload}")
print()
print(f"  -> password leaked: {payload['password']!r}")
print(f"  -> ssn leaked     : {payload['ssn']!r}")
print()

print("=" * 60)
print("TAKEAWAY")
print("=" * 60)
print("Signed != encrypted. The signature stops TAMPERING, it does NOT hide")
print("anything. The payload is world-readable.")
print("RULE: never put secrets in a JWT. (If you truly need confidentiality,")
print("that is a different spec: JWE — JSON Web Encryption.)")
