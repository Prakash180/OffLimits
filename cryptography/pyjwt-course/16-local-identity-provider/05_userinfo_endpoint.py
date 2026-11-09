"""
05 · The /userinfo endpoint — a protected resource in action
============================================================

``/userinfo`` is the simplest *protected resource*: present a valid access
token as ``Authorization: Bearer <token>`` and it returns the user's claims.
Internally the IdP validates the token just like script 04 (kid -> JWKS key ->
RS256 decode with issuer+audience pinned). No valid token, no data.

This demonstrates the resource-server side of the contract: the access token is
the *key to the API*, and a bad/forged token is rejected with 401.

Run:
    uv run python pyjwt-course/16-local-identity-provider/05_userinfo_endpoint.py
"""

import json

from idp.client import LocalIdPClient


def main() -> None:
    client = LocalIdPClient()
    tokens = client.login(scope="openid profile email api.read")
    access_token = tokens["access_token"]

    print("=" * 72)
    print("GET /userinfo  WITH a valid bearer access token")
    print("=" * 72)
    resp = client.userinfo(access_token)
    print(f"HTTP {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@local.test"

    print("\n" + "=" * 72)
    print("GET /userinfo  WITH a garbage token  ->  401")
    print("=" * 72)
    bad = client.userinfo("not.a.realtoken")
    print(f"HTTP {bad.status_code}: {bad.json()['detail']}")
    assert bad.status_code == 401

    print("\n" + "=" * 72)
    print("GET /userinfo  WITH no Authorization header  ->  401")
    print("=" * 72)
    none = client.http.get("/userinfo")
    print(f"HTTP {none.status_code}: {none.json()['detail']}")
    assert none.status_code == 401

    print("\nOK ✔  the access token unlocks /userinfo; bad/missing tokens are 401.")


if __name__ == "__main__":
    main()
