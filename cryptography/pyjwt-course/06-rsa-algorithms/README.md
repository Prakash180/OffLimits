# 🗝️ Module 06 — RSA Algorithms (`RS256` / `RS384` / `RS512`)

> The asymmetric family. A **private** key signs; a **public** key verifies.
> Publish the public key to the whole world and they can confirm your tokens
> are genuine — yet **none of them can forge one**. This is the foundation of
> OAuth2 / OpenID Connect.

---

## 🧠 Why asymmetric signing matters

HMAC (Module 05) uses one shared secret, so *verify == sign*. That breaks down
the moment you need **untrusted third parties** to verify tokens without being
able to mint their own.

RSA solves this with a **key pair**:

- 🔒 **Private key** — kept secret. **Signs** tokens. Never leaves the issuer.
- 🌍 **Public key** — shared freely. **Verifies** tokens. Cannot sign.

```mermaid
flowchart LR
    subgraph Issuer ["Issuer (e.g. OAuth provider)"]
        PK[Private key 🔒]
    end
    PK -- "sign" --> JWT[JWT]
    JWT -- "verify" --> V1[Service A 🌍]
    JWT -- "verify" --> V2[Service B 🌍]
    JWT -- "verify" --> V3[Mobile app 🌍]
    PUB[Public key 🌍] -. "distributed via JWKS" .-> V1
    PUB -.-> V2
    PUB -.-> V3
```

Anyone with the public key can verify; only the holder of the private key can
sign. That asymmetry is what makes federated identity possible.

> 🔐 **Naming note:** `RS` = **R**SASSA-PKCS1-v1_5 + **S**HA. So `RS256` =
> RSASSA-PKCS1-v1_5 signatures using SHA-256. The number is the hash; the
> signature *size* is governed by the **key size** (2048-bit key → 256-byte
> signature), not the hash.

---

## 📜 Scripts in this module

| # | Script | What it shows | Run command |
|---|--------|---------------|-------------|
| 1 | [01_generate_rsa_keypair.py](01_generate_rsa_keypair.py) | Generate RSA-2048; serialize private (PKCS#8) & public (SPKI) PEM | `.venv/bin/python pyjwt-course/06-rsa-algorithms/01_generate_rsa_keypair.py` |
| 2 | [02_rs256_sign_verify.py](02_rs256_sign_verify.py) | Sign with private key, verify with public (`RS256`) | `.venv/bin/python pyjwt-course/06-rsa-algorithms/02_rs256_sign_verify.py` |
| 3 | [03_rs384_rs512.py](03_rs384_rs512.py) | The `RS384` and `RS512` variants | `.venv/bin/python pyjwt-course/06-rsa-algorithms/03_rs384_rs512.py` |
| 4 | [04_private_signs_public_verifies.py](04_private_signs_public_verifies.py) | Public key verifies but **cannot** sign | `.venv/bin/python pyjwt-course/06-rsa-algorithms/04_private_signs_public_verifies.py` |
| 5 | [05_wrong_public_key_fails.py](05_wrong_public_key_fails.py) | A mismatched public key → `InvalidSignatureError` | `.venv/bin/python pyjwt-course/06-rsa-algorithms/05_wrong_public_key_fails.py` |
| 6 | [06_load_keys_from_pem.py](06_load_keys_from_pem.py) | Write PEMs to temp files, reload with `load_pem_*` | `.venv/bin/python pyjwt-course/06-rsa-algorithms/06_load_keys_from_pem.py` |
| 7 | [07_key_sizes.py](07_key_sizes.py) | 2048 vs 3072-bit: security/perf tradeoff | `.venv/bin/python pyjwt-course/06-rsa-algorithms/07_key_sizes.py` |
| 8 | [08_rsa_vs_hmac_when_to_use.py](08_rsa_vs_hmac_when_to_use.py) | HMAC vs RSA side by side — when to pick which | `.venv/bin/python pyjwt-course/06-rsa-algorithms/08_rsa_vs_hmac_when_to_use.py` |

Run them all:

```bash
# from the repo root: /home/astro/catalyst/jwt-test
for f in pyjwt-course/06-rsa-algorithms/*.py; do .venv/bin/python "$f"; done
```

---

## 🔄 Sign / verify at a glance

```mermaid
sequenceDiagram
    participant I as Issuer
    participant T as JWT
    participant V as Verifier
    I->>T: jwt.encode(payload, PRIVATE_KEY, "RS256")
    Note over I,T: only the private key can produce this signature
    T->>V: token travels over the wire
    V->>V: jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    Note over V: public key proves authenticity,<br/>cannot mint new tokens
```

---

## 🧩 PEM key formats you'll see

| Key | PyJWT/cryptography format | PEM header |
|-----|---------------------------|-----------|
| Private | PKCS#8 (`PrivateFormat.PKCS8`) | `-----BEGIN PRIVATE KEY-----` |
| Public | SubjectPublicKeyInfo (`PublicFormat.SubjectPublicKeyInfo`) | `-----BEGIN PUBLIC KEY-----` |

PyJWT happily accepts **either** raw PEM strings/bytes **or** `cryptography`
key objects in `jwt.encode` / `jwt.decode`.

---

## ✨ Key takeaways

- **Private signs, public verifies.** The public key can be published; it
  enables verification, never forgery.
- **Signature size = key size / 8.** A 2048-bit key always yields a 256-byte
  signature regardless of `RS256`/`384`/`512`.
- **Wrong/foreign public key ⇒ `InvalidSignatureError`.** Only the paired key
  validates.
- **2048-bit is the modern minimum.** 3072-bit adds margin at a CPU cost; keys
  under 2048 are considered weak.

---

## ⚠️ Pitfalls

- 🚫 **Leaking the private key.** Game over — anyone can forge. Store it in a
  secret manager / HSM, never in source control.
- 🚫 **Confusing the keys.** Sign with **private**, verify with **public**.
  Handing `jwt.encode` a public key fails (it has no signing material).
- 🚫 **Trusting the header's `alg`.** Always pin accepted algorithms in
  `algorithms=[...]`; never let a token dictate `none` or downgrade you from
  `RS256` to `HS256`.
- 🚫 **Unencrypted private PEMs in transit.** The demo uses `NoEncryption()`
  for clarity; protect real private keys at rest.

---

## ➡️ Next

RSA's `RS*` family uses deterministic PKCS#1 v1.5 padding. The next modules
explore **ECDSA** (smaller keys, same asymmetric model) and **RSA-PSS** (`PS*`,
randomized padding). See [Module 07 — ECDSA](../07-ecdsa-algorithms/) and
[Module 08 — RSA-PSS](../08-rsa-pss-algorithms/).
