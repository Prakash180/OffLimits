"""08 · A robust, reusable token validator.

Pulling the whole module together: a single ``validate(token)`` function that
returns a tuple ``(ok, result)`` instead of letting exceptions escape. On success
``result`` is the claims dict; on failure it's a friendly explanation. We also map
each failure to an HTTP-like status, the way an API gateway would.

The try/except *ladder* matters: order matters because the exceptions are
subclasses of one another. We catch the **specific** cases first and the
**general** ``InvalidTokenError`` last, so each failure gets its precise message
while nothing slips through unhandled.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/08_robust_validator.py
"""

from datetime import UTC, datetime, timedelta

import jwt

SECRET = "teaching-secret-key-with-at-least-32-bytes!"
AUDIENCE = "my-api"


def validate(token: str) -> tuple[bool, dict | str, int]:
    """Validate a token. Returns (ok, claims_or_reason, http_status)."""
    try:
        claims = jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"],
            audience=AUDIENCE,
            options={"require": ["exp"]},  # demand an expiry
        )
        return True, claims, 200

    # --- specific cases first (most-derived -> least-derived) ---
    except jwt.ExpiredSignatureError:
        return False, "Token has expired — please re-authenticate.", 401
    except jwt.ImmatureSignatureError:
        return False, "Token is not valid yet (nbf in the future).", 401
    except jwt.InvalidAudienceError:
        return False, "Token audience mismatch — not issued for this service.", 403
    except jwt.InvalidIssuerError:
        return False, "Token issuer is not trusted.", 403
    except jwt.MissingRequiredClaimError as e:
        return False, f"Token is missing a required claim: {e}.", 400
    except jwt.InvalidSignatureError:
        return False, "Token signature is invalid — possible tampering.", 401
    except jwt.DecodeError:
        return False, "Token is malformed and cannot be decoded.", 400
    # --- catch-all for anything else in the JWT family ---
    except jwt.InvalidTokenError as e:
        return False, f"Token is invalid: {e}", 401


def _make(payload: dict) -> str:
    return jwt.encode(payload, SECRET, algorithm="HS256")


def main() -> None:
    now = datetime.now(UTC)
    good_base = {"sub": "u1", "aud": AUDIENCE, "exp": now + timedelta(hours=1)}

    cases = {
        "valid token": _make(good_base),
        "expired token": _make({**good_base, "exp": now - timedelta(hours=1)}),
        "wrong audience": _make({**good_base, "aud": "other-api"}),
        "missing exp": jwt.encode({"sub": "u1", "aud": AUDIENCE}, SECRET, algorithm="HS256"),
        "future nbf": _make({**good_base, "nbf": now + timedelta(hours=1)}),
        "tampered sig": _make(good_base)[:-3] + "xxx",
        "malformed": "not.a.jwt",
        "wrong key": jwt.encode(good_base, "different-secret-padded-to-32-plus-bytes!", algorithm="HS256"),
    }

    print(f"{'case':<16} {'status':>6}  result")
    print("-" * 70)
    for name, tok in cases.items():
        ok, result, status = validate(tok)
        shown = result if isinstance(result, str) else f"claims OK (sub={result.get('sub')})"
        flag = "✅" if ok else "❌"
        print(f"{name:<16} {status:>6}  {flag} {shown}")

    print()
    print("✅ One validate() funnels every failure mode into a clean (ok, reason, status).")


if __name__ == "__main__":
    main()
