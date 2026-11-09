"""
02 · base64url decoding by hand
===============================

The header and payload of a JWT are JSON objects that have been encoded with
**base64url** (RFC 4648 §5), NOT standard base64. This script decodes them
manually — no PyJWT helpers — so you understand exactly what is happening.

Why base64url instead of standard base64?
  * Standard base64 uses '+' and '/' and '=' padding.
  * Those characters are unsafe/awkward inside URLs, HTTP headers, and cookies
    ('+' becomes a space, '/' is a path separator, '=' needs escaping).
  * base64url swaps '+' -> '-' and '/' -> '_' and DROPS the '=' padding,
    making the token safe to drop straight into a URL or header.

Because the '=' padding is removed, we must add it back before decoding.
"""

import base64
import json

import jwt

# Build a token to dissect (self-contained; see module 02 for encode details).
SECRET = "a-32-byte-or-longer-demo-signing-secret!"
token = jwt.encode({"user": "alice", "scope": ["read", "write"]}, SECRET, algorithm="HS256")
header_segment, payload_segment, signature_segment = token.split(".")


def b64url_decode(segment: str) -> bytes:
    """Decode a base64url string, restoring the stripped '=' padding.

    base64 requires the input length to be a multiple of 4. JWT segments have
    their padding removed, so we re-add the right number of '=' characters.
    """
    # How many padding chars are missing? base64 works in blocks of 4.
    padding_needed = (-len(segment)) % 4
    segment_padded = segment + ("=" * padding_needed)
    # urlsafe_b64decode understands the '-' and '_' alphabet of base64url.
    return base64.urlsafe_b64decode(segment_padded)


print("=" * 60)
print("HEADER segment -> JSON")
print("=" * 60)
print(f"encoded : {header_segment}")
header_bytes = b64url_decode(header_segment)
print(f"raw json: {header_bytes.decode('utf-8')}")
print(f"as dict : {json.loads(header_bytes)}")
print()

print("=" * 60)
print("PAYLOAD segment -> JSON")
print("=" * 60)
print(f"encoded : {payload_segment}")
payload_bytes = b64url_decode(payload_segment)
print(f"raw json: {payload_bytes.decode('utf-8')}")
print(f"as dict : {json.loads(payload_bytes)}")
print()

print("=" * 60)
print("WHY base64url (and not base64)?")
print("=" * 60)
print("base64url replaces '+' -> '-', '/' -> '_', and removes '=' padding,")
print("so the token is safe inside URLs, HTTP headers, and cookies.")
print("We re-added the missing '=' padding before decoding above.")
