"""
05 · You MUST specify algorithms= on decode
===========================================

When verifying, PyJWT requires you to pass `algorithms=[...]` — the explicit
allow-list of algorithms you accept. This is a SECURITY feature, not a nuisance.

Why pin algorithms?
  * The 'alg' value lives in the token HEADER, which is attacker-controlled.
  * If a verifier blindly trusted the header's 'alg', an attacker could switch
    it (e.g. to 'none', or perform an RSA->HMAC "algorithm confusion" attack).
  * By passing your OWN allow-list, you decide what's acceptable — the token
    can't talk you into using a weaker/none algorithm.

This script shows that omitting algorithms= raises, and that an algorithm NOT
in your allow-list is rejected.
"""

import jwt

SECRET = "teaching-secret-at-least-32-bytes-long!!"
token = jwt.encode({"user": "alice"}, SECRET, algorithm="HS256")

print("=" * 60)
print("CASE 1 — omitting algorithms= entirely")
print("=" * 60)
try:
    # Intentionally wrong: no algorithms list supplied.
    jwt.decode(token, SECRET)  # type: ignore[call-arg]
    print("Unexpectedly succeeded without algorithms=!")
except Exception as exc:  # PyJWT raises DecodeError here
    print(f"Rejected as expected: {type(exc).__name__}: {exc}")
print()

print("=" * 60)
print("CASE 2 — token's algorithm not in the allow-list")
print("=" * 60)
try:
    # We accept only RS256, but the token is HS256 -> not allowed.
    jwt.decode(token, SECRET, algorithms=["RS256"])
    print("Unexpectedly accepted a disallowed algorithm!")
except Exception as exc:
    print(f"Rejected as expected: {type(exc).__name__}: {exc}")
print()

print("=" * 60)
print("CASE 3 — correct, explicit allow-list")
print("=" * 60)
claims = jwt.decode(token, SECRET, algorithms=["HS256"])
print(f"Accepted: {claims}")
print()

print("=" * 60)
print("TAKEAWAY")
print("=" * 60)
print("ALWAYS pass algorithms=[...] with the EXACT set you expect. Never derive")
print("it from the token's own header. This single habit defends against")
print("'alg=none' and algorithm-confusion attacks.")
