"""02 · options={"verify_signature": False}.

The signature is what makes a JWT *trustworthy*. Disabling its verification
means you are reading **unauthenticated** data — anyone could have forged or
tampered with it.

Legitimate uses are narrow:
  * inspecting a token's claims/header for debugging,
  * reading the `kid`/`iss` to decide *which* key to then verify with.

⚠️ Never make an authorization decision on a token decoded this way.

Note: when you turn off signature verification, PyJWT also turns off the
expiry/claim checks that depend on trusting the token, so you typically pass no
secret at all.

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/02_options_verify_signature.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"


def main() -> None:
    token = jwt.encode({"sub": "user-123", "roles": ["admin"]}, SECRET, algorithm="HS256")

    # --- Read claims WITHOUT verifying the signature ---------------------
    # No key is required; PyJWT just base64url-decodes the payload.
    unsafe = jwt.decode(
        token,
        options={"verify_signature": False},
        algorithms=["HS256"],
    )
    print("[UNVERIFIED] Claims read without checking the signature:")
    print("    ", unsafe)
    print("    ⚠️ Treat this data as untrusted — do NOT authorize on it.")

    # --- Proof that tampering is undetectable in this mode ---------------
    # Splice the (untrusted) header+payload of a token with a bogus signature.
    header_b64, payload_b64, _ = token.split(".")
    forged = f"{header_b64}.{payload_b64}.not-a-real-signature"
    still_reads = jwt.decode(forged, options={"verify_signature": False}, algorithms=["HS256"])
    print("\n[UNVERIFIED] Even a token with a garbage signature decodes:")
    print("    ", still_reads)

    # --- The safe path, for contrast -------------------------------------
    verified = jwt.decode(token, SECRET, algorithms=["HS256"])
    print("\n[VERIFIED] With the secret, the signature is checked:")
    print("    ", verified)


if __name__ == "__main__":
    main()
