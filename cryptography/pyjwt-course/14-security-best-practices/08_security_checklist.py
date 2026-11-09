"""
08 · The JWT security checklist
================================

A consolidated, actionable checklist distilled from this whole module. Pin it
to your wall, paste it into your code review template, and run through it for
every service that issues or validates JWTs.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/14-security-best-practices/08_security_checklist.py
"""


CHECKLIST: dict[str, list[str]] = {
    "Algorithm safety": [
        "Always pass algorithms=[...] to jwt.decode — pin the EXACT alg(s).",
        "Never read 'alg' from the token header and feed it back to decode.",
        "Never allow 'none' for tokens from untrusted sources.",
        "Never mix symmetric (HS*) and asymmetric (RS*/ES*) in one allow-list.",
    ],
    "Claim validation": [
        "Verify exp (and require it): options={'require': ['exp']}.",
        "Verify aud — pass audience=... so tokens for other apps are rejected.",
        "Verify iss — pass issuer=... to bind tokens to your trusted issuer.",
        "Validate nbf/iat; allow small leeway only for clock skew.",
        "Require the claims you depend on (sub, aud, iss, exp).",
    ],
    "Keys & secrets": [
        "HS256 secret >= 32 random bytes (secrets.token_urlsafe(32)).",
        "Never hardcode secrets; load from env / secret manager / KMS.",
        "Rotate signing keys regularly and on any suspected compromise.",
        "Prefer asymmetric (RS256/ES256/EdDSA) when 3rd parties must verify.",
        "Validate 'kid' against an ALLOWLIST of known keys (no arbitrary fetch).",
    ],
    "Token lifecycle": [
        "Keep access tokens short-lived (minutes); use refresh tokens for length.",
        "Treat JWTs as bearer credentials — always transmit over TLS only.",
        "Have a revocation strategy (short TTL, denylist, or key rotation).",
    ],
    "Data hygiene": [
        "Never put secrets/PII in the payload — it is readable by anyone.",
        "Signing protects integrity, NOT confidentiality. Use JWE if you must.",
        "Use constant-time comparisons for any custom token checks.",
    ],
    "Operational": [
        "Pin your JWT library version; track its CVEs.",
        "Fail closed: on any validation error, deny access.",
        "Log verification failures (without logging the token's secrets).",
    ],
}


def main() -> None:
    print("=" * 72)
    print("✅  JWT SECURITY CHECKLIST")
    print("=" * 72)
    total = 0
    for section, items in CHECKLIST.items():
        print(f"\n▶ {section}")
        print("-" * 72)
        for item in items:
            total += 1
            print(f"  [ ] {item}")

    print("\n" + "=" * 72)
    print(f"{total} checks across {len(CHECKLIST)} categories.")
    print("Golden rule: PIN THE ALGORITHM, VERIFY THE CLAIMS, GUARD THE KEYS.")
    print("=" * 72)


if __name__ == "__main__":
    main()
