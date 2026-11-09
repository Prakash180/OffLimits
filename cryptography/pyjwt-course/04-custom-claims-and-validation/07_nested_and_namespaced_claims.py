"""07 · Nested and namespaced custom claims.

Two patterns you'll meet in real tokens:

1. **Nested objects** — group related data under one key, e.g. a `context`
   object holding tenant + device info. The value is just nested JSON.

2. **Namespaced / URL-style keys** — to avoid collisions, identity providers
   prefix custom claims with a URI, e.g.
   ``"https://example.com/roles"``. OIDC and Auth0 use exactly this style. The
   key is an ordinary string; the URL has no network meaning here.

Both decode back as plain Python dict entries.

Run me:
    .venv/bin/python pyjwt-course/04-custom-claims-and-validation/07_nested_and_namespaced_claims.py
"""

import jwt

SECRET = "super-secret-shared-key-please-change-me"

# A namespace prefix you control, used to qualify private claims.
NS = "https://example.com/claims"


def main() -> None:
    payload = {
        "sub": "user-123",
        # (1) nested object claim
        "context": {
            "tenant": "acme-corp",
            "device": {"os": "linux", "trusted": True},
        },
        # (2) namespaced / URL-style claim keys
        f"{NS}/roles": ["editor", "billing"],
        f"{NS}/plan": "enterprise",
    }

    token = jwt.encode(payload, SECRET, algorithm="HS256")
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])

    # --- Reading nested claims -------------------------------------------
    print("Nested claims:")
    print("    tenant      :", decoded["context"]["tenant"])
    print("    device OS   :", decoded["context"]["device"]["os"])
    print("    device trust:", decoded["context"]["device"]["trusted"])

    # --- Reading namespaced claims ---------------------------------------
    print("\nNamespaced claims:")
    print("    roles:", decoded[f"{NS}/roles"])
    print("    plan :", decoded[f"{NS}/plan"])


if __name__ == "__main__":
    main()
