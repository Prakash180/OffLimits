## 🧠 Mental Model — Behind the Scenes

When Google, Microsoft, or any OIDC provider signs a token with a **private** key, the whole world needs a way to find the matching **public** key to verify it — without phoning the provider's support desk. The answer is delightfully boring: the provider publishes its public keys as **plain JSON on an HTTPS URL**. That document is a **JWKS** (JSON Web Key Set), and each entry inside it is a **JWK** (JSON Web Key). A JWK is just a public key turned inside-out into JSON fields: `kty` (key type), `n` and `e` (the RSA modulus and exponent, base64url-encoded), plus metadata like `kid` (key ID), `use`, and `alg`. There is no secret in it — that's the entire point.

The magic glue is the **`kid`**. When a token is signed, the provider stamps the signing key's `kid` into the token's *header*. So verification becomes a lookup: read the unverified header, pull out the `kid`, find the JWK in the set whose `kid` matches, turn that JWK back into a usable key, and only *then* run `jwt.decode`. PyJWT exposes this as `PyJWKSet.from_dict(jwks)` to load the set and `jwks_set[kid].key` to grab the verification key. Under the hood `RSAAlgorithm.to_jwk()` serializes a key into JWK JSON and `RSAAlgorithm.from_jwk()` reverses it.

`PyJWKClient` is *not* a new algorithm or protocol — it is a thin convenience wrapper that adds exactly two things to the flow above: **fetch the JWKS over HTTPS** and **cache it** so you aren't hammering the `jwks_uri` on every request. `get_signing_key_from_jwt(token)` internally does `get_unverified_header → kid → lookup → return PyJWK`. That's it. Module 11 proves this by reimplementing the method by hand against a local in-memory set.

Because a *set* can hold many keys at once, **key rotation** becomes downtime-free: publish the old and new keys together, switch signing to the new key, and only retire the old key once every token it signed has expired. The overlap window is what keeps verification from ever breaking.

### 🔍 A concrete analogy

A JWKS is like a company's public lobby directory of notary stamps. Every notarized document carries a stamp number (`kid`). To check a document is genuine you don't call the notary — you look up that stamp number in the public directory, compare the impression, and you're done. When the firm hires a new notary, they simply add the new stamp to the directory while leaving the retiring notary's stamp posted until their last documents expire.

### ⚙️ What actually happens when you run the code

1. A provider generates one or more RSA key pairs, each assigned a unique `kid`.
2. Each **public** key is serialized to JWK JSON via `RSAAlgorithm.to_jwk()`, then bundled into `{"keys": [...]}` — the JWKS.
3. A token is signed with a **private** key, and that key's `kid` is written into the token header (`headers={"kid": "key-a"}`).
4. The verifier calls `jwt.get_unverified_header(token)` to read the `kid` *without* trusting anything yet.
5. `PyJWKSet.from_dict(jwks)` parses the set; `jwks_set[kid]` returns the matching `PyJWK`, and `.key` yields a ready cryptographic key object.
6. `jwt.decode(token, signing_key.key, algorithms=["RS256"])` performs the real signature check against that public key.
7. `PyJWKClient` wraps steps 4–5 with an HTTPS fetch plus an in-memory cache.

### 👀 What to notice when you run the examples

- In `01_what_is_a_jwk.py`, the JWK is *human-readable JSON* with no private material — you can paste it anywhere safely.
- In `04_pyjwkset_from_dict.py`, indexing the set by string `kid` (`jwks_set["key-a"]`) returns a `PyJWK` object; `.key` is what `jwt.decode` actually wants.
- `06_key_rotation_flow.py` shows the overlap phase where **both** an A-signed and a B-signed token verify simultaneously — and the moment A is dropped, lingering A-tokens finally fail.
- `07_pyjwkclient_explained.py` reimplements `get_signing_key_from_jwt` in three lines, revealing the "client" as pure convenience around a flow you already know.

### ⚠️ Common misconceptions

- **"A JWKS contains secrets."** No — it contains only *public* keys. Publishing it is intentional and safe.
- **"PyJWKClient does something cryptographically special."** It only fetches and caches JSON; the verification logic is identical to manual `kid` lookup.
- **"Rotation means swapping one key for another instantly."** Real rotation *overlaps* keys so in-flight tokens keep verifying until they expire.
- **"You can skip `algorithms=[...]` because the right key was selected."** Never — always pin the expected algorithm even after resolving the key by `kid`.
