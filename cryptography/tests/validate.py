import os

import dotenv
import jwt
from jwt import PyJWKClient

dotenv.load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

JWKS_URL = (
    f"https://login.microsoftonline.com/{TENANT_ID}"
    "/discovery/v2.0/keys"
)

ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"

def validate_token(access_token: str):

    jwk_client = PyJWKClient(JWKS_URL)

    signing_key = jwk_client.get_signing_key_from_jwt(
        access_token
    )

    decoded = jwt.decode(
        access_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=CLIENT_ID,
        issuer=ISSUER,
    )

    return decoded

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate a JWT access token."
    )
    parser.add_argument("token", help="The JWT access token to validate.")
    args = parser.parse_args()
    claims = validate_token(args.token)
    print(claims)

if __name__ == "__main__":
    main()