"""08 · The `jti` (JWT ID) registered claim.

`jti` is a unique identifier for the token. Its purpose is to give each token
an identity you can track — most importantly to **prevent replay** by keeping a
denylist (or, for one-time tokens, an allowlist that is consumed on first use).

PyJWT does NOT track `jti` for you; uniqueness/replay logic lives in your app.
Below we simulate an in-memory denylist of already-used token IDs.

Run me:
    .venv/bin/python pyjwt-course/03-registered-claims/08_jti_jwt_id.py
"""

import uuid

import jwt

SECRET = "super-secret-shared-key-please-change-me"

# A real system would use Redis / a database with TTLs. An in-memory set is
# enough to demonstrate the idea.
USED_TOKEN_IDS: set[str] = set()


def consume(token: str) -> None:
    """Decode a token and reject it if its `jti` has already been seen."""
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    jti = payload["jti"]
    if jti in USED_TOKEN_IDS:
        print(f"    [DENIED] jti={jti} was already used -> possible replay!")
        return
    USED_TOKEN_IDS.add(jti)
    print(f"    [ACCEPTED] jti={jti} consumed for the first time.")


def main() -> None:
    # Each token gets a fresh, collision-resistant id from uuid4().
    token = jwt.encode(
        {"sub": "user-123", "jti": str(uuid.uuid4())},
        SECRET,
        algorithm="HS256",
    )
    print("Issued a token with a unique `jti`.\n")

    print("First presentation of the token:")
    consume(token)

    print("\nSecond presentation of the SAME token (replay attempt):")
    consume(token)

    print("\nA brand-new token has a different `jti`, so it is accepted:")
    consume(jwt.encode({"sub": "user-123", "jti": str(uuid.uuid4())}, SECRET, algorithm="HS256"))


if __name__ == "__main__":
    main()
