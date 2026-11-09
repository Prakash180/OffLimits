"""
08 · A tiny login simulation
============================

Time to tie module 02 together with a realistic mini-flow:

  LOGIN:   user authenticates -> server issues a signed JWT ("access token").
  REQUEST: user later presents the token -> server verifies it and greets them.

No web framework, no network — just the JWT mechanics you've learned, wrapped
in functions that mimic a login endpoint and a protected endpoint.
"""

import datetime

import jwt
from jwt.exceptions import InvalidTokenError

# The server's signing secret. In production: load from env/secret manager.
SERVER_SECRET = "server-only-hmac-secret-keep-safe"
ALGORITHM = "HS256"

# A pretend user database (username -> password). Never store plaintext
# passwords in real life — hash them. This is illustrative only.
USERS = {"alice": "wonderland", "bob": "builder"}


def login(username: str, password: str) -> str:
    """Authenticate a user and return a signed access token."""
    if USERS.get(username) != password:
        raise ValueError("invalid username or password")
    now = datetime.datetime.now(tz=datetime.UTC)
    payload = {
        "sub": username,                       # subject: who the token is about
        "iat": now,                            # issued-at
        "exp": now + datetime.timedelta(minutes=15),  # short-lived token
    }
    return jwt.encode(payload, SERVER_SECRET, algorithm=ALGORITHM)


def protected_greeting(token: str) -> str:
    """Verify a presented token and return a personalized greeting."""
    # Verifies signature AND expiry; pins the algorithm.
    claims = jwt.decode(token, SERVER_SECRET, algorithms=[ALGORITHM])
    return f"Hello, {claims['sub']}! Your token is valid. 👋"


print("=" * 60)
print("STEP 1 — alice logs in")
print("=" * 60)
access_token = login("alice", "wonderland")
print(f"Issued access token:\n{access_token}\n")

print("=" * 60)
print("STEP 2 — alice calls a protected endpoint with her token")
print("=" * 60)
print(protected_greeting(access_token))
print()

print("=" * 60)
print("STEP 3 — a bad login is rejected")
print("=" * 60)
try:
    login("alice", "wrong-password")
except ValueError as exc:
    print(f"Login refused: {exc}")
print()

print("=" * 60)
print("STEP 4 — a tampered/garbage token is rejected at the endpoint")
print("=" * 60)
try:
    protected_greeting(access_token + "tampered")
except InvalidTokenError as exc:
    print(f"Endpoint refused token: {type(exc).__name__}: {exc}")
print()

print("That's the essence of token-based auth: issue on login, verify on every")
print("request. Modules ahead add claim validation, asymmetric keys, and more.")
