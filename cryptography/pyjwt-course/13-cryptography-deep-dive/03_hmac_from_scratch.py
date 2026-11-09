"""
03 · HMAC from scratch — demystifying the HS256 signature
==========================================================

The big reveal: an HS256 JWT signature is *just* an HMAC-SHA256, base64url-
encoded. Nothing magic. In this script we:

1. Build an HS256 JWT with PyJWT.
2. Split it into its three dot-separated segments: header.payload.signature.
3. Independently compute HMAC-SHA256 over the ASCII bytes of
   ``f"{header}.{payload}"`` using Python's ``hmac`` module + our secret.
4. base64url-encode (no padding) our raw HMAC and show it is byte-for-byte
   identical to the token's third segment.

That equality is the whole trick behind HS256. The verifier recomputes the same
HMAC and compares — an attacker without the secret cannot.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/03_hmac_from_scratch.py
"""

import base64
import hashlib
import hmac

import jwt


def b64url_nopad(raw: bytes) -> str:
    """base64url-encode WITHOUT the trailing '=' padding (the JOSE convention)."""
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def main() -> None:
    # 32+ bytes: RFC 7518 recommends an HMAC key at least as long as the digest.
    secret = "super-secret-shared-key-keep-this-private-please"
    payload = {"sub": "1234567890", "name": "Ada Lovelace", "admin": True}

    print("=" * 70)
    print("STEP 1 — Let PyJWT mint an HS256 token")
    print("=" * 70)
    token = jwt.encode(payload, secret, algorithm="HS256")
    print(f"token: {token}\n")

    header_seg, payload_seg, signature_seg = token.split(".")
    print(f"header    segment: {header_seg}")
    print(f"payload   segment: {payload_seg}")
    print(f"signature segment: {signature_seg}\n")

    print("=" * 70)
    print("STEP 2 — Compute HMAC-SHA256 ourselves over 'header.payload'")
    print("=" * 70)
    signing_input = f"{header_seg}.{payload_seg}".encode("ascii")
    print(f"signing input (bytes): {signing_input}")

    # This is EXACTLY what PyJWT's HS256 signer does internally.
    raw_hmac = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    print(f"raw HMAC-SHA256 (hex): {raw_hmac.hex()}")

    our_signature = b64url_nopad(raw_hmac)
    print(f"our base64url signature: {our_signature}\n")

    print("=" * 70)
    print("STEP 3 — Compare against the token's signature segment")
    print("=" * 70)
    print(f"PyJWT signature : {signature_seg}")
    print(f"our  signature  : {our_signature}")
    match = hmac.compare_digest(our_signature, signature_seg)
    print(f"\nIDENTICAL? {match}  <-- the 'aha': HS256 signature == base64url(HMAC)\n")

    print("=" * 70)
    print("STEP 4 — Verification is just recompute + constant-time compare")
    print("=" * 70)
    # A verifier with the secret recomputes the HMAC and compares. Note we use
    # hmac.compare_digest to avoid timing side-channels (never use ==).
    print("verifier recomputes HMAC over header.payload, compares to segment 3.")
    print("Attacker without the secret cannot produce a matching segment 3.")

    # Sanity: PyJWT verifies the same token with the same secret.
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    print(f"\nPyJWT decode with secret -> {decoded}")


if __name__ == "__main__":
    main()
