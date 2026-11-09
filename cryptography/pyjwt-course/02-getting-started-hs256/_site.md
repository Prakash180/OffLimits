## 🧠 Mental Model — Behind the Scenes

HS256 is the **shared-secret** workhorse, and the key word is *symmetric*: the **same** secret both signs and verifies. There is no public half, no private half — just one key that does both jobs. That symmetry is HS256's superpower (dead simple, blazing fast) and its sharpest edge (anyone who can verify can also forge). The entire security of the scheme collapses to one question: *is the secret unguessable, and is it kept on the server only?*

Under the hood, `encode()` and `decode()` are mirror images of one HMAC computation. `encode()` builds the `header.payload` string and computes `HMAC_SHA256(secret, "header.payload")`, attaching the result as the signature. `decode()` does **not** "decrypt" anything — it re-runs the *exact same* HMAC over the received `header.payload` and compares its result to the signature that came in, byte-for-byte (using a constant-time comparison to resist timing attacks). Match → claims returned. Mismatch → `InvalidSignatureError`. Verification is just *re-signing and comparing*.

Two PyJWT 2.x details trip people up. First, `encode()` returns a **`str`**, not `bytes` — so the old `token.decode('utf-8')` line from 1.x tutorials crashes. Second, `decode()` **requires** `algorithms=[...]`. This isn't bureaucratic; it's a security boundary. If PyJWT trusted the token's own `alg` header, an attacker could set `alg: none` or swap algorithms to bypass verification. The allow-list says "I will only accept these algorithms" *before* looking at the token.

Secrets are bytes to HMAC. A `str` secret is UTF-8 encoded internally, so `"abc"` and `b"abc"` are the *same* key. But a real secret should be high-entropy random bytes (≥ 32 for HS256, matching SHA-256's output). PyJWT 2.13 actively nudges you: a key shorter than the hash size triggers an `InsecureKeyLengthWarning`, because short keys are brute-forceable offline.

### 🔍 A concrete analogy

HS256 is a **shared house key cut from a secret pattern**. Everyone trusted gets an identical copy. To check a guest's key you don't inspect it — you try it in the lock (re-compute the HMAC) and see if it turns. Because the key both *opens* and *could be copied to make new keys*, you'd never hand it to a stranger at the door. Keep it inside the house.

### ⚙️ What actually happens when you run the code

1. `jwt.encode({"user": "alice"}, secret, algorithm="HS256")` serializes claims, builds `header.payload`, and computes the HMAC-SHA256 using the UTF-8 bytes of the secret.
2. The digest is base64url-encoded and appended; a single `str` token is returned.
3. `jwt.decode(token, secret, algorithms=["HS256"])` re-splits the token and **recomputes** the HMAC over the received `header.payload`.
4. PyJWT compares the freshly computed signature to the token's signature in constant time.
5. On a match it returns the claims dict; on any mismatch (wrong secret, tampering) it raises `InvalidSignatureError`.
6. Omitting `algorithms=` raises `DecodeError` — the call refuses to guess which algorithm to trust.

### 👀 What to notice when you run the examples

- `03_str_vs_bytes.py` shows `encode()` returns a `str`, and that a `str` and `bytes` secret with the same characters verify each other — UTF-8 makes them identical keys.
- `04_wrong_secret_fails.py` produces `InvalidSignatureError` even though the token is perfectly well-formed — the signature simply doesn't match.
- `05_must_specify_algorithms.py` fails loudly without `algorithms=`, making the security requirement impossible to forget.
- `07_secret_strength.py` generates 32-byte secrets via `secrets.token_urlsafe`/`token_hex`/`os.urandom`; weak words would invite offline brute force.
- `08_full_login_simulation.py` ties it together: issue on "login", verify on each "request" — the real-world loop.

### ⚠️ Common misconceptions

- ❌ "`decode()` decrypts the token." False — it **re-computes the HMAC and compares**. Nothing is decrypted.
- ❌ "`encode()` returns bytes, so I should call `.decode('utf-8')`." False in PyJWT 2.x — it already returns `str`.
- ❌ "`algorithms=` is optional boilerplate." False — it's mandatory and your defense against `alg=none` and algorithm-confusion attacks.
- ❌ "Any string works as a secret." False — short/guessable keys are forgeable; PyJWT 2.13 even warns with `InsecureKeyLengthWarning` for keys under the hash size.
