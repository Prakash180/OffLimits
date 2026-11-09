"""
04 · The wrong secret fails
===========================

HS256 is symmetric: the SAME secret both signs and verifies. If you try to
verify a token with the wrong secret, the recomputed HMAC won't match the
signature in the token, and PyJWT raises `InvalidSignatureError`.

This is the property that makes JWTs trustworthy: only a holder of the secret
can produce a token that verifies.
"""

import jwt
from jwt.exceptions import InvalidSignatureError

RIGHT_SECRET = "the-correct-secret-at-least-32-bytes!!!!"
WRONG_SECRET = "an-attackers-guess-at-least-32-bytes!!!!"

token = jwt.encode({"user": "alice"}, RIGHT_SECRET, algorithm="HS256")
print(f"Token (signed with the RIGHT secret):\n{token}\n")

print("=" * 60)
print("DECODING WITH THE CORRECT SECRET")
print("=" * 60)
claims = jwt.decode(token, RIGHT_SECRET, algorithms=["HS256"])
print(f"Success: {claims}")
print()

print("=" * 60)
print("DECODING WITH THE WRONG SECRET")
print("=" * 60)
try:
    jwt.decode(token, WRONG_SECRET, algorithms=["HS256"])
    print("BUG: wrong secret accepted (should never happen)!")
except InvalidSignatureError as exc:
    print(f"InvalidSignatureError raised: {exc}")
    print()
    print("The verifier recomputes HMAC-SHA256(header.payload, WRONG_SECRET),")
    print("gets a different value than the token's signature, and rejects it.")
    print("Only someone who knows the real secret can forge a valid token.")
