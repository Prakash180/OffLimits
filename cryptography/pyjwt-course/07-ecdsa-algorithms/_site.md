## 🧠 Mental Model — Behind the Scenes

ECDSA swaps RSA's "factoring is hard" trapdoor for a different one: the **elliptic-curve discrete logarithm problem**. Picture a fixed point `G` on a curve and an operation that lets you "add" the point to itself many times. Your private key is a secret integer `d`; your public key is the point `Q = d·G`. Computing `Q` from `d` is fast, but recovering `d` from `Q` — undoing all those additions — is infeasible. The astonishing payoff is **size**: a 256-bit elliptic-curve key delivers roughly the same security as a 3072-bit RSA key, so keys, signatures, and therefore tokens all shrink dramatically.

The catch that trips up everyone is that **each `ES*` algorithm is welded to exactly one curve and one hash**. `ES256` means P-256 (`SECP256R1`) with SHA-256; `ES384` means P-384 with SHA-384; `ES512` means SHA-512 over **P-521** — *not* "P-512", which doesn't exist; and `ES256K` means the Bitcoin/Ethereum Koblitz curve `secp256k1` with SHA-256. You cannot mix a key on one curve with an algorithm expecting another — PyJWT raises `InvalidKeyError`.

There's a sharp security edge hiding in the signing step. Every ECDSA signature `(r, s)` requires a fresh, secret, **uniformly random nonce `k`**. If `k` ever repeats — or is even slightly predictable — an attacker can solve a little algebra and recover your private key outright. This is exactly how the 2010 Sony PS3 signing key was extracted: they reused `k`. So unlike RSA's deterministic padding, classic ECDSA's correctness *depends on a healthy random number generator at the moment of signing*. (Module 09's EdDSA was designed specifically to remove this footgun by deriving `k` deterministically.)

### 🔍 A concrete analogy

Imagine a **combination dial on a colossal circular track**. Spinning forward `d` clicks from the start lands you at a marked spot (your public point `Q`). Anyone can *check* you ended up at that spot, but staring at the spot tells them nothing about how many clicks you turned — the track is far too large to count backward. The secret nonce `k` is like a single-use scratch-off code you must never reuse on a second lock.

### ⚙️ What actually happens when you run the code

1. `ec.generate_private_key(ec.SECP256R1())` chooses a random secret integer `d` and computes the public point `Q = d·G` on the P-256 curve.
2. The keys are serialized to PEM (PKCS#8 private, SubjectPublicKeyInfo public) so PyJWT can consume the bytes directly.
3. `jwt.encode(payload, private_pem, algorithm="ES256")` SHA-256-hashes the signing input, draws a random nonce `k`, and computes the signature pair `(r, s)`.
4. PyJWT encodes `(r, s)` in the **JOSE/raw concatenated format** (not ASN.1 DER) and base64url-packs it as the token's third segment.
5. `jwt.decode(token, public_pem, algorithms=["ES256"])` re-hashes the input and uses the public point `Q` to confirm `(r, s)` is mathematically consistent.
6. A valid pair returns the claims; a wrong curve or tampered token fails.

### 👀 What to notice when you run the examples

- In `02_es256.py`, the signature segment is strikingly **short** — compare it mentally to RSA's 256-byte signatures from Module 06.
- In `04_es512.py`, the curve is `SECP521R1` (**521** bits) even though the algorithm is named ES**512** — that's the SHA-512 hash talking.
- In `06_curve_must_match_alg.py`, a P-256 key handed to `ES384` raises `InvalidKeyError` — hard proof the algorithm fixes the curve.
- In `05_es256k.py`, ES256K uses `secp256k1`, a *different* 256-bit curve from ES256's P-256 — same key size, not interchangeable.
- In `07_ecdsa_vs_rsa_size.py`, the EC key and signature are a fraction of the RSA equivalents at matching security levels.

### ⚠️ Common misconceptions

- **"ES512 uses a 512-bit curve."** It uses **P-521**. The 512 is the hash (SHA-512). There is no SECP512R1.
- **"ES256 and ES256K are the same."** Both are 256-bit + SHA-256, but on *different* curves (P-256 vs secp256k1). Keys don't cross over.
- **"ECDSA is deterministic like RSA."** It is **not** — it needs a secure random nonce per signature, and reuse leaks the private key.
- **"Smaller keys mean weaker security."** A 256-bit EC key matches RSA-3072. The compactness comes from harder math, not less safety.
