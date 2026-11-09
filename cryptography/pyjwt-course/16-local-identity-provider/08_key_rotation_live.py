"""
08 · Live key rotation — why providers publish more than one key
================================================================

Providers periodically retire their signing key and start signing with a new
one. If they swapped instantly, every token signed by the old key would break
the moment clients refreshed the JWKS. The fix: publish a SET of keys (current +
next) and route by ``kid``. A token verifies as long as its ``kid`` is still in
the JWKS — regardless of which published key signed it.

This script:

    1. publishes two keys and signs a token with EACH — both validate;
    2. rotates (current -> retired, next -> current, new next minted);
    3. shows the token from the still-published key keeps validating;
    4. shows the token from the RETIRED key now fails (its kid left the JWKS).

It mutates the IdP's live ``KeyManager`` (``idp.server.keys``) directly.

Run:
    uv run python pyjwt-course/16-local-identity-provider/08_key_rotation_live.py
"""

from datetime import UTC, datetime, timedelta

import jwt
from idp.server import AUDIENCE, ISSUER, keys


def sign_access_token(signer, sub: str = "user-alice-0001") -> str:
    """Sign a minimal RS256 access token with a SPECIFIC signing key."""
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": sub,
            "scope": "api.read",
            "iat": now,
            "exp": now + timedelta(minutes=15),
        },
        signer.private_key,
        algorithm="RS256",
        headers={"kid": signer.kid},
    )


def validate(token: str, jwks: dict) -> dict:
    """Validate a token by selecting its key from the CURRENT JWKS via kid."""
    kid = jwt.get_unverified_header(token)["kid"]
    keyset = jwt.PyJWKSet.from_dict(jwks)
    for key in keyset.keys:
        if key.key_id == kid:
            return jwt.decode(
                token, key.key, algorithms=["RS256"],
                audience=AUDIENCE, issuer=ISSUER,
            )
    raise jwt.PyJWKClientError(f"no published key for kid={kid!r}")


def main() -> None:
    print("=" * 72)
    print("BEFORE ROTATION · two keys published")
    print("=" * 72)
    print(f"published kids: {[k['kid'] for k in keys.jwks()['keys']]}")

    current_key = keys.current
    next_key = keys.next
    token_from_current = sign_access_token(current_key)
    token_from_next = sign_access_token(next_key)

    jwks_before = keys.jwks()
    validate(token_from_current, jwks_before)
    validate(token_from_next, jwks_before)
    print(f"token signed by current ({current_key.kid}) -> VALID ✔")
    print(f"token signed by next    ({next_key.kid}) -> VALID ✔")
    print("Both published keys validate — that's why a set is published.")

    print("\n" + "=" * 72)
    print("ROTATE · current retires, next becomes current, a new next is minted")
    print("=" * 72)
    retired = keys.rotate()
    jwks_after = keys.jwks()
    print(f"retired kid   : {retired.kid}")
    print(f"published kids: {[k['kid'] for k in jwks_after['keys']]}")

    print("\n" + "=" * 72)
    print("AFTER ROTATION · who still validates?")
    print("=" * 72)
    # token_from_next was signed by the key that is now `current` -> still published.
    validate(token_from_next, jwks_after)
    print(f"token signed by {next_key.kid} (now current) -> STILL VALID ✔")

    # token_from_current was signed by the now-retired key -> kid gone from JWKS.
    try:
        validate(token_from_current, jwks_after)
        print("UNEXPECTED: retired-key token still accepted!")
        raise SystemExit(1)
    except jwt.PyJWKClientError as exc:
        print(f"token signed by {retired.kid} (retired) -> REJECTED: {exc}")

    print("\nOK ✔  rotation kept valid tokens working and aged the old key out.")


if __name__ == "__main__":
    main()
