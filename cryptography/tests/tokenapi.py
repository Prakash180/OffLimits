import os
import urllib.parse

import dotenv
import requests
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

dotenv.load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

REDIRECT_URI = "http://localhost:8443/codereceiver"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SCOPES = [
    "https://graph.microsoft.com/User.Read"
]


@app.get("/")
def login():

    auth_url = (
        f"{AUTHORITY}/oauth2/v2.0/authorize?"
        f"client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_mode=query"
        f"&scope={urllib.parse.quote(' '.join(SCOPES))}"
    )

    return RedirectResponse(auth_url)


@app.get("/codereceiver")
def code_receiver(code: str):

    token_url = f"{AUTHORITY}/oauth2/v2.0/token"

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
    }

    token_response = requests.post(token_url, data=payload)

    return token_response.json()