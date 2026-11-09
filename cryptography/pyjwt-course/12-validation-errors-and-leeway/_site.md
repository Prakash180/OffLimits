## 🧠 Mental Model — Behind the Scenes

`jwt.decode` looks like a single function call, but internally it is a **pipeline of independent checks** run in a specific order: is the string structurally three base64url segments? Does the signature verify against the key and pinned algorithm? Is `exp` in the past? Is `nbf` in the future? Does `aud` include us? Is `iss` trusted? Are all `require`d claims present? Each gate that fails raises a **specific, typed exception** — and crucially, those exceptions form an **inheritance tree** rooted at `PyJWTError`. That tree is the secret to writing auth code that is both robust and precise.

The hierarchy matters because of how Python's `except` matching works: it catches by *class and subclass*. `InvalidSignatureError` **is a** `DecodeError` **is an** `InvalidTokenError` **is a** `PyJWTError`. So `except InvalidTokenError` is the practical "reject this token" catch-all, while `except ExpiredSignatureError` lets you respond narrowly — say, by offering a token refresh instead of a hard `401`. The rule that falls out of this: **order your `except` blocks most-specific first**, otherwise a broad catch placed too early silently swallows the precise cases you wanted to distinguish.

The other half of this module is **leeway** — a deliberate tolerance for **clock skew**. Two servers never agree on the time to the millisecond; a token minted on a machine running three seconds fast can look "not yet valid" (`nbf` in the future) or "already expired" on a machine running slightly behind. `leeway=` (in seconds) widens the acceptance window on both the `exp` and `nbf` comparisons, so a token that is *just barely* outside the boundary still passes. The implementation is simply: compare `now` against `exp + leeway` and `nbf - leeway` instead of the raw values. Keep it to a few seconds — `leeway=3600` would mean expired tokens live an extra hour, which is a real security regression dressed up as forgiveness.

### 🔍 A concrete analogy

Think of airport boarding. A malformed boarding pass (unreadable barcode) is turned away at the scanner — that's a `DecodeError`. A forged pass with a bad signature is a `InvalidSignatureError`. A pass for *yesterday's* flight is `ExpiredSignatureError`; one for *tomorrow's* flight is `ImmatureSignatureError`; the right pass but for the *wrong gate* is `InvalidAudienceError`. Leeway is the gate agent letting you board 30 seconds after the official cutoff because their watch and yours disagree — a small, bounded grace, never an open door.

### ⚙️ What actually happens when you run the code

1. `jwt.decode` first splits and base64url-decodes the token; a structural failure raises `DecodeError`.
2. It recomputes/verifies the signature with your key and pinned `algorithms`; a mismatch raises `InvalidSignatureError` (a subclass of `DecodeError`).
3. It checks time claims: `exp` against now (+ leeway) → `ExpiredSignatureError`; `nbf` against now (− leeway) → `ImmatureSignatureError`.
4. It checks `aud`/`iss` if you passed `audience=`/`issuer=` → `InvalidAudienceError` / `InvalidIssuerError`.
5. It enforces `options={"require": [...]}` → `MissingRequiredClaimError` if any are absent.
6. The first failing gate raises; your `except` ladder catches it by its concrete type and maps it to a `(ok, reason, http_status)` triple.

### 👀 What to notice when you run the examples

- `01_exception_hierarchy.py` prints the actual class tree (via MRO) — you can *see* that `InvalidSignatureError` descends from `DecodeError`.
- `02`–`06` each trigger exactly **one** error type on purpose, so you learn the cause→exception mapping by demonstration.
- `07_leeway.py` shows the *same* just-expired token being **rejected** without leeway and **accepted** with `leeway=10`.
- `08_robust_validator.py` never lets an exception escape — every path returns a friendly reason and an HTTP status, the production-grade shape.

### ⚠️ Common misconceptions

- **"Catch `except Exception` to be safe."** That masks bugs and loses the precise reason; catch `PyJWTError`/`InvalidTokenError` instead.
- **"Order of `except` blocks doesn't matter."** It absolutely does — broad-before-specific swallows the specific cases.
- **"Leeway is harmless slack."** Large leeway extends the life of expired tokens; keep it to seconds.
- **"A token with no `exp` is fine."** It never expires — use `options={"require": ["exp"]}` for anything sensitive.
