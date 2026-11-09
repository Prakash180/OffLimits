"""
06 · Tampering breaks the signature
===================================

The whole point of the signature is INTEGRITY: if even a single byte of the
header or payload changes, verification must fail.

This script demonstrates an attack and its defeat:
  1. Issue a legit token for a normal user (role='user').
  2. Decode the payload, change role -> 'admin' (privilege escalation attempt).
  3. Re-encode the modified payload and reassemble a forged token, reusing the
     ORIGINAL signature (the attacker doesn't know the secret, so they can't
     compute a new valid signature).
  4. Verify the forged token with the real secret -> InvalidSignatureError.
"""

import base64
import json

import jwt
from jwt.exceptions import InvalidSignatureError

SECRET = "server-side-secret-attacker-does-not-know"

# --- Step 1: a legitimate, low-privilege token -------------------------------
token = jwt.encode({"user": "mallory", "role": "user"}, SECRET, algorithm="HS256")
header_seg, payload_seg, signature_seg = token.split(".")
print("Original token (role=user):")
print(token)
print()


def b64url_decode(segment: str) -> bytes:
    return base64.urlsafe_b64decode(segment + "=" * ((-len(segment)) % 4))


def b64url_encode(raw: bytes) -> str:
    # base64url with the '=' padding stripped, exactly like JWT segments.
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


# --- Step 2: attacker edits the payload --------------------------------------
payload = json.loads(b64url_decode(payload_seg))
print(f"Decoded payload: {payload}")
payload["role"] = "admin"  # privilege escalation attempt!
print(f"Tampered payload: {payload}")
print()

# --- Step 3: reassemble a forged token (old signature reused) ----------------
# json.dumps with compact separators to mimic the original encoding style.
forged_payload_seg = b64url_encode(
    json.dumps(payload, separators=(",", ":")).encode("utf-8")
)
forged_token = f"{header_seg}.{forged_payload_seg}.{signature_seg}"
print("Forged token (role=admin, but signature is now stale):")
print(forged_token)
print()

# --- Step 4: verification fails ----------------------------------------------
print("=" * 60)
print("VERIFYING THE FORGED TOKEN WITH THE REAL SECRET")
print("=" * 60)
try:
    jwt.decode(forged_token, SECRET, algorithms=["HS256"])
    print("BUG: forged token was accepted (should never happen)!")
except InvalidSignatureError:
    print("InvalidSignatureError raised — tampering DETECTED and rejected. ✅")
    print()
    print("The signature was computed over the ORIGINAL header.payload. Because")
    print("the payload changed and the attacker can't recompute a valid MAC")
    print("without the secret, verification fails. Integrity wins.")
