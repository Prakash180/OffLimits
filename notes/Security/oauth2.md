# OAuth 2.0 & Authentication

## Auth — The Basics

- **Authentication (AuthN)** — *Who are you?* Verifying identity (e.g., login with username + password).
- **Authorization (AuthZ)** — *What can you do?* Deciding what an authenticated user is allowed to access.

---

## What is OAuth 2.0?

OAuth 2.0 is an **authorization framework** — it lets one app access resources on another app *on behalf of a user*, without sharing the user's password.

**Real-world example:**
> "Sign in with Google" on a third-party app. You give Google your credentials, and Google tells the app "yes, this person is allowed in" — the app never sees your Google password.

---

## SSO vs OAuth 2.0

- **SSO (Single Sign-On)** = the *experience* — log in once, access many apps
- **OAuth 2.0 / OIDC** = the *protocol* — the mechanism used to achieve SSO

| | SSO | OAuth 2.0 |
|---|---|---|
| **What it is** | A user experience pattern | An authorization protocol |
| **Goal** | One login for many apps | Delegate access securely |
| **Needs a protocol?** | Yes — usually OIDC or SAML | It *is* the protocol |
| **Handles identity?** | Yes | Only with OIDC on top |

> **Simple mental model:** SSO is like a theme park season pass — buy once, enter all rides. OAuth 2.0/OIDC is the turnstile system that checks the pass at each ride.

---

## Core Components

