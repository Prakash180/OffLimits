# The PyJWT Codex — Visual Asset Pack

Static visual assets for the dark-themed PyJWT & cryptography learning site.
All assets use the brand palette and are designed for **transparent / dark backgrounds**.

**Palette:** bg `#0b1020` / `#0f172a` · cyan `#22d3ee` · violet `#a78bfa` · emerald `#34d399` · amber `#fbbf24` · pink `#f472b6`

## A) Lottie animations — `lottie/`

Bodymovin / lottie-web compatible JSON. 30 fps, loopable (`ip:0`).

| File | Dimensions | Depicts | Intended use |
|------|-----------|---------|--------------|
| `hero-shield.json` | 512×512 | Shield + padlock outline that breathes (scale/opacity), cyan stroke with violet lock | Hero section background / landing focal animation |
| `key-rotate.json` | 256×256 | Stylized amber key rotating 360° on loop | Key-management & rotation module headers; loaders |
| `signature-check.json` | 256×256 | Emerald ring draws in, cyan checkmark scales ("verified") | Signature-verification callouts; success states |
| `token-flow.json` | 600×200 | Header / payload / signature rounded segments slide + fade in sequence to assemble a token | "Anatomy of a JWT" intro; structure explainer |

## B) Explanatory SVGs — `svg/`

Self-contained, `viewBox` set, transparent background, subtle inline-CSS animation (respects `prefers-reduced-motion`); all readable static.

| File | Dimensions | Depicts | Intended use |
|------|-----------|---------|--------------|
| `jwt-structure.svg` | 760×240 | Three segments `header.payload.signature` (cyan / violet / emerald) with dots and labels | Foundations module; structure concept callout |
| `sign-verify-flow.svg` | 820×260 | Private key signs → token → public key verifies; dashed "marching" flow arrows | Sign/verify lesson header; HS/RS overview |
| `sym-vs-asym.svg` | 820×320 | Left: one shared secret between A & B; right: public/private keypair | Symmetric vs asymmetric concept page |
| `algorithm-families.svg` | 840×360 | Grid of HMAC (HS), RSA (RS/PS), ECDSA (ES), EdDSA (Ed) with one-line descriptors | Algorithms overview / chooser section |
| `key-rotation.svg` | 820×360 | JWKS with two keys (kid A retired, kid B active); token `kid` selects matching key | JWKS & key-rotation module |
| `logo.svg` | 300×88 (scales 40–200px) | "PyJWT Codex" wordmark + tile mark combining `{}` braces and a padlock/keyhole | Site header, favicon source, footer, social card |

## Verification

- Lottie: `uv run python -c "import json; d=json.load(open('FILE')); assert all(k in d for k in ('v','fr','ip','op','w','h','layers'))"`
- SVG: `uv run python -c "import xml.dom.minidom as m; m.parse('FILE')"`

All 4 Lottie files and 6 SVG files verified valid.
