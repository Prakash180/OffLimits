"""
07 · Microsoft Entra ID (Azure AD) validation — the canonical pattern
=====================================================================

This is the real-world pattern used to validate access/id tokens from Microsoft
Entra ID (formerly Azure AD). It is exactly what this repo's
``tests/validate.py`` does:

    from jwt import PyJWKClient
    jwk_client   = PyJWKClient(JWKS_URL)
    signing_key  = jwk_client.get_signing_key_from_jwt(access_token)
    decoded      = jwt.decode(
        access_token, signing_key.key, algorithms=["RS256"],
        audience=CLIENT_ID, issuer=ISSUER,
    )

where, for a tenant:

    JWKS_URL = https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys
    ISSUER   = https://login.microsoftonline.com/{TENANT_ID}/v2.0

``PyJWKClient`` downloads Microsoft's public keys, caches them, and uses the
token's ``kid`` to pick the right one. You then verify with RS256, pinning the
audience (your app/client id) and the issuer (your tenant).

Since there is no network here, we run a LOCAL simulation that mirrors the same
steps — local RS256 key, local JWKS, ``kid`` selection — and keep the genuine
Azure version in comments.

As of module 16, the course also ships a FULL local OIDC provider. This script's
runnable default now drives that real local IdP
(``pyjwt-course/16-local-identity-provider``) when it is importable — issuing a
real token and validating it via JWKS — then falls back to the inline offline
simulation below. Either way the validation call is the same shape as
``tests/validate.py``.

Run:
    uv run python \
        pyjwt-course/15-real-world-fastapi-oauth/07_entra_id_validation_pattern.py
"""

import json
import os
import sys
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

# Make the module-16 local IdP importable (it lives in a sibling folder whose
# name has hyphens, so we add it to sys.path rather than import by dotted name).
_LOCAL_IDP_DIR = os.path.join(
    os.path.dirname(__file__), "..", "16-local-identity-provider"
)
if os.path.isdir(_LOCAL_IDP_DIR):
    sys.path.insert(0, os.path.abspath(_LOCAL_IDP_DIR))

# --- Real Azure values would come from environment / discovery ---
TENANT_ID = "00000000-0000-0000-0000-000000000000"
CLIENT_ID = "api://my-app-client-id"
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
KID = "X5eXk4xyojNFum1kl2Ytv8dlNP4-c57dO6QGTVBwaNk"


# =====================================================================
# THE CANONICAL REAL-WORLD FUNCTION (live network — what validate.py runs)
# =====================================================================
def validate_token_azure(access_token: str) -> dict:
    """The production Entra ID validation. Requires network; shown for truth.

    This is intentionally NOT called in the offline demo below, but it IS the
    pattern you ship. It is identical in shape to repo tests/validate.py.
    """
    from jwt import PyJWKClient

    jwk_client = PyJWKClient(JWKS_URL)  # downloads + caches Microsoft's JWKS
    signing_key = jwk_client.get_signing_key_from_jwt(access_token)  # picks by kid
    return jwt.decode(
        access_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=CLIENT_ID,
        issuer=ISSUER,
    )


# =====================================================================
# OFFLINE SIMULATION — mirrors the steps above without any network
# =====================================================================
def get_signing_key_from_local_jwks(token: str, jwks: dict):
    """Local stand-in for PyJWKClient.get_signing_key_from_jwt: select by kid."""
    kid = jwt.get_unverified_header(token)["kid"]
    keyset = jwt.PyJWKSet.from_dict(jwks)
    for key in keyset.keys:
        if key.key_id == kid:
            return key  # a PyJWK; use .key for the underlying public key
    raise jwt.PyJWKClientError(f"no signing key for kid={kid!r}")


def validate_token_local(access_token: str, jwks: dict) -> dict:
    """Same shape as validate_token_azure, but against a local JWKS."""
    signing_key = get_signing_key_from_local_jwks(access_token, jwks)
    return jwt.decode(
        access_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=CLIENT_ID,
        issuer=ISSUER,
    )


