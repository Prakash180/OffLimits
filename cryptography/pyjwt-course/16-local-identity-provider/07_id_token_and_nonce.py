"""
07 · The OIDC id_token and the nonce round-trip
===============================================

OAuth2 gives you an **access_token** (a key to an API). OpenID Connect adds an
**id_token**: proof of *who logged in*, issued FOR THE CLIENT.

Key differences:

    access_token   aud = the resource API   "what may I call?"
    id_token       aud = your client_id     "who is this user?"

The id_token also carries a ``nonce``: a random value the client generates and
sends on ``/authorize``. The provider copies it into the id_token. The client
then checks ``id_token.nonce == the nonce I sent`` — defeating replay/injection
of a stolen id_token.

This script logs in with a nonce, validates the id_token's iss/aud/exp, and
verifies the nonce round-trips.

Run:
    uv run python pyjwt-course/16-local-identity-provider/07_id_token_and_nonce.py
"""

import jwt
from idp.client import CLIENT_ID, LocalIdPClient
from idp.server import ISSUER


def signing_key_from_jwks(token: str, jwks: dict):
    """Select the public key from the JWKS whose kid matches the token."""
    kid = jwt.get_unverified_header(token)["kid"]
    keyset = jwt.PyJWKSet.from_dict(jwks)
    for key in keyset.keys:
        if key.key_id == kid:
            return key.key
    raise jwt.PyJWKClientError(f"no key for kid={kid!r}")


def validate_id_token(id_token: str, jwks: dict, expected_nonce: str) -> dict:
    """Validate an id_token: signature, iss, aud(=client_id), exp, and nonce."""
    key = signing_key_from_jwks(id_token, jwks)
    claims = jwt.decode(
        id_token,
        key,
        algorithms=["RS256"],
        audience=CLIENT_ID,  # id_token audience MUST be our client_id
        issuer=ISSUER,
        options={"require": ["exp", "iss", "aud", "sub"]},
    )
    # nonce is application-level: PyJWT won't check it for us.
    if claims.get("nonce") != expected_nonce:
        raise jwt.InvalidTokenError("nonce mismatch — possible replay")
    return claims


def main() -> None:
    client = LocalIdPClient()
    sent_nonce = "nonce-7f3a-please-echo-me"

    print("=" * 72)
    print("LOGIN requesting an id_token, sending a nonce")
    print("=" * 72)
    tokens = client.login(scope="openid profile email", nonce=sent_nonce)
    id_token = tokens["id_token"]
    jwks = client.jwks()
    print(f"sent nonce     : {sent_nonce}")
    print(f"id_token header: {jwt.get_unverified_header(id_token)}")

    print("\n" + "=" * 72)
    print("VALIDATE id_token (iss / aud=client_id / exp) and nonce round-trip")
    print("=" * 72)
    claims = validate_id_token(id_token, jwks, sent_nonce)
    print("VALID ✔  identity claims:")
    for k in ("iss", "aud", "sub", "email", "name", "nonce"):
        print(f"  {k}: {claims[k]}")
    print(f"\naud == client_id ({CLIENT_ID}): {claims['aud'] == CLIENT_ID}")
    print(f"nonce echoed back correctly    : {claims['nonce'] == sent_nonce}")

    print("\n" + "=" * 72)
    print("ATTACK CHECK · a token presented with the WRONG expected nonce fails")
    print("=" * 72)
    try:
        validate_id_token(id_token, jwks, "some-other-nonce")
        print("UNEXPECTED: mismatched nonce accepted!")
        raise SystemExit(1)
    except jwt.InvalidTokenError as exc:
        print(f"rejected: {type(exc).__name__}: {exc}")

    print("\nOK ✔  id_token validated; nonce binds it to this exact login.")


if __name__ == "__main__":
    main()
