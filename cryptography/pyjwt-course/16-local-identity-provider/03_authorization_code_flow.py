"""
03 · The authorization-code flow, end to end (locally)
======================================================

This is the heart of OAuth2 + OIDC. The confidential auth-code flow:

    1. Client redirects the browser to  GET /authorize?...   (user logs in)
    2. Provider redirects back with      ?code=...           (a one-time code)
    3. Client POSTs the code to          POST /token         (+ client_secret)
    4. Provider returns                  access_token, id_token, refresh_token

We run all four steps against the LOCAL IdP in-process and decode the tokens so
you can see exactly what comes out. (Token VALIDATION via JWKS is script 04.)

Run:
    uv run python pyjwt-course/16-local-identity-provider/03_authorization_code_flow.py
"""

import json

import jwt
from idp.client import LocalIdPClient


def show(label: str, token: str) -> None:
    """Pretty-print a JWT's header + payload WITHOUT verifying (inspection)."""
    header = jwt.get_unverified_header(token)
    payload = jwt.decode(token, options={"verify_signature": False})
    print(f"\n{label}")
    print(f"  header : {json.dumps(header)}")
    print(f"  payload: {json.dumps(payload, indent=2)}")


def main() -> None:
    client = LocalIdPClient()

    print("=" * 72)
    print("STEP 1+2 · GET /authorize  ->  one-time authorization code")
    print("=" * 72)
    code = client.authorize(
        scope="openid profile email api.read",
        nonce="n-onceabc123",
        state="opaque-state-xyz",
    )
    print(f"Received authorization code: {code[:16]}... (single-use, short-lived)")

    print("\n" + "=" * 72)
    print("STEP 3+4 · POST /token  ->  exchange code for tokens")
    print("=" * 72)
    tokens = client.exchange(code)
    print("Token response fields:")
    for k, v in tokens.items():
        shown = v if k in {"token_type", "expires_in", "scope"} else f"{str(v)[:24]}..."
        print(f"  {k}: {shown}")

    show("ACCESS TOKEN (for the resource API — note aud + scope)", tokens["access_token"])
    show("ID TOKEN (OIDC identity for the client — note nonce/email/name)", tokens["id_token"])

    print("\n" + "=" * 72)
    print("WHAT JUST HAPPENED")
    print("=" * 72)
    print("• The code was exchanged exactly once; replaying it would 400.")
    print("• access_token.aud = the API; id_token.aud = the client_id.")
    print("• Both are RS256-signed with a `kid` pointing at the JWKS (script 04).")

    assert {"access_token", "id_token", "refresh_token"} <= tokens.keys()
    assert tokens["token_type"] == "Bearer"
    print("\nOK ✔  full authorization-code flow completed locally.")


if __name__ == "__main__":
    main()
