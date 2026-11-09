"""08_rsa_vs_hmac_when_to_use.py — Choosing between HMAC and RSA.

Both HMAC (HS*) and RSA (RS*) produce signed, tamper-evident JWTs. The
difference is the TRUST MODEL, and that is what should drive your choice.

  HMAC (symmetric):
    - ONE shared secret signs and verifies.
    - Whoever can verify can also forge.
    - Great when the SAME party / mutually trusting services issue & check.
    - Simple: no key pairs, no PEM.

  RSA (asymmetric):
    - PRIVATE key signs; PUBLIC key verifies.
    - You can publish the public key to untrusted third parties.
    - They can verify but NEVER forge.
    - This is why OAuth2 / OIDC providers (Google, Microsoft Entra ID, Auth0)
      sign with RSA/ECDSA and publish public keys via JWKS endpoints.

This script demonstrates both side by side.
"""

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.exceptions import InvalidSignatureError

payload = {"sub": "user-123", "scope": "read"}

print("=" * 60)
print("HMAC (HS256): one shared secret — same-party trust")
print("=" * 60)
shared_secret = "one-secret-shared-between-trusted-services"
hs_token = jwt.encode(payload, shared_secret, algorithm="HS256")
print("Issuer signs with the secret.")
print("Verifier (same secret) ->", jwt.decode(hs_token, shared_secret, algorithms=["HS256"]))
# Anyone with the secret could ALSO mint tokens — that is the catch:
forged = jwt.encode({"sub": "attacker", "scope": "admin"}, shared_secret, algorithm="HS256")
print("Anyone holding the secret can also FORGE:", jwt.decode(forged, shared_secret, algorithms=["HS256"]))
print("=> Only safe to share the secret with fully trusted parties.\n")

print("=" * 60)
print("RSA (RS256): private signs, public verifies — third-party trust")
print("=" * 60)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
rs_token = jwt.encode(payload, private_key, algorithm="RS256")
print("Provider signs with its PRIVATE key (kept secret).")
print("Third party (PUBLIC key) ->", jwt.decode(rs_token, public_key, algorithms=["RS256"]))
# A third party holding only the public key CANNOT forge:
try:
    jwt.encode({"sub": "attacker"}, public_key, algorithm="RS256")
except Exception as exc:
    print("Third party tries to forge with the public key:", type(exc).__name__, "-> cannot sign")
# And a wrong public key would reject the token:
other_public = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
try:
    jwt.decode(rs_token, other_public, algorithms=["RS256"])
except InvalidSignatureError:
    print("Wrong public key -> InvalidSignatureError (forgeries rejected)")
print("=> Publish the public key freely; only you can sign.\n")

print("DECISION GUIDE")
print("  Use HMAC  when one party (or tightly trusted services) issues AND verifies.")
print("  Use RSA   when others must verify but must NOT be able to sign")
print("            (public APIs, OAuth/OIDC providers, microservices across teams).")
