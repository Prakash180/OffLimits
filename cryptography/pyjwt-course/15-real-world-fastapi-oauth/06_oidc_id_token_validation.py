"""
06 · OIDC id_token validation — verifying against a JWKS by `kid`
=================================================================

OpenID Connect (OIDC) sits on top of OAuth2 and adds an **id_token**: a JWT that
proves *who the user is* to the client application. Its standard claims:

* ``iss``   — the OIDC provider (issuer).
* ``aud``   — the client_id this id_token was issued for.
* ``sub``   — stable unique user id at the provider.
* ``exp``/``iat`` — validity window.
* ``nonce`` — binds the token to the original auth request (replay defense).
* ``email``, ``name``, ... — identity claims (when those scopes were granted).

id_tokens are signed with the provider's PRIVATE key (RS256). Clients fetch the
provider's PUBLIC keys from its **JWKS** (``jwks_uri`` in the discovery doc) and
select the right key by the token's ``kid`` header.

NO NETWORK here: we sign a local RS256 id_token, publish a local JWKS, and
validate by ``kid`` — exactly mirroring the real flow. The real ``PyJWKClient``
version is shown in comments.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/15-real-world-fastapi-oauth/06_oidc_id_token_validation.py
"""

import json
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

ISSUER = "https://idp.example.com"
CLIENT_ID = "my-oidc-client-id"  # this is the id_token's audience
KID = "idp-signing-key-2026"


def build_local_jwks(public_key, kid: str) -> dict:
    """Serialise an RSA public key into a one-key JWKS, like a provider's."""
    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return {"keys": [jwk]}


def select_key_by_kid(jwks: dict, kid: str):
    """Pick the signing key from a JWKS whose 'kid' matches the token header."""
    keyset = jwt.PyJWKSet.from_dict(jwks)
    for key in keyset.keys:
        if key.key_id == kid:
            return key.key
    raise jwt.PyJWKClientError(f"no key in JWKS with kid={kid!r}")


def validate_id_token(id_token: str, jwks: dict) -> dict:
    """Validate an OIDC id_token against a JWKS, selecting the key by kid."""
    header = jwt.get_unverified_header(id_token)  # routing only: read the kid
    signing_key = select_key_by_kid(jwks, header["kid"])
    return jwt.decode(
        id_token,
        signing_key,
        algorithms=["RS256"],
        audience=CLIENT_ID,  # id_token aud MUST equal our client_id
        issuer=ISSUER,
        options={"require": ["exp", "iss", "aud", "sub"]},
    )

    # ------------------------------------------------------------------
    # REAL-WORLD (live network) version — fetch the JWKS from the provider:
    #
    #   from jwt import PyJWKClient
    #   jwks_client = PyJWKClient("https://idp.example.com/.well-known/jwks.json")
    #   signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    #   claims = jwt.decode(
    #       id_token, signing_key.key, algorithms=["RS256"],
    #       audience=CLIENT_ID, issuer=ISSUER,
    #   )
    #
    # The jwks_uri itself comes from the OIDC discovery document at
    #   https://idp.example.com/.well-known/openid-configuration
    # ------------------------------------------------------------------


def main() -> None:
    # --- Provider side: key + signed id_token ---
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    jwks = build_local_jwks(key.public_key(), KID)

    now = datetime.now(UTC)
    id_token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": CLIENT_ID,
            "sub": "248289761001",
            "iat": now,
            "exp": now + timedelta(hours=1),
            "nonce": "n-0S6_WzA2Mj",
            "email": "jane.doe@example.com",
            "name": "Jane Doe",
        },
        private_pem,
        algorithm="RS256",
        headers={"kid": KID},
    )

    print("=" * 72)
    print("PROVIDER published this JWKS (public keys, served at jwks_uri)")
    print("=" * 72)
    preview = json.loads(json.dumps(jwks))
    preview["keys"][0]["n"] = preview["keys"][0]["n"][:32] + "...(truncated)"
    print(json.dumps(preview, indent=2))
    print(f"\nid_token header: {jwt.get_unverified_header(id_token)}\n")

    print("=" * 72)
    print("CLIENT validates the id_token by selecting the key via 'kid'")
    print("=" * 72)
    claims = validate_id_token(id_token, jwks)
    print("VALID id_token. Trusted identity claims:")
    for k in ("iss", "aud", "sub", "email", "name", "nonce"):
        print(f"  {k}: {claims[k]}")
    print()

    print("=" * 72)
    print("ATTACK CHECK — an id_token for a DIFFERENT client is rejected")
    print("=" * 72)
    wrong_aud = jwt.encode(
        {
            "iss": ISSUER,
            "aud": "some-other-client",
            "sub": "248289761001",
            "exp": now + timedelta(hours=1),
        },
        private_pem,
        algorithm="RS256",
        headers={"kid": KID},
    )
    try:
        validate_id_token(wrong_aud, jwks)
        print("UNEXPECTED: id_token for another client accepted!")
    except jwt.InvalidAudienceError as exc:
        print(f"wrong aud -> rejected: {type(exc).__name__}: {exc}")

    print("\nAlways check aud == your client_id and verify nonce against the one")
    print("you sent in the auth request to defeat token replay/injection.")


if __name__ == "__main__":
    main()
