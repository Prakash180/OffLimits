## 🧠 Mental Model — Behind the Scenes

The registered claims (`iss`, `sub`, `aud`, `exp`, `nbf`, `iat`, `jti`) are just **seven short keys in the same plain JSON payload** you met in Module 01 — nothing magical lives in them. What makes them special is a *shared agreement*: RFC 7519 reserves these three-letter names so every issuer and verifier on Earth interprets them the same way. PyJWT's job is to turn that social contract into automatic checks.

The most important mental split is **time claims vs. identity claims**. The time claims (`exp`, `nbf`, and a future-dated `iat`) are checked **automatically** the moment they're present — PyJWT compares them against the current UTC clock with no arguments from you. The identity claims (`iss`, `aud`, `sub`) are **opt-in**: PyJWT ignores `iss` entirely unless you pass `issuer=`, ignores `aud` unless you pass `audience=`, and ignores `sub` unless you pass `subject=`. A token "valid for service A" sails through service B unless B explicitly verifies `aud`. This asymmetry is the single biggest source of real-world JWT bugs.

Under the hood, time claims are stored as **NumericDate** — plain integer seconds since the Unix epoch, *not* ISO strings. When you hand PyJWT a timezone-aware `datetime`, it calls `.timestamp()` to flatten it to that integer. On decode, PyJWT compares `now >= exp` (reject) and `now < nbf` (reject). This is why naive `datetime.now()` is dangerous: without a timezone the epoch conversion is ambiguous and can drift by hours. Always use `datetime.now(timezone.utc)`.

`aud` has its own quirk worth picturing: matching is a **set intersection**. The token's `aud` may be a single string or a *list*, and your `audience=` may also be one or many. The token passes if the two sets overlap by *any* value. And `jti`? PyJWT will store and return it, but it does **nothing** automatically — replay protection is your application's job, typically a denylist keyed by the `jti` UUID.

### 🔍 A concrete analogy

Think of a JWT as a **boarding pass**. The `exp` is the gate-closing time — the scanner rejects you automatically once it passes, no human judgment needed. The `aud` is the destination printed on the pass — but the gate agent only checks it if *they* care about destination; otherwise a London pass might scan fine at the Paris gate. The `jti` is the unique ticket number: it prevents the same pass being used twice *only if someone keeps a list of used numbers*.

### ⚙️ What actually happens when you run the code

1. You build a payload mixing identity claims (`iss`, `sub`, `aud`) and time claims (`exp`, `nbf`, `iat`), passing `datetime` objects for the times.
2. `jwt.encode()` converts each `datetime` to NumericDate (integer epoch seconds) and signs the result.
3. On `jwt.decode()`, PyJWT first verifies the signature, then **automatically** checks `exp` (reject if `now >= exp`) and `nbf` (reject if `now < nbf`).
4. PyJWT checks `iss`/`aud`/`sub` **only** because you passed `issuer=`, `audience=`, `subject=`; a mismatch raises `InvalidIssuerError` / `InvalidAudienceError` / `InvalidSubjectError`.
5. For `aud`, PyJWT intersects the token's audience(s) with your accepted audience(s) and passes on any overlap.
6. `jti` is returned in the claims dict; the script's own in-memory denylist decides whether the token was already used.

### 👀 What to notice when you run the examples

- In `05_exp_expiration.py`, an already-past `exp` raises `ExpiredSignatureError` with **no extra options** — time enforcement is automatic.
- In `06_nbf_not_before.py`, a future `nbf` raises `ImmatureSignatureError` — the token is valid, just "not yet."
- In `01_iss_issuer.py`/`03_aud_audience.py`, *omitting* `issuer=`/`audience=` silently skips the check — the "aha" that identity claims are opt-in.
- In `04_aud_multiple.py`, a list `aud` passes when *any* member matches — set-intersection in action.
- In `08_jti_jwt_id.py`, the first use of a `jti` succeeds and the second is rejected **only because the script tracks it** — PyJWT didn't do that for you.
- In `10_datetime_handling.py`, a `datetime` and a raw `int` epoch produce equivalent claims — proof of the NumericDate conversion.

### ⚠️ Common misconceptions

- ❌ "If a token has an `aud`, PyJWT checks it." False — only if you pass `audience=`; otherwise `aud` is ignored.
- ❌ "`jti` gives me replay protection for free." False — PyJWT stores it; *you* must keep the denylist.
- ❌ "`iat` is just informational and never blocks." Mostly true, but in PyJWT 2.13 a **future** `iat` raises `ImmatureSignatureError` (disable with `options={"verify_iat": False}`).
- ❌ "Naive `datetime.now()` is fine for `exp`." False — without a timezone the epoch conversion is ambiguous; use `datetime.now(timezone.utc)`.
