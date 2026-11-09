## 🧠 Mental Model — Behind the Scenes

RSA signing rests on a **trapdoor function**: multiplying two large primes is trivial, but factoring the product back into those primes is computationally infeasible. Your key pair is two views of that same secret number. The **private key** knows the factors (and a derived "private exponent" `d`); the **public key** only knows the product `n` and a small "public exponent" `e` (almost always 65537). Anyone can run the easy direction; only the private-key holder can run the hard direction. That one-way asymmetry is the whole game — and it's why you can publish the public key to the entire internet without ever risking forgery.

When PyJWT signs with `RS256`, it does **not** encrypt your payload. It builds the signing input `base64url(header) + "." + base64url(payload)`, hashes that with SHA-256, wraps the digest in **PKCS#1 v1.5 padding** (a fixed, deterministic byte template), and then applies the private-key trapdoor to the padded block. The result is the signature — the third segment of the JWT. Because the padding is fixed, RS256 is **fully deterministic**: the same payload and key always produce byte-for-byte the same token.

Verification reverses it: the public key transforms the signature back into the padded digest, the verifier independently re-hashes the header+payload it received, re-applies the same padding template, and checks for an exact match. If even one bit of the header or payload was tampered with, the recomputed digest won't match and PyJWT raises `InvalidSignatureError`. Notice what the signature size tracks: it equals the **modulus size**, not the hash. A 2048-bit key produces a 256-byte signature whether you choose `RS256`, `RS384`, or `RS512` — the hash choice only changes which SHA digest gets padded inside.

### 🔍 A concrete analogy

Think of a **wax seal pressed by a signet ring**. The ring (private key) is unique and you never let it leave your hand. The imprint it leaves (signature) can be examined by anyone holding a reference photo of your seal (public key) — they can confirm "yes, this is genuinely her ring" — but no amount of staring at the photo lets them carve a matching ring of their own.

### ⚙️ What actually happens when you run the code

1. `rsa.generate_private_key(public_exponent=65537, key_size=2048)` picks two ~1024-bit primes and derives the private exponent `d` and modulus `n`.
2. `private_key.public_key()` strips away the secret factors, keeping only `(n, e)` — the safely shareable half.
3. `jwt.encode(payload, private_key, algorithm="RS256")` SHA-256-hashes the `header.payload` string, applies PKCS#1 v1.5 padding, and runs the private-key trapdoor to produce the 256-byte signature.
4. The three base64url segments are joined with dots into the final token string.
5. `jwt.decode(token, public_key, algorithms=["RS256"])` re-hashes the received header+payload and uses the public key to confirm the signature wraps that exact digest.
6. A match returns the claims dict; any mismatch raises `InvalidSignatureError`.

### 👀 What to notice when you run the examples

- In `02_rs256_sign_verify.py`, signing uses `private_key` and decoding uses `public_key` — **two different objects**, the heart of asymmetric crypto.
- In `03_rs384_rs512.py`, the signature length stays **256 bytes** across all three RS variants — proof that size follows the key, not the hash.
- In `04_private_signs_public_verifies.py`, handing the public key to `jwt.encode` fails: it simply has no signing material.
- In `05_wrong_public_key_fails.py`, a foreign but perfectly valid public key still yields `InvalidSignatureError` — only the **paired** key validates.
- In `07_key_sizes.py`, the 3072-bit key is noticeably slower to generate and produces a larger 384-byte signature.

### ⚠️ Common misconceptions

- **"RSA encrypts the JWT."** No — it *signs*. The payload stays fully readable via base64url decode; signing only proves authenticity and integrity.
- **"The number in RS256 is the key size."** It's the **SHA hash** (256/384/512). Key size is chosen separately at generation (2048, 3072, …).
- **"Bigger hash means bigger signature."** Signature size equals the modulus length; the hash only changes the digest padded inside it.
- **"The public key is a secondary secret."** It's meant to be published (via JWKS). Its safety to share is the entire point of going asymmetric.
