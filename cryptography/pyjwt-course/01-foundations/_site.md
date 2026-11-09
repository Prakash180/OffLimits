## 🧠 Mental Model — Behind the Scenes

A JWT looks like one opaque blob of gibberish, but it is really just **three pieces of text glued together with dots**: `header.payload.signature`. The first two pieces are nothing more than JSON dictionaries that have been run through base64url encoding — a reversible *transport* trick, not a lock. If you split the string on the dot and decode the chunks, the JSON pops right back out in plaintext. No key required. That single fact reorganizes everything: a JWT is a **public postcard with a tamper-evident seal**, not a sealed envelope.

The third piece — the signature — is where the cryptography lives. It is the raw output of an HMAC (for HS256) computed over the *exact* ASCII string `base64url(header) + "." + base64url(payload)`. Notice what gets signed: the **encoded** bytes, not your original Python dict. That is why even a single flipped character in the payload produces a completely different signature. The signature doesn't hide anything; it *binds* the header and payload together so that any change is detectable by anyone holding the secret.

base64url itself is worth internalizing. Standard base64 uses `+`, `/`, and `=` — all awkward inside URLs and HTTP headers. base64url swaps `+→-`, `/→_`, and **drops the `=` padding** so a token can be dropped straight into a `Authorization` header or query string. The cost: when you decode by hand you must *re-add* the padding back to a multiple of four, which is exactly what the scripts here do with `(-len(seg)) % 4`.

The deepest lesson of this module is the distinction between **integrity** and **confidentiality**. The signature gives you integrity (was this changed?) and authenticity (was this signed by someone with the key?). It gives you *zero* confidentiality. Reading the payload requires no secret at all — so anything secret you place inside is effectively public.

### 🔍 A concrete analogy

Think of a JWT as a **wax-sealed letter written in plain ink**. Anyone who intercepts it can read every word — the seal doesn't hide the text. But the seal is pressed with a unique signet ring (the secret). If a meddler scratches out a word and rewrites it, the seal cracks and no longer matches. You can't read the seal to learn the message; you only check whether it's intact.

### ⚙️ What actually happens when you run the code

1. `jwt.encode({...}, SECRET, algorithm="HS256")` serializes your dict to compact JSON, base64url-encodes the header and payload, joins them with a `.`, and computes the HMAC-SHA256 over that joined string.
2. The HMAC digest is itself base64url-encoded and appended as the third segment, producing one `str` (PyJWT 2.x returns `str`, not `bytes`).
3. The scripts call `token.split(".")` to recover the three segments as raw text.
4. `b64url_decode` re-adds the stripped `=` padding, then `base64.urlsafe_b64decode` turns each segment back into JSON bytes — **without any key**.
5. `jwt.decode(token, ..., options={"verify_signature": False})` reads the same claims while explicitly *skipping* the integrity check.
6. Tampering scripts mutate a byte in the payload segment, re-join the token, and call `decode()` with verification on — PyJWT recomputes the HMAC, finds a mismatch, and raises `InvalidSignatureError`.

### 👀 What to notice when you run the examples

- In `02_base64url_decode.py`, the header and payload print as readable JSON with **no secret supplied** — proof the payload is public.
- In `05_jwt_is_signed_not_encrypted.py`, a "secret" placed in the payload is recovered verbatim by anyone — the script is a live demonstration that JWTs are *not* encrypted.
- In `06_tampering_breaks_signature.py`, changing one character flips the verification from success to `InvalidSignatureError` — the seal cracks.
- In `07_get_unverified_header.py`, `get_unverified_header()` reads `alg`/`kid` *before* any key is chosen — useful for routing, never for trust.
- The signature segment is shorter and more random-looking than header/payload because it encodes 32 raw HMAC bytes, not JSON.

### ⚠️ Common misconceptions

- ❌ "JWTs are encrypted." False — they are **signed**. The payload is plain base64url JSON anyone can read.
- ❌ "I need the secret to read the claims." False — decoding requires no key; only *verifying* the signature does.
- ❌ "A successful unverified decode means the token is trustworthy." False — `verify_signature: False` and `get_unverified_header` return attacker-controllable data.
- ❌ "base64url is the same as base64." False — different alphabet (`-`/`_`) and no `=` padding, so manual decoding needs the padding restored first.
