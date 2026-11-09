"""
01 · The OIDC discovery document — the provider's machine-readable manifest
===========================================================================

Every OpenID Connect provider publishes a JSON document at a well-known URL:

    GET {issuer}/.well-known/openid-configuration

It tells clients *everything* they need to talk to the provider — without
hard-coding a single URL. Real examples:

    Azure Entra ID : https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration
    Google         : https://accounts.google.com/.well-known/openid-configuration

Our LOCAL IdP serves the same document. This script fetches it (in-process,
no network) and explains the most important fields.

Run:
    uv run python pyjwt-course/16-local-identity-provider/01_discovery_document.py
"""

import json

from idp.client import LocalIdPClient

FIELD_NOTES = {
    "issuer": "The provider's identity. Baked into every token's `iss` claim; clients pin it.",
    "authorization_endpoint": "Where the browser is sent to log in and get an auth `code`.",
    "token_endpoint": "Where the client swaps the code (or a refresh_token) for tokens.",
    "userinfo_endpoint": "Protected endpoint returning user claims for a valid access token.",
    "jwks_uri": "Where the provider publishes its PUBLIC signing keys (the JWKS).",
    "id_token_signing_alg_values_supported": "Which algorithms id_tokens are signed with (RS256).",
    "grant_types_supported": "OAuth2 grants we accept (authorization_code, refresh_token).",
    "scopes_supported": "Scopes a client may request (openid, profile, email, api.*).",
}


def main() -> None:
    client = LocalIdPClient()
    doc = client.discovery()

    print("=" * 72)
    print("OIDC DISCOVERY DOCUMENT  (GET /.well-known/openid-configuration)")
    print("=" * 72)
    print(json.dumps(doc, indent=2))

    print("\n" + "=" * 72)
    print("WHAT EACH KEY FIELD MEANS")
    print("=" * 72)
    for field, note in FIELD_NOTES.items():
        value = doc.get(field)
        print(f"\n• {field}")
        print(f"    value: {value}")
        print(f"    note : {note}")

    print("\n" + "=" * 72)
    print("HOW THIS MAPS TO REAL PROVIDERS")
    print("=" * 72)
    print("A client library reads THIS document and auto-discovers the token,")
    print("authorize, userinfo and jwks URLs. Point it at Azure/Google instead")
    print("of http://localhost:9000 and the exact same code keeps working.")

    # Sanity checks so the lesson fails loudly if the contract drifts.
    assert doc["issuer"] == "http://localhost:9000"
    assert doc["jwks_uri"].endswith("/jwks.json")
    assert "RS256" in doc["id_token_signing_alg_values_supported"]
    print("\nOK ✔  discovery document is well-formed.")


if __name__ == "__main__":
    main()