def run_local_idp_default() -> bool:
    """Drive the real local IdP from module 16 and validate its token by JWKS.

    Returns True if the local IdP was available and the demo ran, else False
    (so the inline offline simulation still executes). Never raises: this keeps
    the script exiting 0 under ``uv run`` whether or not module 16 is present.
    """
    try:
        from idp.client import LocalIdPClient  # module 16, added to sys.path above
        from idp.server import AUDIENCE, ISSUER
    except ImportError:  # module 16 not importable -> use offline sim only
        return False

    print("=" * 72)
    print("RUNNABLE DEFAULT — validate a REAL token from the LOCAL IdP (module 16)")
    print("=" * 72)
    client = LocalIdPClient()
    tokens = client.login(scope="openid api.read")
    access_token = tokens["access_token"]
    jwks = client.jwks()

    # Identical shape to validate_token_azure(): select key by kid, then decode
    # with algorithms=["RS256"], pinning audience + issuer.
    kid = jwt.get_unverified_header(access_token)["kid"]
    keyset = jwt.PyJWKSet.from_dict(jwks)
    signing_key = next(k for k in keyset.keys if k.key_id == kid)
    claims = jwt.decode(
        access_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=AUDIENCE,
        issuer=ISSUER,
    )
    print(f"local issuer : {ISSUER}")
    print(f"local jwks   : {ISSUER}/jwks.json  (served by module 16's FastAPI app)")
    print(f"token kid    : {kid}")
    print("VALID ✔  trusted claims from the local IdP:")
    for key in ("iss", "aud", "sub", "scope"):
        print(f"  {key}: {claims[key]}")
    return True


def main() -> None:
    # =================================================================
    # RUNNABLE DEFAULT: validate against the REAL local IdP (module 16)
    # =================================================================
    # This is the same pattern as validate_token_azure(), but the JWKS comes
    # from our own fully-local OIDC provider instead of Microsoft. It issues a
    # genuine RS256 token through the auth-code flow and validates it by kid.
    if run_local_idp_default():
        print()  # spacer before the inline offline simulation below

    # --- Simulate Microsoft's signing key + JWKS endpoint ---
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    jwk = json.loads(RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update({"kid": KID, "use": "sig", "alg": "RS256"})
    jwks = {"keys": [jwk]}  # what JWKS_URL would return

    # --- Simulate an Entra ID access token for our API ---
    now = datetime.now(UTC)
    access_token = jwt.encode(
        {
            "iss": ISSUER,
            "aud": CLIENT_ID,
            "sub": "AAAAAAAAAAAAAAAAAAAAAA",
            "oid": "11111111-1111-1111-1111-111111111111",  # Entra object id
            "tid": TENANT_ID,
            "name": "Jane Doe",
            "preferred_username": "jane.doe@contoso.com",
            "scp": "Reports.Read",  # Entra delegated scope claim
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(hours=1),
        },
        private_pem,
        algorithm="RS256",
        headers={"kid": KID},
    )

    print("=" * 72)
    print("ENTRA ID VALIDATION PATTERN (offline simulation of validate.py)")
    print("=" * 72)
    print(f"ISSUER  : {ISSUER}")
    print(f"JWKS_URL: {JWKS_URL}")
    print(f"token kid: {jwt.get_unverified_header(access_token)['kid'][:24]}...\n")

    print("Step 1: select signing key from JWKS by the token's kid")
    signing_key = get_signing_key_from_local_jwks(access_token, jwks)
    print(f"        matched PyJWK kid = {signing_key.key_id[:24]}...")

    print("Step 2: jwt.decode(token, key, algorithms=['RS256'], audience, issuer)")
    claims = validate_token_local(access_token, jwks)
    print("        VALID ✔  trusted claims:")
    for k in ("aud", "iss", "name", "preferred_username", "scp", "tid"):
        print(f"          {k}: {claims[k]}")
    print()

    print("=" * 72)
    print("A token with the WRONG audience is rejected (defends your API)")
    print("=" * 72)
    bad = jwt.encode(
        {
            "iss": ISSUER,
            "aud": "api://some-other-app",
            "sub": "x",
            "exp": now + timedelta(hours=1),
        },
        private_pem,
        algorithm="RS256",
        headers={"kid": KID},
    )
    try:
        validate_token_local(bad, jwks)
        print("UNEXPECTED: wrong-audience token accepted!")
    except jwt.InvalidAudienceError as exc:
        print(f"wrong aud -> rejected: {type(exc).__name__}: {exc}")

    print("\nThe offline functions above are line-for-line equivalent to the live")
    print("Azure version in validate_token_azure() / repo tests/validate.py — the")
    print("only difference is PyJWKClient(JWKS_URL) fetching Microsoft's real keys.")


if __name__ == "__main__":
    main()
