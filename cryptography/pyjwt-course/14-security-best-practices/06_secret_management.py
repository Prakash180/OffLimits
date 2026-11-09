"""
06 · Secret management — strong secrets, never hardcoded
========================================================

For HS256 your secret IS your security. If it is weak or leaked, anyone can mint
valid tokens. Two rules:

1. **Make it strong and random.** Use ``secrets.token_urlsafe()`` to generate
   high-entropy keys (>= 32 bytes for SHA-256, per RFC 7518 §3.2). Do not use
   dictionary words, app names, or "changeme".
2. **Never hardcode it.** Load from an environment variable / secrets manager so
   the secret is not committed to source control.

We contrast a weak secret with a strong one and reason (without actually brute
forcing) about how astronomically harder the strong one is to guess.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/06_secret_management.py
"""

import math
import os
import secrets

import jwt


def entropy_bits(num_chars: int, alphabet_size: int) -> float:
    """Rough Shannon entropy in bits for a random string of given length."""
    return num_chars * math.log2(alphabet_size)


def main() -> None:
    print("=" * 72)
    print("WEAK secret — guessable, low entropy")
    print("=" * 72)
    weak = "password"  # the kind of thing that ends up in real code, sadly
    weak_bits = entropy_bits(len(weak), 26)  # pretend lowercase only
    print(f"weak secret: {weak!r}")
    print(f"~entropy: {weak_bits:.0f} bits — in any wordlist; cracked instantly.")
    print("An attacker who guesses this can forge ANY token you 'trust'.\n")

    print("=" * 72)
    print("STRONG secret — generated with secrets.token_urlsafe(32)")
    print("=" * 72)
    strong = secrets.token_urlsafe(32)  # 32 random bytes -> ~43 url-safe chars
    strong_bits = 32 * 8  # 32 bytes of entropy
    print(f"strong secret: {strong}")
    print(f"length: {len(strong)} chars, ~{strong_bits} bits of entropy.")
    print(f"search space: 2^{strong_bits} ~= 10^{strong_bits * 0.301:.0f} keys.")
    print("Brute force is infeasible — more keys than atoms in the observable")
    print("universe. (We do NOT brute force here; the math alone settles it.)\n")

    print("=" * 72)
    print("NEVER HARDCODE — load the secret from the environment")
    print("=" * 72)
    # In production: os.environ["JWT_SECRET"], a vault, or a managed KMS.
    # We fall back to the generated value so this demo is self-contained.
    runtime_secret = os.getenv("JWT_SECRET", strong)
    source = "env var JWT_SECRET" if os.getenv("JWT_SECRET") else "generated fallback"
    print(f"secret source: {source}")
    token = jwt.encode({"sub": "alice"}, runtime_secret, algorithm="HS256")
    decoded = jwt.decode(token, runtime_secret, algorithms=["HS256"])
    print(f"token signed+verified with the runtime secret: {decoded}\n")

    print("=" * 72)
    print("CHECKLIST")
    print("=" * 72)
    print("- HS256 secret: >= 32 random bytes via secrets.token_urlsafe(32).")
    print("- Store in env/secret manager; never commit to git.")
    print("- Rotate periodically and on any suspected leak.")
    print("- Prefer asymmetric (RS256/ES256) when third parties must verify, so")
    print("  no shared secret needs distributing at all.")


if __name__ == "__main__":
    main()
