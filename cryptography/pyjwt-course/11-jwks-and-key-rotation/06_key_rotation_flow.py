"""06 · A key-rotation flow, simulated locally.

Key rotation is *the* reason JWKS exists. You periodically retire an old signing
key and start using a new one — but you can't flip a switch instantly, because
tokens signed by the old key are still circulating and valid. The solution:
**publish both keys at once** for an overlap window.

The lifecycle this script simulates:

    Phase 1 — only key A exists. Tokens signed by A. JWKS = {A}.
    Phase 2 — rotation begins. New key B added. JWKS = {A, B}.
              Start signing new tokens with B (kid=B).
              Verifier with JWKS={A,B} validates BOTH old-A and new-B tokens.
    Phase 3 — A is fully retired. JWKS = {B}.
              Old A-signed tokens now FAIL (their kid isn't in the set).

This is precisely how providers rotate without downtime: overlap, then drop.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/11-jwks-and-key-rotation/06_key_rotation_flow.py
"""

import json

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


def public_jwk(public_key, kid: str) -> dict:
    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return jwk


def make_jwks(*pairs) -> dict:
    """Build a JWKS from (public_key, kid) pairs."""
    return {"keys": [public_jwk(pub, kid) for pub, kid in pairs]}


def try_verify(token: str, jwks: dict) -> str:
    """Verify a token against a JWKS, returning a human-readable outcome."""
    jwks_set = jwt.PyJWKSet.from_dict(jwks)
    kid = jwt.get_unverified_header(token)["kid"]
    try:
        signing_key = jwks_set[kid]  # KeyError-like failure if kid not published
    except KeyError:
        return f"REJECTED — kid {kid!r} is not in the current JWKS"
    try:
        claims = jwt.decode(token, signing_key.key, algorithms=["RS256"])
    except jwt.PyJWTError as exc:
        return f"REJECTED — {type(exc).__name__}"
    return f"VERIFIED — {claims}"


def main() -> None:
    key_a = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_b = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # A token issued early in life, signed by key A.
    token_old = jwt.encode({"era": "old"}, key_a, algorithm="RS256", headers={"kid": "A"})

    # --- Phase 1: only A is published ---
    jwks_v1 = make_jwks((key_a.public_key(), "A"))
    print("Phase 1 — JWKS = {A}")
    print(f"  old token (kid=A): {try_verify(token_old, jwks_v1)}")
    print()

    # --- Phase 2: rotation — A and B both published; new tokens signed by B ---
    jwks_v2 = make_jwks((key_a.public_key(), "A"), (key_b.public_key(), "B"))
    token_new = jwt.encode({"era": "new"}, key_b, algorithm="RS256", headers={"kid": "B"})
    print("Phase 2 — JWKS = {A, B}  (overlap window)")
    print(f"  old token (kid=A): {try_verify(token_old, jwks_v2)}")
    print(f"  new token (kid=B): {try_verify(token_new, jwks_v2)}")
    print()

    # --- Phase 3: A retired; only B remains ---
    jwks_v3 = make_jwks((key_b.public_key(), "B"))
    print("Phase 3 — JWKS = {B}  (A retired)")
    print(f"  old token (kid=A): {try_verify(token_old, jwks_v3)}")
    print(f"  new token (kid=B): {try_verify(token_new, jwks_v3)}")
    print()
    print("✅ Overlap keeps old tokens valid; dropping A finally invalidates them.")


if __name__ == "__main__":
    main()
