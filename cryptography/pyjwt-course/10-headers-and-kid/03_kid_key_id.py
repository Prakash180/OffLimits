"""03 · ``kid`` — the Key ID header.

A single service often has **multiple** signing keys at once: an old one being
phased out, a current one, maybe a future one. The ``kid`` header is how a token
announces *which* key was used, so the verifier can pick the matching key from
its keystore instead of guessing (or trying them all).

Here we keep an in-memory keystore mapping ``kid -> secret``. The issuer stamps
each token with the ``kid`` of the secret it used. The verifier reads that
``kid`` and looks up the correct secret. Use the wrong secret and verification
fails — so getting the lookup right matters.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/10-headers-and-kid/03_kid_key_id.py
"""

import jwt

# A keystore: each key has a name (kid) and a secret value.
KEYSTORE = {
    "key-1": "secret-for-key-one-padded-to-32-plus-bytes!",
    "key-2": "secret-for-key-two-padded-to-32-plus-bytes!",
}


def issue(payload: dict, kid: str) -> str:
    """Sign a token using the secret named by ``kid`` and stamp ``kid`` in the header."""
    secret = KEYSTORE[kid]
    return jwt.encode(payload, secret, algorithm="HS256", headers={"kid": kid})


def verify(token: str) -> dict:
    """Read the kid from the (unverified) header, pick the right secret, then verify."""
    kid = jwt.get_unverified_header(token)["kid"]
    secret = KEYSTORE[kid]  # the right key for THIS token
    return jwt.decode(token, secret, algorithms=["HS256"])


def main() -> None:
    # Issue two tokens signed with two different keys.
    token_a = issue({"user": "alice"}, kid="key-1")
    token_b = issue({"user": "bob"}, kid="key-2")

    for label, token in (("token_a (key-1)", token_a), ("token_b (key-2)", token_b)):
        claims = verify(token)
        chosen_kid = jwt.get_unverified_header(token)["kid"]
        print(f"{label}: kid={chosen_kid} -> verified claims {claims}")

    print()

    # Show what happens if the kid points at the WRONG secret: verification fails.
    print("Tampering demo — verify token_a with key-2's secret:")
    try:
        jwt.decode(token_a, KEYSTORE["key-2"], algorithms=["HS256"])
    except jwt.InvalidSignatureError:
        print("  ❌ InvalidSignatureError (as expected — wrong key for this token)")

    print()
    print("✅ kid lets a verifier select the correct key per token.")


if __name__ == "__main__":
    main()
