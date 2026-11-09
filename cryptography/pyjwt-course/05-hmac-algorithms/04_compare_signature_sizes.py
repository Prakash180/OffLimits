"""04_compare_signature_sizes.py — How big is each HMAC signature?

A JWT has three dot-separated parts:  header.payload.signature
Each part is base64url-encoded. The signature is the raw output of the HMAC
function, which is exactly as long as the underlying hash digest:

    HS256 -> SHA-256 -> 256 bits -> 32 bytes
    HS384 -> SHA-384 -> 384 bits -> 48 bytes
    HS512 -> SHA-512 -> 512 bits -> 64 bytes

This script signs the SAME payload with all three algorithms and measures the
raw signature length to prove the relationship above.
"""

import base64

import jwt

# 64+ bytes so HS256/384/512 are all happy with the key length.
SECRET = "super-secret-shared-key-keep-me-safe-please-and-make-it-nice-and-long"
payload = {"user": "ada", "role": "admin"}


def b64url_decode(segment: str) -> bytes:
    """Decode a base64url string, restoring any stripped '=' padding."""
    # JWT strips base64url padding; we add it back before decoding.
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


print("Raw HMAC signature size = the hash digest size:\n")
for alg, expected_bytes in [("HS256", 32), ("HS384", 48), ("HS512", 64)]:
    token = jwt.encode(payload, SECRET, algorithm=alg)

    # The signature is the 3rd part of the compact token.
    signature_segment = token.split(".")[2]
    raw_signature = b64url_decode(signature_segment)

    print(
        f"  {alg}: {len(raw_signature):>2} bytes "
        f"({len(raw_signature) * 8} bits)  "
        f"-> matches SHA-{alg[2:]} digest: {len(raw_signature) == expected_bytes}"
    )

print()
print("Takeaway: a stronger hash => longer signature => slightly longer token.")
print("All three are secure; HS256 is the common default.")
