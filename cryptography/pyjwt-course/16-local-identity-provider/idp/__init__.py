"""
Local Identity Provider (IdP) package
=====================================

A tiny, fully-local, offline OAuth2 + OpenID Connect (OIDC) identity provider
built on FastAPI + PyJWT + cryptography. It mirrors the real-world shape of
Microsoft Entra ID / Google / Auth0 so the course can teach (and *test*) the
authorization-code flow, JWKS validation, refresh tokens, and key rotation
without ever touching the network.

Modules
-------
* ``idp.keys``   — RSA-2048 signing keys, a stable ``kid``, JWKS publication,
                   and a two-key (current + next) manager for rotation demos.
* ``idp.server`` — the FastAPI ``app`` with the OIDC endpoints
                   (discovery, jwks, authorize, token, userinfo).
* ``idp.client`` — a thin in-process client that drives the flow for the demos.

Everything is signed RS256 with the ``kid`` in the JWT header, exactly like a
production provider, so ``jwt.decode`` + JWKS validation behaves identically.
"""

from idp.keys import KeyManager, SigningKey, generate_signing_key

__all__ = ["KeyManager", "SigningKey", "generate_signing_key"]
