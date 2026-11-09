"""07_key_sizes.py — RSA key size: 2048 vs 3072 bits.

The RSA key size is the length of the modulus. Bigger keys are harder to
break but cost more CPU to generate, sign, and verify, and produce larger
signatures (signature size = key_size / 8 bytes).

Rough guidance:
  - 2048-bit: the modern minimum; fine for most systems today.
  - 3072-bit: higher security margin (~128-bit security level); slower.
  - <2048-bit: considered weak — avoid.

This script builds a token with each size, confirms it still verifies, and
prints the signature size so you can see the cost.
"""

import base64
import time

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

payload = {"user": "ada"}


def raw_signature_len(token: str) -> int:
    segment = token.split(".")[2]
    padding = "=" * (-len(segment) % 4)
    return len(base64.urlsafe_b64decode(segment + padding))


for key_size in (2048, 3072):
    # Time the keygen to illustrate the perf tradeoff.
    start = time.perf_counter()
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    gen_ms = (time.perf_counter() - start) * 1000
    public_key = private_key.public_key()

    token = jwt.encode(payload, private_key, algorithm="RS256")
    decoded = jwt.decode(token, public_key, algorithms=["RS256"])

    print(f"--- RSA-{key_size} ---")
    print(f"  keygen time:      {gen_ms:7.1f} ms")
    print(f"  signature size:   {raw_signature_len(token)} bytes (= {key_size}/8)")
    print(f"  verifies OK:      {decoded == payload}")
    print()

print("Tradeoff: larger keys = stronger but slower and bigger tokens.")
print("2048-bit is a sound default; step up to 3072-bit for long-lived,")
print("high-value keys where the extra margin is worth the cost.")
