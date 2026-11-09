"""
08 · The algorithm family grand tour — one alg from each family
================================================================

PyJWT supports five families of signing algorithms. This script signs the SAME
payload with one representative from each, then prints a comparison table of the
header ``alg`` and the resulting signature length.

| Family   | Example | Key type            | Notes                          |
|----------|---------|---------------------|--------------------------------|
| HMAC     | HS256   | shared secret       | symmetric, fast                |
| RSA      | RS256   | RSA private/public  | PKCS#1 v1.5 padding            |
| ECDSA    | ES256   | EC P-256 keypair    | small signatures               |
| RSA-PSS  | PS256   | RSA private/public  | randomised (PSS) padding       |
| EdDSA    | EdDSA   | Ed25519 keypair     | modern, deterministic          |

Note: ECDSA and RSA-PSS are *randomised*, so their signatures differ run to run
even for identical input — that is expected and secure.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/08_algorithm_family_tour.py
"""

import base64
import json

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa


def pem_pair(private_key) -> tuple[str, str]:
    """Serialise any asymmetric private key to (private_pem, public_pem)."""
    priv = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    pub = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )
    return priv, pub


def sig_len(token: str) -> int:
    """Decode the base64url signature segment and return its raw byte length."""
    sig_seg = token.split(".")[2]
    padding = "=" * (-len(sig_seg) % 4)
    return len(base64.urlsafe_b64decode(sig_seg + padding))


def main() -> None:
    payload = {"sub": "grand-tour", "iss": "pyjwt-course"}

    # Build a (sign_key, verify_key) for one alg in each family.
    rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_priv, rsa_pub = pem_pair(rsa_key)

    ec_key = ec.generate_private_key(ec.SECP256R1())  # P-256 -> ES256
    ec_priv, ec_pub = pem_pair(ec_key)

    ed_key = ed25519.Ed25519PrivateKey.generate()  # -> EdDSA
    ed_priv, ed_pub = pem_pair(ed_key)

    families = [
        ("HMAC", "HS256", "shared-secret-key-at-least-32-bytes-long!", "shared-secret-key-at-least-32-bytes-long!"),
        ("RSA", "RS256", rsa_priv, rsa_pub),
        ("ECDSA", "ES256", ec_priv, ec_pub),
        ("RSA-PSS", "PS256", rsa_priv, rsa_pub),
        ("EdDSA", "EdDSA", ed_priv, ed_pub),
    ]

    print("=" * 78)
    print("SIGNING THE SAME PAYLOAD WITH ONE ALGORITHM PER FAMILY")
    print("=" * 78)
    print(f"payload: {payload}\n")

    header = f"{'Family':<10}{'alg':<8}{'header.alg':<12}{'sig bytes':<11}{'verify?'}"
    print(header)
    print("-" * 78)

    for family, alg, sign_key, verify_key in families:
        token = jwt.encode(payload, sign_key, algorithm=alg)

        # Read the alg straight out of the (unverified) JOSE header.
        header_seg = token.split(".")[0]
        header_seg += "=" * (-len(header_seg) % 4)
        hdr = json.loads(base64.urlsafe_b64decode(header_seg))
        header_alg = hdr["alg"]

        # Verify it round-trips with the matching key.
        try:
            jwt.decode(token, verify_key, algorithms=[alg])
            verified = "yes"
        except Exception as ex:  # noqa: BLE001
            verified = f"no ({type(ex).__name__})"

        print(f"{family:<10}{alg:<8}{header_alg:<12}{sig_len(token):<11}{verified}")

    print("\n" + "=" * 78)
    print("TAKEAWAYS")
    print("=" * 78)
    print("- The header 'alg' always names the algorithm used to sign.")
    print("- HMAC/RSA/PSS digests vary in size; EC & EdDSA are compact.")
    print("- ES256 & PS256 are randomised: re-running yields a different sig.")
    print("- Choose: HS* (internal), RS*/PS* (RSA infra), ES*/EdDSA (small+fast).")


if __name__ == "__main__":
    main()
