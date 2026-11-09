"""06_secret_rotation_hmac.py — Rotating HMAC secrets without downtime.

Secrets should be rotated periodically. But you cannot flip every issuer and
verifier to a new secret at the same instant — tokens signed with the OLD
secret are still in flight and valid until they expire.

The classic pattern: keep a SHORT LIST of accepted secrets. Sign new tokens
with the newest secret, but when verifying, try each candidate secret in turn
until one validates. Once all old tokens have expired, drop the old secret.

This script demonstrates that fallback loop.
"""

import jwt
from jwt.exceptions import InvalidSignatureError

# Newest secret first; we always SIGN with the first entry.
# Kept >=32 bytes each to satisfy HS256's recommended key length.
OLD_SECRET = "secret-v1-being-retired-but-still-accepted-for-now"
NEW_SECRET = "secret-v2-current-and-freshly-rotated-into-service"

# Ordered list of secrets a verifier will accept during the overlap window.
CANDIDATE_SECRETS = [NEW_SECRET, OLD_SECRET]


def verify_with_rotation(token: str, candidates: list[str]) -> dict:
    """Try each candidate secret until one verifies; else raise."""
    for index, secret in enumerate(candidates):
        try:
            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            print(f"  -> verified with candidate #{index} ({secret!r})")
            return decoded
        except InvalidSignatureError:
            print(f"  -> candidate #{index} ({secret!r}) did not match, trying next")
    raise InvalidSignatureError("Token did not verify against any known secret")


# --- A token still signed with the OLD secret (in flight) ----------------
old_token = jwt.encode({"sub": "legacy-session"}, OLD_SECRET, algorithm="HS256")
print("Verifying a token signed with the OLD secret:")
print(verify_with_rotation(old_token, CANDIDATE_SECRETS), "\n")

# --- A freshly issued token signed with the NEW secret -------------------
new_token = jwt.encode({"sub": "fresh-session"}, NEW_SECRET, algorithm="HS256")
print("Verifying a token signed with the NEW secret:")
print(verify_with_rotation(new_token, CANDIDATE_SECRETS), "\n")

# --- A token signed with a secret we no longer accept --------------------
bogus_token = jwt.encode(
    {"sub": "evil"},
    "secret-we-never-knew-and-will-never-accept-at-all",
    algorithm="HS256",
)
print("Verifying a token signed with an UNKNOWN secret:")
try:
    verify_with_rotation(bogus_token, CANDIDATE_SECRETS)
except InvalidSignatureError as exc:
    print("  -> rejected:", exc)

print()
print("Rotation recipe: sign with newest, verify against [newest, ...older],")
print("then remove the oldest secret once its tokens can no longer be valid.")
