import os

import dotenv
import msal

dotenv.load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET,
)

auth_url = app.get_authorization_request_url(
    scopes=["https://graph.microsoft.com/User.Read"],
    redirect_uri="http://localhost:8443/codereceiver"
)

print(auth_url)