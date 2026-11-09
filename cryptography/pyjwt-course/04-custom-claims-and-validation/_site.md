## 🧠 Mental Model — Behind the Scenes

A JWT payload is **open-ended JSON**, so beyond the seven registered names you can add any **private claim** your app needs — `roles`, `tenant`, `email`, feature flags. PyJWT treats them as opaque data: it signs them like everything else, but it has no opinion about their meaning. That means *reading* them is trivial (`decoded["roles"]`), and *trusting* them is entirely a function of whether you verified the signature first. The whole module orbits one idea: **the signature decides trust; the claims decide policy**, and you must never blur the two.

The real subject here is `decode()`'s **control surface** — the `options`, `require`, and `leeway` knobs. By default PyJWT is strict in the ways that matter: it verifies the signature, and it enforces `exp` when present. Each knob *relaxes or tightens* one specific guardrail. `options={"verify_signature": False}` turns decoding into a pure base64url read — fast for inspection, but the returned claims are **attacker-controllable** and must never drive authorization. Critically, disabling signature verification also disables the dependent claim checks, because there's nothing trustworthy left to check.

`require=[...]` is about **presence, not value**: it forces certain claims to exist, raising `MissingRequiredClaimError` if not. Think of it as a schema gate — "every token *must* carry `exp`, `iss`, `sub`" — that runs before your value-level logic. It pairs naturally with the value checks (`issuer=`, `audience=`) from Module 03: `require` ensures the claim is there, those parameters check it's correct.

`leeway` exists because **clocks drift**. Two servers rarely agree to the millisecond, so a token that expired "one second ago" by your clock may be perfectly fresh by the issuer's. `leeway=timedelta(seconds=10)` widens the `exp`/`nbf`/`iat` boundaries by that grace window — PyJWT effectively compares against `exp + leeway`. The danger is obvious once you see it: every second of leeway is a second of extra replay window *past* expiry, so it should be seconds, never minutes.

### 🔍 A concrete analogy

Picture a **nightclub door**. The bouncer first checks the wristband is genuine (signature) — fake band, you're out, no further questions. `require` is the rule "everyone must show ID *and* a ticket" — missing either and you're turned away before they even read them. The value checks are reading the ID's name against the guest list. And `leeway` is the bouncer letting in someone whose ticket says "valid until 11:00" at 11:00:08 because the club clock and the ticket printer disagree by a few seconds — generous by seconds, never by an hour.

### ⚙️ What actually happens when you run the code

1. `jwt.encode()` packs registered *and* custom claims into one signed payload — PyJWT doesn't distinguish them while signing.
2. A normal `jwt.decode(token, secret, algorithms=[...])` verifies the signature, enforces `exp`, then returns the full claims dict including your custom keys.
3. With `options={"require": ["exp", "iss", "sub"]}`, PyJWT checks each listed claim **exists** before value checks; a gap raises `MissingRequiredClaimError`.
4. With `leeway=timedelta(seconds=N)`, the `exp`/`nbf` comparisons are widened by `N` seconds, so a just-expired token can still pass.
5. With `options={"verify_signature": False}`, PyJWT skips the HMAC check (and the dependent `exp`/`aud` checks) and simply base64url-decodes the payload — **untrusted**.
6. Your code then reads custom claims (e.g. `roles`) and makes the authorization decision — which is only sound if step 2's signature check actually ran.

### 👀 What to notice when you run the examples

- In `01_custom_claims.py`, custom keys come back exactly as inserted — they're just JSON the signature protects.
- In `02_options_verify_signature.py`, the claims still decode with verification off, underscoring that an unverified read is *data*, not *trust*.
- In `05_require_claims.py`, removing a required claim raises `MissingRequiredClaimError` *before* any value comparison — presence is checked first.
- In `06_leeway.py`, a token that fails without leeway **passes** with a small `leeway` at the `exp` boundary — clock-skew tolerance made visible.
- In `08_role_based_access_demo.py`, `authorize()` grants or denies based on the `roles` claim — but only meaningfully because the token was verified first.

### ⚠️ Common misconceptions

- ❌ "I can authorize on claims I read with `verify_signature: False`." False — those claims are attacker-controlled; never authorize on them.
- ❌ "`require` checks the claim's value." False — it only checks **presence**; value checks (`issuer=`, `audience=`) are separate.
- ❌ "More `leeway` is safer." Backwards — leeway *extends* the validity window past `exp`, widening the replay window. Keep it to seconds.
- ❌ "Custom claims are private/hidden." False — the payload is base64url-encoded plaintext; anyone can read your `roles`/`email`. Never store secrets there.
