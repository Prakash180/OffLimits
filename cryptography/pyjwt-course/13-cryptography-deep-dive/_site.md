## 🧠 Mental Model — Behind the Scenes

Strip the JSON costume off any JWT and you find three classic cryptographic primitives stacked on top of each other: **hashing → MACs → digital signatures.** A **hash** like SHA-256 is a one-way function: feed it any number of bytes and it spits out a fixed-size digest (32 bytes for SHA-256) that is infeasible to reverse. Flip a single input bit and roughly half the output bits flip — the **avalanche effect**. A hash proves the bytes didn't change *by accident*: that's **integrity**. But it proves nothing about *who* produced them, because anyone can recompute a hash. Integrity without **authenticity** is not security.

To add authenticity you mix a **secret** into the hash. That's an **HMAC** (Hash-based Message Authentication Code), and HMAC-SHA256 is *literally* the engine behind `HS256`. The reveal that makes JWTs click: an HS256 signature is exactly `base64url( HMAC-SHA256( "header.payload", secret ) )`. You can recompute it by hand with Python's `hmac` module and watch it come out **byte-for-byte identical** to the token's third segment. There is no magic — the verifier simply recomputes the same HMAC and compares with a constant-time check (`hmac.compare_digest`, never `==`, to avoid timing leaks). An attacker without the secret can't produce a matching segment.

HMAC is **symmetric**: the same secret both signs and verifies, so everyone who can verify can also forge. That's fine inside one trust boundary but useless for the public internet. **Digital signatures** solve this with **asymmetric** key pairs: a **private** key signs, and a mathematically-linked **public** key verifies. The private key never leaves the issuer; the public key can be published to the entire world (that's what JWKS does). This is why `RS256`/`ES256`/`PS256`/`EdDSA` let any client verify a provider's tokens while being unable to mint one. The security rests on **trapdoor functions** — operations easy one way but infeasible to reverse (integer factoring for RSA, the discrete-log problem on elliptic curves for ECDSA/EdDSA).

Finally, the *same* key wears different clothes depending on context: **PEM** (base64 text with `-----BEGIN-----` headers, what PyJWT usually wants), **DER** (the raw binary encoding underneath PEM), and **JWK** (the JSON form served by JWKS endpoints). Converting between them never changes the key — only its packaging.

### 🔍 A concrete analogy

A **hash** is a tamper-evident seal: break it and you can tell something changed, but anyone can buy the same seal. An **HMAC** is a seal pressed with a *shared signet ring* — only ring-holders can make or check it. A **digital signature** is a wax seal from a ring whose *impression* is published in the town square: everyone can confirm the impression matches the public pattern, but only the ring's owner can press a genuine one. Publishing the impression (public key) never lets anyone carve the ring (private key).

### ⚙️ What actually happens when you run the code

1. SHA-256 reduces arbitrary input to a fixed 32-byte digest; changing one character produces a wildly different digest (avalanche).
2. A demo shows a bare hash gives integrity but **not** authenticity — an attacker just recomputes it over their own forged payload.
3. PyJWT mints an HS256 token; the script splits off `header.payload.signature`.
4. Python's `hmac.new(secret, "header.payload", sha256).digest()` is computed independently and base64url-encoded without padding.
5. The hand-computed value is compared against the token's third segment — they match exactly, proving `HS256 == base64url(HMAC-SHA256)`.
6. An RSA private key signs a message and the public key verifies it, demonstrating the asymmetric (sign=private / verify=public) split behind `RS256`.
7. One public key is serialized three ways — PEM, DER (hex), JWK — showing they're the same key in different formats.

### 👀 What to notice when you run the examples

- `01_hashing_sha2.py`: the digest length is **fixed** regardless of input size, and a one-character change scrambles the whole output.
- `03_hmac_from_scratch.py`: the `IDENTICAL? True` line is the course's big "aha" — your handmade HMAC equals PyJWT's signature segment.
- `05_digital_signatures.py`: the *private* key signs, the *public* key verifies, and swapping in the wrong public key fails.
- `08_algorithm_family_tour.py`: signature **lengths** differ per family, and ECDSA/RSA-PSS produce a *different* signature each run (they're randomized — by design).

### ⚠️ Common misconceptions

- **"Hashing is encryption."** No — hashing is one-way; there is no "unhash" and you can't recover a payload from a signature.
- **"A hash alone authenticates the sender."** It only proves integrity; without a secret or private key, anyone can recompute it.
- **"Publishing a public key is risky."** Trapdoor math makes deriving the private key infeasible — publishing it is the intended design.
- **"A different signature each run means it's broken."** ECDSA and RSA-PSS are intentionally randomized; identical-every-time is *not* required.
