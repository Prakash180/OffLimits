"""03_rs384_rs512.py — The other RSA/SHA-2 variants: RS384 and RS512.

Just like the HMAC family had HS256/384/512, the RSA family has:
  RS256 -> RSASSA-PKCS1-v1_5 + SHA-256
  RS384 -> RSASSA-PKCS1-v1_5 + SHA-384
  RS512 -> RSASSA-PKCS1-v1_5 + SHA-512

The KEY stays the same; only the hash used inside the signature changes.
Note that, unlike HMAC, the RSA signature length is governed by the KEY SIZE
(2048-bit key -> 256-byte signature), not by the hash — so all three produce
the same signature size for a given key.
"""

import base64

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

payload = {"user": "ada", "role": "admin"}


def raw_signature_len(token: str) -> int:
    segment = token.split(".")[2]
    padding = "=" * (-len(segment) % 4)
    return len(base64.urlsafe_b64decode(segment + padding))


for alg in ["RS384", "RS512"]:
    token = jwt.encode(payload, private_key, algorithm=alg)
    header = jwt.get_unverified_header(token)
    decoded = jwt.decode(token, public_key, algorithms=[alg])

    print(f"--- {alg} ---")
    print("  header alg:", header["alg"])
    print("  signature size (bytes):", raw_signature_len(token), "(= key size / 8)")
    print("  decoded payload:", decoded)
    print()

print("With RSA the signature size tracks the KEY size (2048 bits -> 256 bytes),")
print("not the hash size — that is the big difference from the HMAC family.")
