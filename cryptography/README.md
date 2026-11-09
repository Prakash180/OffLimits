# jwt-test

Experiments with [PyJWT](https://pyjwt.readthedocs.io/) plus a full hands-on
learning course.

- [`main.py`](main.py) — minimal HS256 encode/decode smoke test.
- [`tests/`](tests/) — Microsoft Entra ID (Azure AD) OAuth2 / OIDC flow:
  authorization-code login ([`authurl.py`](tests/authurl.py),
  [`tokenapi.py`](tests/tokenapi.py)) and JWKS-based access-token validation
  ([`validate.py`](tests/validate.py), [`validateapi.py`](tests/validateapi.py)).

## 📚 The PyJWT course

A complete, end-to-end PyJWT curriculum lives in
[`pyjwt-course/`](pyjwt-course/) — **118 runnable, verified examples** across 16
modules, from the raw bytes of a token to production OAuth2/OIDC, with a deep
dive into the underlying cryptography. Module 16 is a **fully local OAuth2/OIDC
identity provider**, so authentication can be learned and tested without Azure.

Start here: [`pyjwt-course/README.md`](pyjwt-course/README.md)

```bash
uv run python pyjwt-course/01-foundations/01_anatomy_of_a_jwt.py
```

## 🌐 The interactive website

An offline-capable static site (`sitegen/` → `site/`) explains every module and
every example with a dark cryptographic theme, Lottie animations, Mermaid
diagrams, captured outputs, and an in-browser JWT decoder.

```bash
uv run --with markdown --with pygments python sitegen/build.py   # build → site/
cd site && uv run python -m http.server 8777                     # http://localhost:8777
```
