## 🧠 Mental Model — Behind the Scenes

The HMAC family — `HS256`, `HS384`, `HS512` — is one algorithm with three hash sizes bolted in. **HMAC** means *Hash-based Message Authentication Code*, and the formula is the heart of the whole module: `signature = HMAC_SHA(secret, base64url(header) + "." + base64url(payload))`. The number in the name (`256`/`384`/`512`) is simply *which SHA-2 hash* runs inside. Everything else — the symmetry, the trust model, the verification dance — is identical across all three.

HMAC isn't a plain hash; it's a *keyed* construction. Internally it mixes the secret into the message in two passes (an inner and outer hash, each with the secret XOR'd against a pad), which is what stops an attacker from extending or forging a digest without knowing the key. The practical upshot you can hold in your head: **the signature is the raw hash digest, and its length equals the digest size** — HS256 → 32 bytes, HS384 → 48, HS512 → 64. A bigger hash means a longer signature and a marginally longer token; all three are cryptographically secure, and HS256 is the sensible default.

The defining trait of the entire family is **symmetry**: there is exactly *one* secret, and it both signs and verifies. This is the same coin from Module 02, now seen as a *trust model*. Because verifying requires the same key as signing, **whoever can verify can also forge**. That's why HMAC fits a single party or a tight cluster of mutually trusted services sharing a secret out-of-band — and why it's the *wrong* choice the moment an untrusted third party needs to verify (that's RSA/ECDSA territory in later modules).

Two operational realities round out the model. First, **key length matters per algorithm**: RFC 7518 recommends a key at least as long as the hash output, and PyJWT 2.13 emits an `InsecureKeyLengthWarning` for short keys. Second, **rotation is just a list**: sign new tokens with the newest secret, but accept verification against `[newest, …older]` so in-flight tokens keep working, then retire the old secret once its tokens have all expired.

### 🔍 A concrete analogy

HMAC is a **tamper-evident seal pressed from a secret die**, and the SHA size is *how finely the die is engraved*. SHA-256 is a 32-notch die; SHA-512 is a 64-notch die — more notches, a longer impression, but the same kind of seal. Anyone holding a copy of the die can both *make* genuine seals and *check* them — which is exactly why you'd only ever share the die inside your own workshop, never with outside vendors.

### ⚙️ What actually happens when you run the code

1. `jwt.encode(payload, SECRET, algorithm="HS384")` builds the `header.payload` string, with the header recording `"alg": "HS384"`.
2. PyJWT runs `HMAC_SHA384(SECRET, "header.payload")`, producing a 48-byte digest.
3. That digest is base64url-encoded and appended as the third segment; a `str` token is returned.
4. `jwt.decode(token, SECRET, algorithms=["HS384"])` re-computes the same HMAC over the received `header.payload` and constant-time-compares it to the signature.
5. In `04_compare_signature_sizes.py`, the script base64url-*decodes* the signature segment and measures its raw byte length, proving 32/48/64 bytes for 256/384/512.
6. In rotation (`06_secret_rotation_hmac.py`), `decode()` is retried across a candidate list of secrets until one verifies — the others raise `InvalidSignatureError` and are skipped.

### 👀 What to notice when you run the examples

- Across `01`–`03`, only the algorithm name changes — the API and round-trip are identical, hammering home that it's one family.
- In `01_hs256.py`, reading the unverified header shows `alg` matches the algorithm you signed with.
- In `04_compare_signature_sizes.py`, the measured signature lengths come out exactly 32/48/64 bytes — the digest size *is* the signature size.
- In `05_shared_secret_model.py`, two simulated parties using the **same** secret both verify successfully — and that's precisely why each could also forge.
- In `06_secret_rotation_hmac.py`, a token signed with the *old* secret still verifies during the overlap window because the verifier tries multiple candidate secrets.

### ⚠️ Common misconceptions

- ❌ "HS512 is more secure than HS256, so always use it." Overstated — all three are secure; the difference is signature length, and HS256 is a fine default.
- ❌ "The `256` is the key length." False — it's the **SHA hash size**; the key should be *at least* that many bytes (PyJWT 2.13 warns with `InsecureKeyLengthWarning` if shorter).
- ❌ "I can give the verify secret to third parties to verify tokens." Dangerous — with HMAC, verify == sign, so they could forge. Use RSA/ECDSA for that.
- ❌ "Rotating secrets means an instant cutover." False — you accept a *list* of secrets during overlap, then drop the old one once its tokens expire.
