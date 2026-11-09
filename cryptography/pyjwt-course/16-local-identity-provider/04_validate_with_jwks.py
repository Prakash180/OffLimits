"""
04 · Validate the access token against the LOCAL JWKS (the Azure pattern)
========================================================================

This script validates a token EXACTLY the way this repo's ``tests/validate.py``
validates an Azure Entra ID token — only the JWKS source is our local IdP
instead of ``login.microsoftonline.com``.

The canonical steps (identical in shape to ``tests/validate.py``):

    1. read the `kid` from the token's UNVERIFIED header   (routing only)
    2. fetch the provider's JWKS                            (public keys)
    3. build the signing key whose `kid` matches
    4. jwt.decode(token, key, algorithms=["RS256"], audience=..., issuer=...)

If anything is off — bad signature, wrong audience, wrong issuer, expiry — step
4 raises and the token is rejected. We prove that with a TAMPERED token.

Run:
    uv run python pyjwt-course/16-local-identity-provider/04_validate_with_jwks.py
"""

import jwt
from idp.client import LocalIdPClient
from idp.server import AUDIENCE, ISSUER


def signing_key_from_jwks(token: str, jwks: dict):
    """Local stand-in for PyJWKClient.get_signing_key_from_jwt: pick by kid.

    PyJWKClient does precisely this against a live URL; here the JWKS dict came
    from our in-process IdP. The selection logic is identical.
    """
    kid = jwt.get_unverified_header(token)["kid"]
    keyset = jwt.PyJWKSet.from_dict(jwks)
    for key in keyset.keys:
        if key.key_id == kid:
            return key.key  # the underlying cryptography public key
    raise jwt.PyJWKClientError(f"no signing key in JWKS for kid={kid!r}")


def validate_access_token(token: str, jwks: dict) -> dict:
    """Validate a local access token — same call shape as tests/validate.py."""
    key = signing_key_from_jwks(token, jwks)
    return jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        audience=AUDIENCE,
        issuer=ISSUER,
    )
    # ------------------------------------------------------------------
    # LIVE-SERVER equivalent (when the IdP runs under `uv run uvicorn`):
    #
    #   from jwt import PyJWKClient
    #   jwk_client  = PyJWKClient("http://localhost:9000/jwks.json")
    #   signing_key = jwk_client.get_signing_key_from_jwt(token)
    #   claims = jwt.decode(
    #       token, signing_key.key, algorithms=["RS256"],
    #       audience=AUDIENCE, issuer=ISSUER,
    #   )
    #
    # This is line-for-line tests/validate.py, with localhost:9000 in place of
    # login.microsoftonline.com.
    # ------------------------------------------------------------------


def main() -> None:
    client = LocalIdPClient()
    tokens = client.login(scope="openid api.read")
    access_token = tokens["access_token"]
    jwks = client.jwks()

    print("=" * 72)
    print("VALIDATE ACCESS TOKEN AGAINST LOCAL JWKS (mirrors tests/validate.py)")
    print("=" * 72)
    print(f"issuer   : {ISSUER}")
    print(f"audience : {AUDIENCE}")
    print(f"token kid: {jwt.get_unverified_header(access_token)['kid']}")

    claims = validate_access_token(access_token, jwks)
    print("\nVALID ✔  trusted claims:")
    for k in ("iss", "aud", "sub", "scope", "roles"):
        print(f"  {k}: {claims[k]}")

    print("\n" + "=" * 72)
    print("TAMPERED TOKEN IS REJECTED")
    print("=" * 72)
    # Flip a character in the payload segment -> signature no longer matches.
    head, payload, sig = access_token.split(".")
    tampered_payload = ("A" if payload[0] != "A" else "B") + payload[1:]
    tampered = ".".join([head, tampered_payload, sig])
    try:
        validate_access_token(tampered, jwks)
        print("UNEXPECTED: tampered token accepted!")
        raise SystemExit(1)
    except jwt.PyJWTError as exc:
        print(f"rejected: {type(exc).__name__}: {exc}")

    print("\nOK ✔  genuine token validates; tampered token fails the signature.")


if __name__ == "__main__":
    main()
