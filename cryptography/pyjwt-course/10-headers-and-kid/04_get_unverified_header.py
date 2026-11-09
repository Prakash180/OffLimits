"""04 · ``get_unverified_header`` — reading the header BEFORE you verify.

This is one of the most important — and most misunderstood — functions in PyJWT.

To verify a token you need the right key. But for asymmetric tokens (and any
multi-key setup) you don't know *which* key until you read the ``kid`` from the
header... which lives *inside the token you haven't verified yet*. Chicken, meet
egg.

The resolution: ``jwt.get_unverified_header(token)`` decodes the header segment
**without checking the signature**. You use it ONLY to discover ``alg`` and
``kid`` so you can choose the verification key — and then you do a *full*,
signature-checked ``jwt.decode`` with that key.

⚠️  UNVERIFIED means UNTRUSTED. An attacker fully controls these values. Never
make a security decision based on unverified header/claims beyond "which key
should I try". Always whitelist algorithms in ``decode(algorithms=[...])`` — do
NOT feed the header's ``alg`` straight back in, or you enable algorithm-confusion
attacks (module 14).

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/10-headers-and-kid/04_get_unverified_header.py
"""

import json

import jwt

KEYSTORE = {
    "key-1": "secret-one-padded-to-at-least-32-bytes-long!",
    "key-2": "secret-two-padded-to-at-least-32-bytes-long!",
}
ALLOWED_ALGS = ["HS256"]  # our trusted whitelist — fixed, never taken from the token


def main() -> None:
    token = jwt.encode(
        {"user": "carol"}, KEYSTORE["key-2"], algorithm="HS256", headers={"kid": "key-2"}
    )

    # STEP 1: peek at the header — no key, no signature check.
    header = jwt.get_unverified_header(token)
    print("Unverified header (do NOT trust yet):")
    print(json.dumps(header, indent=2))
    print()

    alg = header["alg"]
    kid = header["kid"]
    print(f"Header advertises alg={alg!r}, kid={kid!r}")

    # STEP 2: use kid to select the key. Use our OWN whitelist for algorithms,
    # not the header's alg value.
    if alg not in ALLOWED_ALGS:
        raise ValueError(f"Refusing untrusted algorithm {alg!r}")
    key = KEYSTORE[kid]

    # STEP 3: NOW verify for real — this is the trusted result.
    verified = jwt.decode(token, key, algorithms=ALLOWED_ALGS)
    print(f"✅ Verified claims (trusted): {verified}")
    print()
    print("Remember: get_unverified_header is for KEY SELECTION only — never trust it.")


if __name__ == "__main__":
    main()