| Role | Who it is |
|---|---|
| **Resource Owner** | The user |
| **Client** | The app that wants access (e.g., Spotify) |
| **Authorization Server (AS)** | Issues tokens (e.g., Google's login server) |
| **Resource Server (RS)** | Holds the data the client wants (e.g., Google Drive) |

---

## Grant Types (Flows)

### 1. Authorization Code Flow *(most common, most secure)*
**Used for:** Web apps with a backend server

```
User clicks "Login with Google"
  → Browser redirects to AS with:
      client_id, redirect_uri, scope, state, response_type=code
  → User logs in & approves
  → AS redirects back with: ?code=ABC123
  → Your backend exchanges code for tokens:
      POST /token { code, client_id, client_secret, redirect_uri }
  → AS returns: access_token + refresh_token
  → Use access_token to call Resource Server
```

**Why two steps (code → token)?**
The code is visible in the browser URL, but the token exchange happens server-to-server — never exposed to the browser.

---

### 2. Authorization Code + PKCE *(mobile/SPA apps)*
**Used for:** Apps that can't store a `client_secret` safely (mobile apps, single-page apps)

PKCE = *Proof Key for Code Exchange*

```
App generates:
  code_verifier  = random string
  code_challenge = SHA256(code_verifier)

Sends code_challenge in auth request →
Gets back the code →
Sends code_verifier during token exchange →
AS verifies: SHA256(code_verifier) == code_challenge ✓
```

This replaces `client_secret` for public clients.

---

### 3. Client Credentials Flow *(machine-to-machine)*
**Used for:** Backend service talking to another service, no user involved

```
Service A → POST /token { client_id, client_secret, grant_type=client_credentials }
          ← access_token
Service A → calls Service B's API with access_token
```

Common in microservices.

---

### 4. Device Code Flow *(smart TVs, CLIs)*
**Used for:** Devices with no browser

```
Device → POST /device_authorization → gets device_code + user_code
Device → shows user: "Go to example.com/activate, enter: ABCD-1234"
Device → polls AS every few seconds
User logs in on phone/laptop and approves
Device → gets access_token
```

---

### ~~Implicit Flow~~ *(deprecated — don't use)*
Returned tokens directly in the URL. Replaced by PKCE.

---

## Token Types

| Token | Lifespan | Purpose |
|---|---|---|
| **Access Token** | Short (mins–hours) | Call APIs |
| **Refresh Token** | Long (days–weeks) | Get new access tokens |
| **ID Token** (OIDC only) | Short | Know *who* the user is |

**Access Token formats:**
- **Opaque** — random string; AS must be called to validate it
- **JWT** — self-contained; Resource Server validates it locally using AS's public key

---

## JWT (JSON Web Token)

A JWT looks like: `header.payload.signature`

```
eyJhbGciOiJSUzI1NiJ9       ← header (algorithm used)
.eyJzdWIiOiJ1c2VyMTIzIn0   ← payload (claims: user id, expiry, scopes)
.SflKxwRJSMeKKF2...         ← signature (AS signs with private key)
```

The Resource Server verifies the signature using the AS's **public key** — no need to call the AS on every request. Fast and scalable.

---

## Scopes

Scopes define *what* the client is asking permission for.

```
scope=read:emails write:calendar
```

The user sees: *"This app wants to read your emails and write to your calendar. Allow?"*

Always request minimum needed — **principle of least privilege**.

---

## Full Flow Diagram

```
         Client App
             │
    1. Redirect to AS with client_id + scope
             │
     Authorization Server
             │
    2. User logs in + approves
             │
    3. Redirect back with auth code
             │
         Client App
             │
    4. Exchange code + client_secret → tokens
             │
     Authorization Server
             │
    5. Returns access_token (+ refresh_token)
             │
         Client App
             │
    6. Call Resource Server with access_token
             │
      Resource Server
             │
    7. Validate token → return data
```

---

## Implementation Options

### Option A: Use an existing Identity Provider (IdP)
Don't build from scratch. Use:
- **Okta**, **Auth0**, **Azure AD**, **AWS Cognito**, **Google Identity**
- They handle the Authorization Server. You just integrate their SDK.

### Option B: Build your own Authorization Server
Use a library:
- **Java/Spring:** Spring Authorization Server
- **Node.js:** `node-oidc-provider`
- **Python:** `authlib`

Endpoints you'd implement:
- `/authorize` — starts the flow
- `/token` — exchanges code for tokens
- `/userinfo` — returns user details (OIDC)
- `/.well-known/openid-configuration` — discovery endpoint (tells clients where everything is)

---

## Security Checklist

| Threat | Defense |
|---|---|
| Code interception | Use PKCE |
| CSRF on redirect | Use `state` parameter (random nonce) |
| Token theft | Short-lived access tokens + HTTPS only |
| Scope creep | Request minimal scopes |
| Token replay | Use `jti` (JWT ID) claim + check expiry |

---

## OAuth 2.0 vs OIDC

- **OAuth 2.0** = Authorization only ("can this app access my files?")
- **OIDC (OpenID Connect)** = OAuth 2.0 + Authentication ("who is this user?") — adds the ID Token

---

## Managed Identity

Managed Identity is a cloud-platform concept (Azure, AWS, GCP) that solves the **secrets management problem** in the Client Credentials flow.

### The Problem
In Client Credentials, your service needs a `client_secret` to get a token — but storing and rotating secrets is risky.

### What Managed Identity Does
The cloud platform **automatically assigns an identity** to your app and handles the secret entirely — you never store, see, or rotate it.

```
Normal Client Credentials:
  App → client_id + client_secret → AS → token

Managed Identity:
  App (running on Azure) → "I am App X on VM Y" → Azure AS → token
  (Azure verifies using infrastructure-level trust — no secret needed)
```

### Two Types (Azure)

| Type | What it is |
|---|---|
| **System-assigned** | Identity tied to one specific resource. Deleted with the resource. |
| **User-assigned** | Standalone identity, can be shared across multiple resources. |

### Comparison

| | Client Credentials (with secret) | Managed Identity |
|---|---|---|
| **Secret in code?** | Yes (`client_secret`) | Never |
| **Rotation needed?** | Yes, manually | Automatic |
| **Works where?** | Anywhere | Only on cloud-hosted resources |

> **Simple analogy:** A regular app shows a badge (client_secret) to get in. A managed identity app works in a building where the security system already knows every employee by face — the building itself vouches for them.

### In `panel-aggregationengine`
The project does **NOT** use Managed Identity. It uses `ClientSecretCredentialBuilder` with `${AZURE_CLIENT_SECRET}` injected via environment variables — the classic Client Credentials approach with an explicit secret.
