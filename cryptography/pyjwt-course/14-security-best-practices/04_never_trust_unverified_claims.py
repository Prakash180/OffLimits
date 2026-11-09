"""
04 · Never trust unverified claims — decode-without-verify is for routing only
===============================================================================

Sometimes you need to peek inside a token BEFORE you can verify it — most often
to read the ``kid`` (key id) or ``iss`` so you know *which* key to fetch. PyJWT
supports this via ``jwt.get_unverified_header()`` and
``jwt.decode(..., options={"verify_signature": False})``.

The iron rule: **unverified claims may be used to ROUTE, never to TRUST.**
An attacker can put anything in an unverified payload. Authorization decisions
(is this user an admin? which tenant?) must come only from a token whose
signature you have validated.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/04_never_trust_unverified_claims.py
"""

import jwt

SECRET = "a-strong-shared-secret-at-least-32-bytes-long!!"


def main() -> None:
    token = jwt.encode(
        {"sub": "alice", "role": "user", "kid_hint": "tenant-A"},
        SECRET,
        algorithm="HS256",
        headers={"kid": "key-2026-06"},
    )

    print("=" * 72)
    print("LEGITIMATE USE — peek at the header to choose a verification key")
    print("=" * 72)
    header = jwt.get_unverified_header(token)
    print(f"unverified header: {header}")
    print(f"-> route: fetch signing key with kid={header['kid']!r} (then verify).\n")

    print("=" * 72)
    print("LEGITIMATE USE — peek at unverified claims for routing only")
    print("=" * 72)
    unverified = jwt.decode(token, options={"verify_signature": False})
    print(f"unverified claims: {unverified}")
    print("OK to use 'iss'/'kid' to look up a key. NOT ok to trust 'role' yet.\n")

    print("=" * 72)
    print("THE DANGER — an attacker forges claims in an UNSIGNED-CHECK read")
    print("=" * 72)
    # Attacker crafts a token we never issued; they don't know the secret.
    forged = jwt.encode({"sub": "mallory", "role": "admin"}, "attacker-guessed-secret-32-bytes-long!!!", algorithm="HS256")
    sneaky = jwt.decode(forged, options={"verify_signature": False})
    print(f"attacker's unverified payload: {sneaky}")
    print("If you authorize off THIS, mallory is 'admin'. Catastrophe.\n")

    print("=" * 72)
    print("THE CORRECT FLOW — verify the signature, THEN read claims to trust")
    print("=" * 72)
    try:
        jwt.decode(forged, SECRET, algorithms=["HS256"])
        print("UNEXPECTED: forged token verified?!")
    except jwt.InvalidSignatureError as exc:
        print(f"verify forged token -> {type(exc).__name__}: {exc} (rejected)")

    trusted = jwt.decode(token, SECRET, algorithms=["HS256"])
    print(f"verify genuine token -> trusted claims: {trusted}")
    print(f"NOW it is safe to authorize on role={trusted['role']!r}.\n")

    print("=" * 72)
    print("RULE: verify_signature=False is for plumbing (kid/iss lookup), never")
    print("for security decisions. Trust flows only from a verified token.")
    print("=" * 72)


if __name__ == "__main__":
    main()
