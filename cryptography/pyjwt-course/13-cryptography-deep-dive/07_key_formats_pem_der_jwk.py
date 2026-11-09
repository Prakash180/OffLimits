"""
07 · Key formats — PEM, DER, and JWK for one RSA public key
============================================================

The same public key can be written in several encodings. Knowing them avoids a
lot of "why won't this key load?" pain.

* **PEM** — base64 of the DER bytes, wrapped in ``-----BEGIN PUBLIC KEY-----``
  headers. ASCII, copy-paste friendly. What you usually see in ``.pem`` files,
  env vars, and PyJWT examples.

* **DER** — the raw binary ASN.1 encoding. PEM is literally DER + base64 + a
  header. Used where binary is fine (TLS internals, some libraries).

* **JWK** — "JSON Web Key": a JSON object describing the key
  (``{"kty":"RSA","n":...,"e":...}``). This is what an OIDC provider's JWKS
  endpoint serves, and what ``PyJWKClient`` parses. ``n`` and ``e`` are the same
  RSA public numbers, base64url-encoded.

We take ONE RSA public key and emit all three.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/07_key_formats_pem_der_jwk.py
"""

import json

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


def main() -> None:
    # One key, three representations.
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    print("=" * 70)
    print("FORMAT 1 — PEM (base64 text with BEGIN/END headers)")
    print("=" * 70)
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    print(pem.decode())
    print("Used in: .pem files, env vars, most PyJWT key arguments.\n")

    print("=" * 70)
    print("FORMAT 2 — DER (raw binary ASN.1; shown as a hex preview)")
    print("=" * 70)
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    print(f"DER length: {len(der)} bytes")
    print(f"DER hex preview: {der[:48].hex()}...")
    print("PEM is exactly this DER, base64-encoded, with header/footer lines.\n")

    print("=" * 70)
    print("FORMAT 3 — JWK (JSON, what a JWKS endpoint serves)")
    print("=" * 70)
    # PyJWT can serialise a public key straight to a JWK string.
    jwk_str = RSAAlgorithm.to_jwk(public_key)
    jwk = json.loads(jwk_str)
    pretty = json.dumps(jwk, indent=2)
    # n is long; truncate it for readable teaching output.
    if "n" in jwk:
        jwk_preview = dict(jwk)
        jwk_preview["n"] = jwk_preview["n"][:40] + "...(truncated)"
        pretty = json.dumps(jwk_preview, indent=2)
    print(pretty)
    print(f"\nkty = {jwk.get('kty')}  (key type: RSA)")
    print(f"e   = {jwk.get('e')}  (public exponent 65537 -> 'AQAB' in base64url)")
    print(f"n   = the RSA modulus, base64url-encoded ({len(jwk.get('n', ''))} chars)")
    print("Used in: OIDC /jwks_uri responses, parsed by PyJWKClient/PyJWKSet.")

    print("\n" + "=" * 70)
    print("ROUND-TRIP — JWK back into a usable public key")
    print("=" * 70)
    reconstructed = RSAAlgorithm.from_jwk(jwk_str)
    same = reconstructed.public_numbers() == public_key.public_numbers()
    print(f"from_jwk(to_jwk(key)) yields the same public numbers? {same}")
    print("This is precisely how JWKS-based verification rebuilds keys.")


if __name__ == "__main__":
    main()
