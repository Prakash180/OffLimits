"""06 · The header drives key selection — the foundation of JWKS.

This script ties the whole module together into the pattern that every JWKS-based
system (Auth0, Okta, Microsoft Entra ID, Google, ...) uses under the hood:

    1. The issuer holds a KEYSTORE: {kid -> key}.
    2. When signing, it picks a key and stamps that key's ``kid`` into the header.
    3. The verifier reads the ``kid`` from the *unverified* header.
    4. It looks up the matching key in its own copy of the keystore.
    5. It performs a full, signature-checked ``jwt.decode`` with that key.

Swap the in-memory dict for "a JWKS document fetched over HTTPS and cached" and
you have exactly what ``PyJWKClient`` does (module 11). The mechanics are
identical; only the *source* of the keys differs.

We use HMAC secrets here to keep the focus on the selection pattern. In module 11
the same flow runs with RSA public keys from a real JWKS.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/10-headers-and-kid/06_header_drives_key_selection.py
"""

import jwt

# The issuer's keystore — multiple active keys, each addressable by kid.
KEYSTORE = {
    "2024-key": "secret-from-last-year-padded-to-32-bytes-ok!",
    "2025-key": "secret-currently-in-use-padded-to-32-bytes!",
}
ALLOWED_ALGS = ["HS256"]


def sign(payload: dict, kid: str) -> str:
    """Issuer side: pick the key by kid and advertise that kid in the header."""
    return jwt.encode(payload, KEYSTORE[kid], algorithm="HS256", headers={"kid": kid})


def verify(token: str) -> dict:
    """Verifier side: kid -> key lookup -> signature-checked decode."""
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if kid is None:
        raise jwt.InvalidTokenError("Token has no 'kid' header")
    if kid not in KEYSTORE:
        raise jwt.InvalidKeyError(f"Unknown kid: {kid!r}")
    key = KEYSTORE[kid]
    return jwt.decode(token, key, algorithms=ALLOWED_ALGS)


def main() -> None:
    print("Keystore kids:", list(KEYSTORE))
    print()

    for kid in KEYSTORE:
        token = sign({"resource": f"signed-with-{kid}"}, kid)
        claims = verify(token)
        print(f"kid={kid}: verified -> {claims}")

    print()

    # An unknown kid (e.g. a retired or forged key id) is cleanly rejected.
    forged = jwt.encode(
        {"x": 1}, "whatever-secret-padded-to-at-least-32-bytes", algorithm="HS256",
        headers={"kid": "ghost"},
    )
    print("Token with unknown kid 'ghost':")
    try:
        verify(forged)
    except jwt.InvalidKeyError as exc:
        print(f"  ❌ {type(exc).__name__}: {exc}")

    print()
    print("✅ This kid -> key -> decode flow IS the heart of JWKS (next module).")


if __name__ == "__main__":
    main()
