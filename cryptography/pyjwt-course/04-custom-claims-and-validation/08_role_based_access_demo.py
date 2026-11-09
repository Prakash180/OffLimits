"""08 · Role-Based Access Control (RBAC) demo with JWT claims.

This ties the module together: tokens carry a `roles` custom claim, and a tiny
``authorize()`` helper enforces that a caller holds a required role before an
action runs.

The flow mirrors a real API gateway:
    1. Verify the token's signature (and any registered claims).
    2. Read the `roles` claim from the trusted payload.
    3. Allow or deny based on the required role for the operation.

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/08_role_based_access_demo.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "super-secret-shared-key-please-change-me"
ISSUER = "https://auth.example.com"
AUDIENCE = "https://api.example.com"


def issue_token(user_id: str, roles: list[str]) -> str:
    """Mint a signed token for a user carrying their roles."""
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "roles": roles,
        },
        SECRET,
        algorithm="HS256",
    )


class AccessDenied(Exception):
    """Raised when a verified token lacks the required role."""


def authorize(token: str, required_role: str) -> dict:
    """Verify a token and ensure it grants `required_role`.

    Returns the decoded payload on success; raises on failure.
    """
    # Step 1: fully verify the token (signature + iss/aud + exp).
    payload = jwt.decode(
        token,
        SECRET,
        algorithms=["HS256"],
        issuer=ISSUER,
        audience=AUDIENCE,
    )
    # Step 2: read roles from the *trusted* payload.
    roles = payload.get("roles", [])
    # Step 3: enforce the requirement.
    if required_role not in roles:
        raise AccessDenied(
            f"user {payload['sub']} has roles {roles}; '{required_role}' required"
        )
    return payload


def attempt(token: str, required_role: str, label: str) -> None:
    """Try an authorized action and print the outcome."""
    try:
        payload = authorize(token, required_role)
        print(f"[ALLOW] {label}: {payload['sub']} has '{required_role}'.")
    except AccessDenied as exc:
        print(f"[DENY]  {label}: {exc}")
    except jwt.InvalidTokenError as exc:
        print(f"[DENY]  {label}: invalid token ({exc}).")


def main() -> None:
    admin_token = issue_token("alice", ["admin", "editor"])
    editor_token = issue_token("bob", ["editor"])

    print("Required role for deleting a record: 'admin'\n")
    attempt(admin_token, "admin", "alice deletes record")   # allowed
    attempt(editor_token, "admin", "bob deletes record")    # denied

    print("\nRequired role for editing a record: 'editor'\n")
    attempt(admin_token, "editor", "alice edits record")    # allowed (has editor)
    attempt(editor_token, "editor", "bob edits record")     # allowed


if __name__ == "__main__":
    main()
