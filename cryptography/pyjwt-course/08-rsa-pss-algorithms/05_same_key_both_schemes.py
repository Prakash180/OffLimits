"""
08 · RSA-PSS · 05 — One RSA key, both schemes; algorithms aren't interchangeable
================================================================================

We established that a single RSA keypair can sign with both RS256 and PS256.
But the **verifier must whitelist the correct algorithm**. A token signed with
PS256 will NOT verify if you tell PyJWT to expect only RS256 — even though the
exact same key pair is involved — because the padding differs.

This protects you: the `algorithms=[...]` allow-list on `jwt.decode()` is a
security control. Never set it to a permissive catch-all.

This script proves:
    1. RS256 token verifies as RS256.            ✔
    2. PS256 token verifies as PS256.            ✔
    3. PS256 token FAILS to verify as RS256.     ✘ (caught & explained)
"""

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def main() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    payload = {"sub": "erin"}

    rs_token = jwt.encode(payload, private_pem, algorithm="RS256")
    ps_token = jwt.encode(payload, private_pem, algorithm="PS256")

    print("1) RS256 token verified as RS256:")
    print("   ", jwt.decode(rs_token, public_pem, algorithms=["RS256"]))

    print("\n2) PS256 token verified as PS256:")
    print("   ", jwt.decode(ps_token, public_pem, algorithms=["PS256"]))

    print("\n3) PS256 token verified as RS256 (EXPECTED TO FAIL):")
    try:
        jwt.decode(ps_token, public_pem, algorithms=["RS256"])
        print("   !! Unexpected success.")
    except jwt.InvalidAlgorithmError as exc:
        print("   Caught InvalidAlgorithmError:", exc)
        print("   The token's alg (PS256) is not in the allow-list ['RS256'].")
    except jwt.InvalidSignatureError as exc:
        print("   Caught InvalidSignatureError:", exc)

    print("\nThe decode-time algorithms allow-list is a real security boundary.")


if __name__ == "__main__":
    main()
