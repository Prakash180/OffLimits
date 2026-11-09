"""
07 · Don't put secrets in the payload — JWTs are signed, not encrypted
======================================================================

The #1 misconception about JWTs: that the payload is "hidden". It is NOT. The
payload is merely base64url-encoded — trivially reversible by anyone, with no
key whatsoever. Signing protects *integrity*, not *confidentiality*.

This script plays an eavesdropper who never has any key, yet reads a "password"
and other sensitive claims straight out of an intercepted token.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/07_dont_put_secrets_in_payload.py
"""

import base64
import json

import jwt

SECRET = "a-strong-shared-secret-at-least-32-bytes-long!!"


def decode_payload_no_key(token: str) -> dict:
    """Read the payload with NO key and NO verification — pure base64url."""
    payload_seg = token.split(".")[1]
    payload_seg += "=" * (-len(payload_seg) % 4)  # restore base64 padding
    return json.loads(base64.urlsafe_b64decode(payload_seg))


def main() -> None:
    print("=" * 72)
    print("A developer foolishly stuffs sensitive data into the payload")
    print("=" * 72)
    token = jwt.encode(
        {
            "sub": "alice",
            "password": "hunter2",  # NEVER do this
            "ssn": "123-45-6789",  # NEVER do this
            "credit_card": "4111111111111111",  # NEVER do this
        },
        SECRET,
        algorithm="HS256",
    )
    print(f"token: {token}\n")

    print("=" * 72)
    print("An eavesdropper with NO KEY reads it all")
    print("=" * 72)
    # No secret, no public key, no verification — just base64 decoding.
    leaked = decode_payload_no_key(token)
    print("attacker recovered claims without any key:")
    for k, v in leaked.items():
        marker = "  <-- SENSITIVE!" if k in {"password", "ssn", "credit_card"} else ""
        print(f"  {k}: {v}{marker}")

    # PyJWT itself will read claims without verification too.
    same = jwt.decode(token, options={"verify_signature": False})
    print(f"\nsame via jwt.decode(verify_signature=False): keys={list(same)}\n")

    print("=" * 72)
    print("THE LESSON")
    print("=" * 72)
    print("- Signing != encryption. Anyone can read a JWT payload.")
    print("- Put ONLY non-sensitive identifiers/claims in the payload.")
    print("- Keep secrets server-side; reference them by id if needed.")
    print("- If you truly need confidentiality, use JWE (encrypted tokens),")
    print("  or transmit the data over TLS out-of-band — not in a JWS payload.")


if __name__ == "__main__":
    main()
