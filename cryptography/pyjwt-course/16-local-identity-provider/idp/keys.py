"""
idp.keys — RSA signing keys, JWKS publication, and rotation
===========================================================

A production identity provider signs every token with the **private** half of
an RSA keypair and publishes only the **public** half as a JWKS (JSON Web Key
Set) at ``jwks_uri``. Each key carries a ``kid`` (key id) so that a client,
given a token, can pick the exact public key to verify it with.

This module gives the local IdP the same machinery:

* ``SigningKey``  — one RSA-2048 keypair + a stable ``kid``; knows how to emit
  its public half as a JWK via ``jwt.algorithms.RSAAlgorithm.to_jwk``.
* ``KeyManager``  — holds TWO keys at once (``current`` + ``next``) so we can
  demonstrate **key rotation**: both are published in the JWKS, new tokens are
  signed by ``current``, and ``rotate()`` promotes ``next`` to ``current`` and
  mints a fresh ``next`` (retiring the old key, which then disappears from the
  JWKS so its tokens stop validating).

Only PyJWT 2.13.0 public API is used: ``jwt.algorithms.RSAAlgorithm.to_jwk``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


@dataclass
class SigningKey:
    """One RSA-2048 keypair with a stable ``kid`` used to sign/verify tokens."""

    kid: str
    private_key: rsa.RSAPrivateKey

    @property
    def public_key(self) -> rsa.RSAPublicKey:
        """The public half — what gets published in the JWKS."""
        return self.private_key.public_key()

    @property
    def private_pem(self) -> str:
        """PKCS#8 PEM of the private key (handy for logging / inspection)."""
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

    @property
    def public_pem(self) -> str:
        """SubjectPublicKeyInfo PEM of the public key."""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

    def to_jwk(self) -> dict:
        """Serialise the PUBLIC key as a JWK dict, tagged with kid/use/alg.

        ``RSAAlgorithm.to_jwk`` produces the RSA-specific JWK fields
        (``kty``, ``n``, ``e``). We add the metadata a real JWKS includes so
        clients can route by ``kid`` and know the algorithm.
        """
        jwk = json.loads(RSAAlgorithm.to_jwk(self.public_key))
        jwk.update({"kid": self.kid, "use": "sig", "alg": "RS256"})
        return jwk


def generate_signing_key(kid: str) -> SigningKey:
    """Create a brand-new RSA-2048 signing key with the given ``kid``."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return SigningKey(kid=kid, private_key=private_key)


class KeyManager:
    """Holds the IdP's signing keys and publishes their public JWKS.

    Two keys are kept live at once so JWKS validation keeps working across a
    rotation window:

    * ``current`` — signs all newly-issued tokens.
    * ``next``    — already published, ready to take over; lets clients that
      cached the JWKS recognise it the instant we rotate.

    ``rotate()`` retires ``current``, promotes ``next`` to ``current``, and
    generates a fresh ``next``. The retired key is dropped from the published
    JWKS, so any token still signed by it will fail validation (no matching
    ``kid``) — exactly how real providers age keys out.
    """

    def __init__(self, kid_prefix: str = "local-key") -> None:
        self._prefix = kid_prefix
        self._counter = 0
        self.current = self._new_key()
        self.next = self._new_key()

    def _new_key(self) -> SigningKey:
        self._counter += 1
        return generate_signing_key(f"{self._prefix}-{self._counter:04d}")

    @property
    def signing_key(self) -> SigningKey:
        """The key used to SIGN new tokens (always ``current``)."""
        return self.current

    def published_keys(self) -> list[SigningKey]:
        """All keys currently advertised in the JWKS (current + next)."""
        return [self.current, self.next]

    def jwks(self) -> dict:
        """The public JWKS document served at ``jwks_uri``."""
        return {"keys": [key.to_jwk() for key in self.published_keys()]}

    def get_published_key(self, kid: str | None) -> SigningKey | None:
        """Return the published key matching ``kid``, or ``None`` if retired."""
        for key in self.published_keys():
            if key.kid == kid:
                return key
        return None

    def rotate(self) -> SigningKey:
        """Promote ``next`` -> ``current``, mint a fresh ``next``.

        Returns the now-RETIRED key so callers/demos can prove its tokens stop
        validating once it leaves the JWKS.
        """
        retired = self.current
        self.current = self.next
        self.next = self._new_key()
        return retired
