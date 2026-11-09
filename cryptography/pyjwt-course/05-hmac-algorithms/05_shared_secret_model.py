"""05_shared_secret_model.py — The shared-secret (symmetric) trust model.

HMAC is *symmetric*: there is exactly ONE secret, and that single secret is
used for BOTH signing and verifying. Anyone who can verify a token can also
forge one, because verifying and signing require the same key.

That makes HMAC perfect when the SAME party (or a small set of mutually
trusting services) both issues and checks the tokens. It is a poor fit when
you need to let untrusted third parties verify but not mint tokens — that is
RSA/ECDSA territory (see module 06).

Below we simulate two parties, an Issuer and a Verifier, that share one
secret out-of-band.
"""

import jwt
from jwt.exceptions import InvalidSignatureError

# The single secret both parties agreed on ahead of time (out-of-band).
# Kept comfortably long (>=32 bytes) to satisfy HS256 recommendations.
SHARED_SECRET = "the-one-secret-we-both-hold-and-keep-very-safe-indeed"


def issuer_sign(payload: dict) -> str:
    """The Issuer mints a token using the shared secret."""
    return jwt.encode(payload, SHARED_SECRET, algorithm="HS256")


def verifier_check(token: str, secret: str) -> dict:
    """The Verifier validates a token using the secret it holds."""
    return jwt.decode(token, secret, algorithms=["HS256"])


# --- Happy path: both sides hold the SAME secret -------------------------
token = issuer_sign({"order_id": 42})
print("Issuer produced token:")
print(token, "\n")

result = verifier_check(token, SHARED_SECRET)
print("Verifier (correct secret) accepted payload:", result, "\n")

# --- Failure path: a verifier with the WRONG secret ----------------------
# This proves verification truly depends on possessing the shared secret.
try:
    verifier_check(token, "an-attacker-guess-that-is-also-comfortably-long-but-wrong")
except InvalidSignatureError:
    print("Verifier (wrong secret) -> InvalidSignatureError, as expected.")

print()
print("Lesson: with HMAC, 'can verify' == 'can sign'. Guard the secret like")
print("a password and only share it with parties you fully trust.")
