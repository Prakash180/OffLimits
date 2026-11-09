"""
04 · Decoding WITHOUT verifying the signature
=============================================

PyJWT can decode the claims of a token *without checking the signature* and
*without a key* if you pass options={"verify_signature": False}.

This is genuinely useful in a few narrow cases (e.g. reading the `kid` or
`iss` to decide WHICH key to fetch before doing a real verification).

But it is also DANGEROUS if misused: the claims are completely untrusted.
Anyone could have forged or altered them. Never make a security decision based
on an unverified token.
"""

import jwt

SECRET = "the-real-secret-at-least-32-bytes-long!!"
token = jwt.encode({"user": "alice", "role": "admin"}, SECRET, algorithm="HS256")

print("=" * 60)
print("DECODE WITHOUT VERIFICATION (no key supplied)")
print("=" * 60)
# Note: no secret/key argument is needed at all here.
unverified_claims = jwt.decode(token, options={"verify_signature": False})
print(f"Claims read without any key: {unverified_claims}")
print()

print("=" * 60)
print("WHY THIS IS DANGEROUS")
print("=" * 60)
print("These claims are UNTRUSTED. We never checked the signature, so we have")
print("no proof they weren't forged or modified. An attacker could claim")
print("role='admin' for any user and this call would happily return it.")
print()

print("=" * 60)
print("LEGITIMATE USES (read-then-verify)")
print("=" * 60)
print("Reading metadata to choose a verification key BEFORE verifying, e.g.:")
print("  * read 'iss' to pick the right issuer config")
print("  * read 'kid' (in the header) to fetch the matching public key")
print("...then ALWAYS call jwt.decode(...) again WITH the key to verify.")
print()
print("Rule of thumb: unverified decode = read-only hint, never authorization.")
