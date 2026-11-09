"""
idp.client — a tiny in-process client for the local IdP
=======================================================

A real OAuth2 client (your web app) talks to the IdP over HTTP. In the lesson
scripts we don't want to spin up a live server and block, so we drive the same
FastAPI ``app`` *in-process* with ``fastapi.testclient.TestClient`` — it speaks
the ASGI protocol directly, no socket, no network, but the request/response
shapes are byte-for-byte what a real HTTP client would see.

``LocalIdPClient`` wraps the four calls a confidential auth-code client makes:

    discovery()  -> the .well-known document
    jwks()       -> the public keys
    authorize()  -> obtain an authorization code (we read it from the redirect)
    exchange()   -> swap the code for tokens at /token
    refresh()    -> swap a refresh_token for fresh tokens
    userinfo()   -> call the protected /userinfo with the access token

``follow_redirects=False`` lets us inspect the 302 from ``/authorize`` and pull
the ``code`` out of its ``Location`` header — exactly how a browser-based client
receives the code at its redirect URI.
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from idp.server import app

# Default registered client + user used across the demos.
CLIENT_ID = "local-web-app"
CLIENT_SECRET = "local-web-app-secret"
REDIRECT_URI = "http://localhost:8443/callback"


class LocalIdPClient:
    """Drives the OAuth2 auth-code + OIDC flow against the local IdP app."""

    def __init__(self) -> None:
        # follow_redirects=False so we can read the code from /authorize's 302.
        self.http = TestClient(app, follow_redirects=False)

    # -- metadata -----------------------------------------------------------
    def discovery(self) -> dict:
        return self.http.get("/.well-known/openid-configuration").json()

    def jwks(self) -> dict:
        return self.http.get("/jwks.json").json()

    # -- authorization-code flow -------------------------------------------
    def authorize(
        self,
        *,
        scope: str = "openid profile email api.read",
        state: str = "xyz-state",
        nonce: str | None = None,
        username: str = "alice",
    ) -> str:
        """Hit /authorize and return the issued authorization ``code``.

        Reads the 302 redirect to the client's ``redirect_uri`` and extracts
        ``?code=...`` from its Location header, like a browser would.
        """
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": scope,
            "state": state,
            "username": username,
        }
        if nonce is not None:
            params["nonce"] = nonce
        resp = self.http.get("/authorize", params=params)
        assert resp.status_code == 302, resp.text
        location = resp.headers["location"]
        query = parse_qs(urlparse(location).query)
        return query["code"][0]

    def exchange(self, code: str) -> dict:
        """Exchange an authorization code for the token set at /token."""
        resp = self.http.post(
            "/token",
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )
        resp.raise_for_status()
        return resp.json()

    def refresh(self, refresh_token: str) -> dict:
        """Exchange a refresh_token for a fresh token set at /token."""
        resp = self.http.post(
            "/token",
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": refresh_token,
            },
        )
        resp.raise_for_status()
        return resp.json()

    # -- protected resource -------------------------------------------------
    def userinfo(self, access_token: str):
        """Call the protected /userinfo endpoint with a bearer access token.

        Returns the raw ``httpx.Response`` so callers can inspect status codes
        (e.g. assert a bad token yields 401).
        """
        return self.http.get(
            "/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def login(
        self,
        *,
        scope: str = "openid profile email api.read",
        nonce: str | None = None,
        username: str = "alice",
    ) -> dict:
        """Convenience: run authorize -> exchange and return the token set."""
        code = self.authorize(scope=scope, nonce=nonce, username=username)
        return self.exchange(code)
