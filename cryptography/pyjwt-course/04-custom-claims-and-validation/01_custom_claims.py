"""01 · Custom (private) claims.

Beyond the seven registered claims, you can put any JSON-serialisable data in
the payload. These are **private claims** — meaningful only to your application.
Common examples: `roles`, `email`, `tenant`, `permissions`.

To avoid collisions with future registered claims (or other systems), real
deployments often namespace custom keys (see script 07). Here we keep them
simple to focus on the read/write round-trip.

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/01_custom_claims.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    # Custom claims sit right alongside any registered ones.
    payload = {
        "sub": "user-123",
        "email": "ada@example.com",
        "tenant": "acme-corp",
        "roles": ["editor", "billing"],
    }

    token = jwt.encode(payload, SECRET, algorithm="HS256")
    print("Encoded a token carrying custom claims.\n")

    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])

    # Read custom claims back out — they are just dict keys.
    print("email :", decoded["email"])
    print("tenant:", decoded["tenant"])
    print("roles :", decoded["roles"])

    # Use .get() for optional claims so a missing key won't crash.
    print("plan  :", decoded.get("plan", "<not present>"))


if __name__ == "__main__":
    main()
