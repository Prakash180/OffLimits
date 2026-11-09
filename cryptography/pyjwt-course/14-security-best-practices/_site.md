## 🧠 Mental Model — Behind the Scenes

A JWT is a **bearer credential**: the verifier treats whoever presents a valid token *as* the subject, no questions asked. That makes the verifier's configuration the entire security boundary — and almost every JWT disaster reduces to **one root cause: the verifier trusted something the attacker controls.** The token header, the `alg` field, the claims, the absence of an expiry — all of these are attacker-influenced inputs until a *correct* signature check proves otherwise.

The most famous footgun is **`alg: none`**. The JOSE spec defines an "unsecured" token type with an empty signature. A naive verifier that reads the algorithm *from the token's own header* will happily accept a token whose signature was simply deleted — letting an attacker forge any payload. The defense is to **never** let the token choose its own algorithm: always pass an explicit `algorithms=[...]` allowlist to `jwt.decode`. PyJWT refuses `none` unless you dangerously opt in, but you should pin regardless.

The subtlest attack is **RS256→HS256 algorithm confusion**. An RS256 server verifies with a **public** key that is, by design, known to everyone. HS256 is **symmetric** — the same key signs and verifies. So an attacker takes the public key, uses its PEM bytes as an **HMAC secret**, forges an HS256 token, and a server misconfigured to allow `algorithms=["HS256","RS256"]` "verifies" it using that public key as the HMAC secret. Forgery complete, no private key required. Module 14 demonstrates all three outcomes for real: a deliberately *vulnerable* hand-rolled verifier accepts the forgery; **PyJWT 2.13 blocks it at the API** by refusing to use an asymmetric PEM as an HMAC secret (`InvalidKeyError`); and the fix you own — pinning `algorithms=["RS256"]` — rejects it outright. Don't lean on the library's guard alone; pin explicitly.

The remaining rules follow the same logic. **Decoding without verification is plumbing, not trust** — `verify_signature=False` is only for reading a `kid` to *choose* a key, never for reading claims you'll act on. **`exp` is mandatory** — a token with no expiry is valid forever, so use `options={"require": ["exp"]}` and short TTLs. **Secrets must be strong** — generate them with `secrets.token_urlsafe`, store them in env/secret managers, and rotate. And critically: **the payload is readable by anyone.** Signing is *not* encryption; base64url is reversible with no key, so never place passwords, PII, or secrets in claims.

### 🔍 A concrete analogy

A JWT is a backstage wristband: security only checks the *band*, never your face. `alg: none` is a band with the hologram peeled off that a lazy guard still waves through. Algorithm confusion is photocopying the *public* hologram pattern (the public key) and gluing it onto a fake band that a confused guard "validates" against that same pattern. And the payload being readable is the band's printed text — anyone standing near you can read your name and section, so you'd never write your PIN on it.

### ⚙️ What actually happens when you run the code

1. An attacker takes a legitimate token, swaps the header to `{"alg":"none"}`, edits the payload, and drops the signature segment.
2. A verifier that trusts the token's own `alg` accepts it — the forgery succeeds against the naive path.
3. For algorithm confusion: the server's RSA **public** key is exported as PEM and handed to the attacker (it's meant to be public).
4. The attacker computes `HMAC-SHA256("header.payload", public_pem_bytes)` and base64url-encodes it — a valid HS256 signature *for that secret*.
5. The deliberately vulnerable verifier recomputes the same HMAC with the public PEM and the signatures match → forged token accepted.
6. `jwt.decode(forged, public_pem, algorithms=["HS256","RS256"])` is rejected by modern PyJWT with `InvalidKeyError` (asymmetric PEM can't be an HMAC secret).
7. Pinning `algorithms=["RS256"]` rejects the forged HS256 token while genuine RS256 tokens still verify.

### 👀 What to notice when you run the examples

- `01_alg_none_attack.py`: PyJWT *refuses* `none` unless you explicitly opt in — the safe default in action.
- `03_algorithm_confusion_rsa_hmac.py`: the three labeled results — **forgery accepted** (vulnerable), **`InvalidKeyError`** (PyJWT guard), **rejected** (your `RS256` pin) — tell the whole story.
- `04_never_trust_unverified_claims.py`: claims pulled with `verify_signature=False` show `role=admin` with *no* signature check — proof that decoding ≠ trusting.
- `07_dont_put_secrets_in_payload.py`: the payload is extracted with **no key at all**, hammering home that base64url is not encryption.

### ⚠️ Common misconceptions

- **"PyJWT blocks confusion attacks, so I'm safe."** Its guard helps, but you must still pin `algorithms=[...]` explicitly — never echo the token's own `alg`.
- **"`verify_signature=False` is fine for reading claims."** Only for routing (picking a key by `kid`); never trust those claims.
- **"Signing hides the payload."** Signing proves integrity/authenticity; the payload stays readable by anyone.
- **"A long-lived token is convenient and harmless."** No `exp` (or a huge one) means a leaked token works forever — short TTL plus `require: ['exp']`.
