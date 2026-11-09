"""
08 · RSA-PSS · 03 — PSS is PROBABILISTIC (RS is deterministic)
==============================================================

This is the defining behavioural difference between the two RSA schemes:

    PS256 (RSASSA-PSS)        -> randomised: signing injects a random *salt*,
                                  so signing the SAME payload twice yields TWO
                                  DIFFERENT tokens.

    RS256 (RSASSA-PKCS1-v1.5) -> deterministic: signing the SAME payload twice
                                  with the SAME key yields the SAME token,
                                  byte-for-byte.

Both are perfectly valid and both verify correctly. The randomness in PSS is a
security feature (it strengthens the proof of security and resists certain
attacks), not a bug.

We sign the identical payload twice with each scheme and compare.
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def main() -> None:
    # One key used for everything below.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    payload = {"sub": "carol", "msg": "sign me twice"}

    # --- PS256: expect TWO DIFFERENT tokens ---
    ps_a = jwt.encode(payload, private_pem, algorithm="PS256")
    ps_b = jwt.encode(payload, private_pem, algorithm="PS256")

    print("=" * 70)
    print("PS256 — sign identical payload twice")
    print("=" * 70)
    print("token A:", ps_a)
    print("token B:", ps_b)
    print("Tokens identical? ", ps_a == ps_b, " <- expect False (random salt)")
    # Both still verify just fine:
    jwt.decode(ps_a, public_pem, algorithms=["PS256"])
    jwt.decode(ps_b, public_pem, algorithms=["PS256"])
    print("Both PS256 tokens verify correctly. ✔")

    # --- RS256: expect TWO IDENTICAL tokens ---
    rs_a = jwt.encode(payload, private_pem, algorithm="RS256")
    rs_b = jwt.encode(payload, private_pem, algorithm="RS256")

    print("\n" + "=" * 70)
    print("RS256 — sign identical payload twice")
    print("=" * 70)
    print("token A:", rs_a)
    print("token B:", rs_b)
    print("Tokens identical? ", rs_a == rs_b, " <- expect True (deterministic)")
    print("\nSummary: PSS adds per-signature randomness; PKCS#1 v1.5 does not.")


if __name__ == "__main__":
    main()
