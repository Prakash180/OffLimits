"""
01 · Your first encode
======================

The most basic JWT operation: turn a dictionary of claims into a signed token
string using a shared secret and the HS256 algorithm.

  jwt.encode(payload, key, algorithm="HS256")

  * payload   — a dict of claims (your data).
  * key       — the shared secret only your server knows.
  * algorithm — how to sign. "HS256" = HMAC with SHA-256 (symmetric).

In PyJWT 2.x, encode() returns a `str` you can send to a client.
"""

import jwt

# In real life this comes from config/secrets, never hard-coded like this.
SECRET = "change-me-to-a-real-secret-min-32-bytes!"

print("=" * 60)
print("ENCODING A TOKEN")
print("=" * 60)
payload = {"user": "alice"}
print(f"payload   : {payload}")
print("algorithm : HS256 (HMAC-SHA256)")
print()

token = jwt.encode(payload, SECRET, algorithm="HS256")
print(f"token     : {token}")
print(f"token type: {type(token).__name__}  (a str in PyJWT 2.x)")
print()

print("That's it — you've issued your first JWT. The next script reads it back.")
