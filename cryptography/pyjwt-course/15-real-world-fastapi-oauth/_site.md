## 🧠 Mental Model — Behind the Scenes

Production auth is a relationship between **three roles** that never fully trust each other: the **authorization server** (the IdP) that *mints* tokens, the **client app** that *carries* them, and the **resource server** (your API) that *verifies* them. The tokens flowing between them come in three distinct flavors, and conflating them is the most common architectural mistake. An **access token** is a short-lived key to *call an API* — the resource server checks its signature, `iss`, `aud`, and `exp` on every request. A **refresh token** is a longer-lived, separately-keyed credential whose *only* job is to obtain a fresh access token when the old one expires; an API must never accept it in the access slot. An **id_token** is an OIDC artifact about *who the user is* — it's for the **client**, validated against `aud == client_id` (and a `nonce`), not a license to call APIs.

On the API side, the verification gate is plumbed into the framework as a **dependency**. In FastAPI you write one `Depends(get_current_user)` that extracts the `Authorization: Bearer <token>` header, runs `jwt.decode` with pinned `algorithms`, `audience`, and `issuer`, and either returns the claims or raises `401`. Every protected route reuses that single gate — authentication becomes a one-liner per endpoint. Crucially, **authentication and authorization are two separate gates**: a valid signature proves *who* the caller is (→ `401` if it fails), while a **scope** or role check decides *what they may do* (→ `403` if insufficient). The `scope` claim is OAuth2's permission grammar; a `require_scope("read")` guard enforces it after identity is established.

The deepest pattern in the module is **JWKS-based verification**, which is how the real internet checks tokens it has never seen. The resource server doesn't share a secret with the IdP — instead it fetches the IdP's **public** keys from a published `jwks_uri`, selects the right one by the token's `kid`, and verifies the RS256 signature. PyJWT packages this as `PyJWKClient`: point it at the keys URL, call `get_signing_key_from_jwt(token)`, and pass the result to `jwt.decode(token, signing_key.key, algorithms=["RS256"], audience=..., issuer=...)`. This is **exactly** the Microsoft **Entra ID** pattern — `https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys` for the JWKS and `.../v2.0` for the issuer. Module 15 runs an *offline mirror* of this flow (local keys, local JWKS, real `kid` selection) so it works with no network, keeping the live Azure code in comments. For a fully runnable local issuer that speaks OAuth2/OIDC end-to-end, the course also ships a **local identity provider in module 16**.

### 🔍 A concrete analogy

An access token is a **day-pass wristband** to the theme park rides — checked at every gate, expires at closing. A refresh token is your **season membership card** kept safe at home; you don't wave it at rides, you only show it at the booth to get tomorrow's wristband. An id_token is your **photo ID** that tells the *front desk* who you are, not a ride pass. And JWKS is the park's **public registry of valid wristband patterns** posted at the entrance — every gate consults it (by serial number / `kid`) instead of radioing headquarters.

### ⚙️ What actually happens when you run the code

1. The auth server signs an access token (RS256) with realistic claims — `iss`, `sub`, `aud`, `iat`, `exp`, and `scope` — stamping its `kid` into the header.
2. The client sends it to the API as `Authorization: Bearer <token>`.
3. A FastAPI dependency extracts the token from the header (or raises `401` if missing/malformed).
4. The resource server obtains the IdP's public key — locally by `kid` in the offline demo, or via `PyJWKClient.get_signing_key_from_jwt` in the Entra pattern.
5. `jwt.decode(token, key, algorithms=["RS256"], audience=CLIENT_ID, issuer=ISSUER)` verifies signature + `aud` + `iss` + `exp` in one call.
6. A scope/role check runs *after* identity is confirmed — insufficient scope → `403`, never `401`.
7. When the access token expires, the client presents its refresh token to mint a new one without re-authenticating.

### 👀 What to notice when you run the examples

- `02_verify_access_token.py`: dropping `audience=` or `issuer=` lets a token *from another app* sail through — the checks are not optional.
- `03_access_and_refresh_tokens.py`: an access token offered in the refresh slot (or vice versa) is rejected — they're keyed/typed separately.
- `04_fastapi_dependency.py`: `httpx` isn't installed here, so `TestClient` falls back to calling the dependency directly — still exercising valid/invalid/missing paths and exiting 0.
- `07_entra_id_validation_pattern.py`: the offline run mirrors the *exact* `PyJWKClient` + `jwt.decode` sequence used against live Azure (see the commented `validate_token_azure()`).

### ⚠️ Common misconceptions

- **"Verifying the signature is enough."** You must also pin `audience=` and `issuer=`, or a valid token from a different app/tenant passes.
- **"An id_token can call my API."** It's identity for the *client*; APIs should accept *access* tokens and check `aud`.
- **"`scope` is identity."** Scope is permission (what the app may do); `sub` is identity (who the user is) — keep authN and authZ separate.
- **"Trust the `kid`/`jku` the token supplies."** Always resolve keys against a known JWKS / allowlist, never a URL the token itself dictates.
