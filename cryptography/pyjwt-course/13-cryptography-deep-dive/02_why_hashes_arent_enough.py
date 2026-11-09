"""
02 · Why a plain hash isn't enough — integrity vs. authenticity
================================================================

A bare hash gives you **integrity**: if you have the message *and* its digest,
you can detect accidental corruption by re-hashing and comparing.

But a bare hash gives you NO **authenticity**. Anyone who can change the message
can simply recompute the hash to match. There is no secret involved, so the
digest proves nothing about *who* produced it.

    integrity   = "the bits didn't change by accident"
    authenticity = "the bits came from someone who holds a secret/key"

This script plays the attacker: we intercept a (message, hash) pair, rewrite the
message, recompute the hash, and the receiver's naive check still passes. This
is the motivation for **MACs** (next script: HMAC) and digital signatures.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/02_why_hashes_arent_enough.py
"""

import hashlib


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def receiver_accepts(message: str, claimed_hash: str) -> bool:
    """A naive receiver: trusts the message if SHA-256(message) == claimed_hash."""
    return sha256_hex(message) == claimed_hash


def main() -> None:
    print("=" * 70)
    print("STEP 1 — Alice sends a message plus its SHA-256 hash")
    print("=" * 70)
    alice_message = "Pay Bob $100"
    alice_hash = sha256_hex(alice_message)
    print(f"message      : {alice_message!r}")
    print(f"sha256(msg)  : {alice_hash}")
    print("Alice transmits BOTH over the wire.\n")

    print("=" * 70)
    print("STEP 2 — The receiver verifies (integrity check passes)")
    print("=" * 70)
    print(f"receiver accepts original? {receiver_accepts(alice_message, alice_hash)}\n")

    print("=" * 70)
    print("STEP 3 — Mallory (attacker) intercepts and tampers")
    print("=" * 70)
    # Mallory rewrites the message AND recomputes the hash. No secret needed.
    mallory_message = "Pay Mallory $10000"
    mallory_hash = sha256_hex(mallory_message)
    print(f"forged message: {mallory_message!r}")
    print(f"forged hash   : {mallory_hash}")
    print("Mallory replaces both fields and forwards them on.\n")

    print("=" * 70)
    print("STEP 4 — The naive receiver is fooled")
    print("=" * 70)
    fooled = receiver_accepts(mallory_message, mallory_hash)
    print(f"receiver accepts forgery? {fooled}  <-- DISASTER")
    print(
        "\nThe hash matched, so the receiver 'trusts' the message — but it came\n"
        "from an attacker. A plain hash proves integrity, NOT authenticity."
    )

    print("\n" + "=" * 70)
    print("THE FIX (preview)")
    print("=" * 70)
    print(
        "Mix a SECRET into the hash so only key-holders can produce a valid tag:\n"
        "  - shared secret  -> HMAC  (HS256)      [next script]\n"
        "  - private key    -> signature (RS256)  [script 05]\n"
        "Mallory has neither, so she can no longer forge a matching tag."
    )


if __name__ == "__main__":
    main()
