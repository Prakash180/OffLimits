"""
01 · The "alg: none" attack — unsecured JWTs
=============================================

The JWT spec defines an *unsecured* token: ``"alg": "none"`` with an EMPTY
signature. It exists for cases where integrity is guaranteed by another layer,
but it is a notorious footgun: if a verifier accepts ``none``, an attacker can
strip the signature, rewrite the payload, and walk straight in.

This script shows:

1. How to (deliberately) build a ``none`` token with PyJWT.
2. That PyJWT REFUSES to decode it unless you *explicitly* opt in with
   ``algorithms=["none"]`` AND disable signature verification.
3. Why you must NEVER allow ``none`` for tokens from untrusted sources.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/01_alg_none_attack.py
"""

import jwt


def main() -> None:
    print("=" * 70)
    print("STEP 1 — Build an unsecured 'alg: none' token (no signature)")
    print("=" * 70)
    # PyJWT lets you create one, but only when you pass algorithm="none" and a
    # None key. Note the token ENDS WITH A DOT: the signature segment is empty.
    none_token = jwt.encode({"user": "attacker", "role": "admin"}, None, algorithm="none")
    print(f"none token: {none_token}")
    print(f"ends with empty signature segment? {none_token.endswith('.')}\n")

    print("=" * 70)
    print("STEP 2 — A safe verifier pins a real algorithm -> rejected")
    print("=" * 70)
    try:
        jwt.decode(none_token, "any-secret", algorithms=["HS256"])
        print("UNEXPECTED: none token accepted by an HS256 verifier?!")
    except jwt.InvalidAlgorithmError as exc:
        print(f"algorithms=['HS256'] -> rejected: {type(exc).__name__}: {exc}")
    except jwt.InvalidTokenError as exc:
        print(f"rejected: {type(exc).__name__}: {exc}")
    print("Because 'none' is not in the allow-list, the token is refused.\n")

    print("=" * 70)
    print("STEP 3 — Even allowing 'none' requires disabling signature checks")
    print("=" * 70)
    # PyJWT guards you twice: you must allow "none" AND turn off the signature
    # verification, otherwise it still raises.
    try:
        jwt.decode(none_token, algorithms=["none"])
        print("UNEXPECTED: decoded with just algorithms=['none']?!")
    except jwt.DecodeError as exc:
        print(f"algorithms=['none'] alone -> {type(exc).__name__}: {exc}")

    decoded = jwt.decode(
        none_token,
        algorithms=["none"],
        options={"verify_signature": False},  # explicit, scary opt-in
    )
    print(f"\nOnly with verify_signature=False does it decode: {decoded}")
    print("Notice: ZERO cryptographic proof was checked. Anyone wrote this.\n")

    print("=" * 70)
    print("THE LESSON")
    print("=" * 70)
    print("- NEVER include 'none' in `algorithms=[...]` for untrusted input.")
    print("- An attacker would flip role->admin, drop the signature, and submit.")
    print("- Always pin the exact signing algorithm(s) you actually issue.")


if __name__ == "__main__":
    main()
