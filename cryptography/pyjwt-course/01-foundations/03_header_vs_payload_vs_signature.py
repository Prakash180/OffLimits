"""
03 · Header vs Payload vs Signature
===================================

Now that we can decode the segments, let's clearly separate the THREE roles:

  * HEADER    — a small JSON object describing HOW the token is signed
                (e.g. {"alg": "HS256", "typ": "JWT"}).
  * PAYLOAD   — a JSON object of "claims" (the actual data).
  * SIGNATURE — NOT JSON. It is raw cryptographic bytes computed over
                `header.payload`. Trying to read it as JSON is meaningless.

This script pretty-prints the header and payload dicts, and proves the
signature is binary, not text/JSON.
"""

import base64
import json

import jwt

token = jwt.encode(
    {"user": "alice", "role": "admin", "active": True},
    "a-32-byte-or-longer-demo-signing-secret!",
    algorithm="HS256",
)
header_segment, payload_segment, signature_segment = token.split(".")


def b64url_decode(segment: str) -> bytes:
    return base64.urlsafe_b64decode(segment + "=" * ((-len(segment)) % 4))


print("=" * 60)
print("HEADER  (decoded JSON, pretty-printed)")
print("=" * 60)
header = json.loads(b64url_decode(header_segment))
print(json.dumps(header, indent=2))
print("-> 'alg' tells the verifier which algorithm to use.")
print("-> 'typ' is just a media-type hint, almost always 'JWT'.")
print()

print("=" * 60)
print("PAYLOAD  (decoded JSON, pretty-printed)")
print("=" * 60)
payload = json.loads(b64url_decode(payload_segment))
print(json.dumps(payload, indent=2))
print("-> These key/value pairs are called 'claims'.")
print()

print("=" * 60)
print("SIGNATURE  (raw bytes — NOT JSON)")
print("=" * 60)
signature_bytes = b64url_decode(signature_segment)
print(f"length      : {len(signature_bytes)} bytes")
print(f"raw bytes   : {signature_bytes!r}")
print(f"hex view    : {signature_bytes.hex()}")
print()
# Prove it is not JSON by trying to parse it and catching the failure.
try:
    json.loads(signature_bytes)
    print("Unexpectedly parsed as JSON?!")
except (json.JSONDecodeError, UnicodeDecodeError) as exc:
    print(f"Parsing the signature as JSON FAILS, as expected: {type(exc).__name__}")
    print("The signature is a binary MAC, not human-readable data.")
