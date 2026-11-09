"""
02 · Always pin algorithms — never trust the token's own header
================================================================

``jwt.decode()`` REQUIRES an ``algorithms=[...]`` allow-list. This is not
bureaucracy — it's the single most important line of defense against
algorithm-substitution attacks (see script 03).

The cardinal sin is to read the algorithm out of the *token's own header* and
feed it back to ``decode``. The header is attacker-controlled. If you trust it,
the attacker chooses how their token gets verified.

This script demonstrates:

1. Decoding works when you pin the correct algorithm.
2. Pinning the WRONG algorithm rejects the token.
3. The dangerous anti-pattern: ``algorithms=[unverified_header["alg"]]``.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/02_always_pin_algorithms.py
"""

import jwt

SECRET = "a-strong-shared-secret-at-least-32-bytes-long!!"


def main() -> None:
    token = jwt.encode({"sub": "alice"}, SECRET, algorithm="HS256")
    print(f"HS256 token: {token[:50]}...\n")

    print("=" * 70)
    print("GOOD — pin the exact algorithm you issued")
    print("=" * 70)
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    print(f"algorithms=['HS256'] -> {decoded}\n")

    print("=" * 70)
    print("GOOD — pinning the wrong algorithm rejects the token")
    print("=" * 70)
    try:
        jwt.decode(token, SECRET, algorithms=["HS512"])
        print("UNEXPECTED: HS256 token verified under HS512?!")
    except jwt.InvalidAlgorithmError as exc:
        print(f"algorithms=['HS512'] -> rejected: {type(exc).__name__}: {exc}\n")

    print("=" * 70)
    print("DANGEROUS ANTI-PATTERN — echoing the token's own 'alg'")
    print("=" * 70)
    # The header is NOT authenticated before verification; an attacker controls
    # it. Reading alg from here and trusting it defeats the whole allow-list.
    unverified_header = jwt.get_unverified_header(token)
    print(f"unverified header: {unverified_header}")
    print("BAD CODE:  jwt.decode(token, key, algorithms=[unverified_header['alg']])")
    print("Why it's bad: the attacker picks 'alg', so they pick how you verify.")
    print("It opens the door to the RS256->HS256 confusion attack (script 03).\n")

    print("=" * 70)
    print("RULE")
    print("=" * 70)
    print("Hard-code the algorithm(s) your system issues. Treat the token header")
    print("as a routing hint at most (e.g. selecting a key by 'kid'), never as")
    print("the source of truth for which algorithm to verify with.")


if __name__ == "__main__":
    main()
