#!/usr/bin/env python3
"""
The PyJWT Codex — static site generator.

Reads the pyjwt-course/ modules (READMEs, _site.md narratives, and the numbered
lesson scripts), runs each lesson script to capture its real output, and emits a
self-contained static website into ../site.

Run (no venv activation needed):

    uv run --with markdown --with pygments python sitegen/build.py

Everything is offline-capable after build: third-party libs (mermaid, lottie-web)
are vendored into site/assets/vendor on first build.
"""
from __future__ import annotations

import ast
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import markdown as md
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

# --------------------------------------------------------------------------- #
# paths
# --------------------------------------------------------------------------- #
SITEGEN = Path(__file__).resolve().parent
REPO = SITEGEN.parent
COURSE = REPO / "pyjwt-course"
OUT = REPO / "site"
ASSETS_SRC = SITEGEN / "assets_src"
CACHE = SITEGEN / ".cache"
CACHE.mkdir(exist_ok=True)

ACCENTS = [
    ("#22d3ee", "#0ea5e9"), ("#a78bfa", "#7c3aed"), ("#34d399", "#10b981"),
    ("#fbbf24", "#f59e0b"), ("#f472b6", "#db2777"), ("#60a5fa", "#2563eb"),
    ("#f87171", "#dc2626"), ("#a3e635", "#65a30d"),
]

VENDOR = {
    "mermaid.min.js": "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js",
    "lottie.min.js": "https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie_light.min.js",
}

YEAR = time.strftime("%Y")

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def nice_title(stem: str) -> str:
    """`05_exp_expiration` -> `Exp Expiration` (drops the NN_ prefix)."""
    name = re.sub(r"^\d+_", "", stem)
    words = name.replace("_", " ").split()
    keep_upper = {"jwt", "jwks", "jwk", "hmac", "rsa", "ecdsa", "eddsa", "pss",
                  "kid", "iat", "exp", "nbf", "iss", "sub", "aud", "jti", "oidc",
                  "id", "api", "pem", "der", "hs256", "rs256", "es256", "ps256",
                  "rs384", "rs512", "es512", "es384", "es256k", "ps384", "ps512",
                  "ed25519", "ed448", "url", "http", "fastapi"}
    out = []
    for w in words:
        lw = w.lower()
        if lw in keep_upper:
            out.append("EdDSA" if lw == "eddsa" else "FastAPI" if lw == "fastapi" else w.upper())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def module_meta(folder: Path) -> dict:
    """slug, num, title from folder + README H1."""
    slug = folder.name
    num = slug[:2]
    readme = read(folder / "README.md")
    m = re.search(r"^#\s+(.+)$", readme, re.MULTILINE)
    raw = m.group(1).strip() if m else nice_title(slug[3:])
    # strip leading emoji/symbols and any leading number
    title = re.sub(r"^[^\w(]*", "", raw).strip()
    title = re.sub(r"^\d+[\.\)]\s*", "", title)
    # drop markdown emphasis markers that leak from the README heading
    title = title.replace("`", "").replace("**", "").replace("*", "").replace("_", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return {"slug": slug, "num": num, "title": title or slug}


def get_docstring(src: str) -> str:
    try:
        doc = ast.get_docstring(ast.parse(src))
    except SyntaxError:
        doc = None
    return (doc or "").strip()


def docstring_to_html(doc: str) -> str:
    """Turn a lesson script's module docstring into a friendly intro.

    The scripts use a heading-underline style (`Title\n=====`). Keep the body
    paragraphs, drop the redundant title/underline lines, render as markdown.
    """
    lines = doc.splitlines()
    # drop a leading "Title" + "====/----" pair
    if len(lines) >= 2 and set(lines[1].strip()) <= {"=", "-"} and lines[1].strip():
        lines = lines[2:]
    cleaned = "\n".join(lines).strip()
    return md_to_html(cleaned)


# --------------------------------------------------------------------------- #
# markdown rendering (mermaid-aware + pygments highlight)
# --------------------------------------------------------------------------- #
_MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def md_to_html(text: str) -> str:
    if not text.strip():
        return ""
    blocks: list[str] = []

    def stash(m):
        blocks.append(m.group(1))
        return f"\n\n@@MERMAID{len(blocks) - 1}@@\n\n"

    text = _MERMAID_RE.sub(stash, text)

    converter = md.Markdown(
        extensions=["extra", "sane_lists", "toc", "codehilite"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "codehl",
                           "pygments_style": "monokai"},
            "toc": {"permalink": False},
        },
    )
    out = converter.convert(text)

    # restore mermaid blocks
    def restore(idx: int) -> str:
        graph = html.escape(blocks[idx].strip())
        return (f'<div class="mermaid-wrap reveal"><div class="mermaid">{graph}</div></div>')

    for i in range(len(blocks)):
        token = f"@@MERMAID{i}@@"
        out = out.replace(f"<p>{token}</p>", restore(i)).replace(token, restore(i))

    out = rewrite_links(out)
    return out


def rewrite_links(html_text: str) -> str:
    def repl(m):
        href = m.group(1)
        # external
        if href.startswith("http://") or href.startswith("https://"):
            return f'href="{href}" target="_blank" rel="noopener"'
        if href.startswith("#") or href.startswith("mailto:"):
            return f'href="{href}"'
        # link to a lesson script -> jump to its example accordion
        mpy = re.search(r"([0-9A-Za-z_]+)\.py(?:#.*)?$", href)
        if mpy:
            return f'href="#ex-{mpy.group(1)}"'
        # link to another module folder -> its module page
        mmod = re.search(r"(\d\d-[a-z0-9-]+)/?$", href.rstrip("/"))
        if mmod:
            return f'href="{mmod.group(1)}.html"'
        # neutralise other repo-relative links
        return 'href="#"'

    return re.sub(r'href="([^"]+)"', repl, html_text)


def highlight_py(src: str) -> str:
    formatter = HtmlFormatter(cssclass="codehl", nowrap=False)
    return highlight(src, PythonLexer(), formatter)


# --------------------------------------------------------------------------- #
# run lesson scripts, capture stdout (cached by mtime)
# --------------------------------------------------------------------------- #
def load_cache() -> dict:
    p = CACHE / "outputs.json"
    return json.loads(read(p)) if p.exists() else {}


def run_script(path: Path, cache: dict) -> str:
    rel = str(path.relative_to(REPO))
    mtime = path.stat().st_mtime
    hit = cache.get(rel)
    if hit and abs(hit.get("mtime", 0) - mtime) < 1e-6:
        return hit["stdout"]
    print(f"    running {rel}")
    try:
        proc = subprocess.run(
            [sys.executable, str(path)], cwd=REPO, capture_output=True,
            text=True, timeout=180,
            env={**os.environ, "PYTHONWARNINGS": "ignore", "NO_COLOR": "1"},
        )
        stdout = proc.stdout.rstrip("\n")
        if proc.returncode != 0:
            stdout += f"\n\n[exit code {proc.returncode}]"
            err = (proc.stderr or "").strip().splitlines()
            if err:
                stdout += "\n" + "\n".join(err[-6:])
    except subprocess.TimeoutExpired:
        stdout = "[skipped: timed out]"
    cache[rel] = {"mtime": mtime, "stdout": stdout}
    return stdout


# --------------------------------------------------------------------------- #
# vendoring
# --------------------------------------------------------------------------- #
def vendor():
    vdir = OUT / "assets" / "vendor"
    vdir.mkdir(parents=True, exist_ok=True)
    for name, url in VENDOR.items():
        dest = vdir / name
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        try:
            print(f"  vendoring {name} …")
            req = urllib.request.Request(url, headers={"User-Agent": "codex-build"})
            with urllib.request.urlopen(req, timeout=30) as r:
                dest.write_bytes(r.read())
        except Exception as e:  # offline / blocked — site still works without it
            print(f"    ! could not fetch {name}: {e}")


def copy_assets():
    import shutil

    adir = OUT / "assets"
    (adir / "css").mkdir(parents=True, exist_ok=True)
    (adir / "js").mkdir(parents=True, exist_ok=True)
    shutil.copy(ASSETS_SRC / "css" / "styles.css", adir / "css" / "styles.css")
    shutil.copy(ASSETS_SRC / "js" / "app.js", adir / "js" / "app.js")
    for sub in ("lottie", "svg"):
        s = ASSETS_SRC / sub
        if s.exists():
            d = adir / sub
            if d.exists():
                shutil.rmtree(d)
            shutil.copytree(s, d)
    # pygments stylesheet
    css = HtmlFormatter(style="monokai", cssclass="codehl").get_style_defs(".codehl")
    (adir / "css" / "pygments.css").write_text(css, encoding="utf-8")


# --------------------------------------------------------------------------- #
# HTML shell
# --------------------------------------------------------------------------- #
def head(title: str, depth: int) -> str:
    base = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="An interactive, end-to-end course on JSON Web Tokens and the cryptography behind PyJWT.">
<link rel="icon" href="{base}assets/svg/logo.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/css/pygments.css">
<link rel="stylesheet" href="{base}assets/css/styles.css">
</head>
<body>
<div class="bg-canvas"></div>
<canvas id="stars"></canvas>
"""


def sidebar(modules: list[dict], active: str, depth: int) -> str:
    base = "../" * depth
    links = []
    for mod in modules:
        cls = " class=\"active\"" if mod["slug"] == active else ""
        links.append(
            f'<a href="{base}m/{mod["slug"]}.html"{cls}>'
            f'<span class="num">{mod["num"]}</span>{html.escape(mod["title"])}</a>'
        )
    nav = "\n".join(links)
    home_active = " class=\"active\"" if active == "home" else ""
    pg_active = " class=\"active\"" if active == "playground" else ""
    return f"""<aside class="sidebar">
  <a class="brand" href="{base}index.html">
    <img src="{base}assets/svg/logo.svg" alt="logo">
    <span style="line-height:1.1"><b>PyJWT Codex</b><span>Interactive course</span></span>
  </a>
  <nav class="nav">
    <a href="{base}index.html"{home_active}><span class="num">⌂</span>Home</a>
    <a href="{base}playground.html"{pg_active}><span class="num">▶</span>Playground</a>
    <div class="nav-group-title">Modules</div>
    {nav}
  </nav>
</aside>"""


def topbar(crumb: str) -> str:
    return f"""<div class="topbar">
  <div style="display:flex;align-items:center;gap:14px">
    <button class="menu-btn" aria-label="menu">☰</button>
    <div class="crumb">{crumb}</div>
  </div>
  <a class="crumb" href="https://pyjwt.readthedocs.io/" target="_blank" rel="noopener">PyJWT 2.13 ↗</a>
  <div class="progress-rail"><div class="progress-bar"></div></div>
</div>"""


def scripts(depth: int) -> str:
    base = "../" * depth
    return f"""<script src="{base}assets/vendor/mermaid.min.js"></script>
<script src="{base}assets/vendor/lottie.min.js"></script>
<script src="{base}assets/js/app.js"></script>
</body></html>"""


def page(title, crumb, body, modules, active, depth):
    return (head(title, depth) + '<div class="layout">' + sidebar(modules, active, depth)
            + '<main class="content">' + topbar(crumb)
            + '<div class="container">' + body + footer() + "</div></main></div>"
            + scripts(depth))


def footer():
    return (f'<footer class="footer">The PyJWT Codex · {YEAR} · 16 modules · 118 verified examples · '
            f'built locally with <code>uv</code>, zero npm. Tokens are <b>signed, not encrypted</b> — '
            f'never put secrets in a payload.</footer>')


# --------------------------------------------------------------------------- #
# build module pages
# --------------------------------------------------------------------------- #
def build_module(folder: Path, meta: dict, accent, modules, idx, cache) -> None:
    readme_html = md_to_html(read(folder / "README.md"))
    site_md = read(folder / "_site.md")
    mental_html = md_to_html(site_md) if site_md.strip() else ""

    scripts_paths = sorted(folder.glob("[0-9][0-9]_*.py"))
    examples = []
    for sp in scripts_paths:
        src = read(sp)
        doc = get_docstring(src)
        out = run_script(sp, cache)
        stem = sp.stem
        examples.append({
            "id": f"ex-{stem}", "file": sp.name, "stem": stem,
            "title": nice_title(stem),
            "explain": docstring_to_html(doc),
            "code": highlight_py(src),
            "output": html.escape(out) if out else "(no stdout)",
            "cmd": f"uv run python {sp.relative_to(REPO)}",
        })

    ex_html = []
    for i, e in enumerate(examples):
        open_attr = " open" if i == 0 else ""
        ex_html.append(f"""
<details class="example reveal" id="{e['id']}"{open_attr}>
  <summary>
    <span class="ix">{e['file'][:2]}</span>
    <span class="meta"><b>{html.escape(e['title'])}</b><span>{html.escape(e['file'])}</span></span>
    <span class="chev">▾</span>
  </summary>
  <div class="body">
    <div class="explain">{e['explain'] or '<p>Run it and read along.</p>'}</div>
    <div class="tabwrap">
      <div class="tabs">
        <button class="tab active" data-pane="explain-{i}">▶ Output</button>
        <button class="tab" data-pane="code-{i}">&lt;/&gt; Code</button>
        <button class="tab" data-pane="cmd-{i}">$ Run</button>
      </div>
      <div class="pane active" data-pane="explain-{i}">
        <div class="terminal"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="t">output · {html.escape(e['file'])}</span></div><pre>{e['output']}</pre></div>
      </div>
      <div class="pane" data-pane="code-{i}">
        <div class="codewin"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">{html.escape(e['file'])}</span><button class="copy">copy</button></div>{e['code']}</div>
      </div>
      <div class="pane" data-pane="cmd-{i}">
        <div class="codewin"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">terminal</span><button class="copy">copy</button></div><pre><span class="seg-s">$</span> {html.escape(e['cmd'])}</pre></div>
      </div>
    </div>
  </div>
</details>""")

    mental_section = (f'<section class="mental reveal">{mental_html}</section>'
                      if mental_html else "")

    prev_link = next_link = ""
    if idx > 0:
        p = modules[idx - 1]
        prev_link = (f'<a class="prev" href="{p["slug"]}.html"><div class="dir">← Previous</div>'
                     f'<div class="ttl">{p["num"]} · {html.escape(p["title"])}</div></a>')
    else:
        prev_link = '<a class="prev" href="../index.html"><div class="dir">← Back</div><div class="ttl">Home</div></a>'
    if idx < len(modules) - 1:
        n = modules[idx + 1]
        next_link = (f'<a class="next" href="{n["slug"]}.html"><div class="dir">Next →</div>'
                     f'<div class="ttl">{n["num"]} · {html.escape(n["title"])}</div></a>')
    else:
        next_link = '<a class="next" href="../playground.html"><div class="dir">Next →</div><div class="ttl">▶ Playground</div></a>'

    body = f"""
<style>:root{{--accent:linear-gradient(90deg,{accent[0]},{accent[1]})}}</style>
<section class="hero" style="padding-bottom:8px">
  <span class="eyebrow" style="color:{accent[0]};border-color:{accent[0]}55;background:{accent[0]}11">Module {meta['num']}</span>
  <h1 style="margin-top:18px">{html.escape(meta['title'])}</h1>
</section>
{mental_section}
<section class="prose reveal">{readme_html}</section>
<h2 id="examples">🧪 Hands-on examples <span style="color:var(--faint);font-size:1rem;font-weight:500">· {len(examples)} runnable scripts</span></h2>
<p style="color:var(--muted)">Every script below was executed locally with <code>uv run</code>; the
<b>Output</b> tab shows its real, captured result. Open the <b>Code</b> tab to read the
fully-commented source.</p>
{''.join(ex_html)}
<nav class="pager">{prev_link}{next_link}</nav>
"""
    crumb = f'<a href="../index.html">Home</a> &nbsp;/&nbsp; <b>{meta["num"]} · {html.escape(meta["title"])}</b>'
    (OUT / "m").mkdir(parents=True, exist_ok=True)
    out_html = page(f'{meta["title"]} · PyJWT Codex', crumb, body, modules, meta["slug"], depth=1)
    (OUT / "m" / f'{meta["slug"]}.html').write_text(out_html, encoding="utf-8")


# --------------------------------------------------------------------------- #
# landing page
# --------------------------------------------------------------------------- #
def build_index(modules, accents_by_slug, totals):
    cards = []
    for mod in modules:
        a = accents_by_slug[mod["slug"]]
        cards.append(f"""
<a class="card reveal" href="m/{mod['slug']}.html" style="--accent:linear-gradient(90deg,{a[0]},{a[1]})">
  <div class="kicker">Module {mod['num']}</div>
  <h3>{html.escape(mod['title'])}</h3>
  <p>{html.escape(mod['blurb'])}</p>
  <div class="chips"><span class="chip">{mod['n']} examples</span></div>
</a>""")

    path = """flowchart TD
  A["01 · Foundations"] --> B["02 · HS256 Basics"] --> C["03 · Registered Claims"]
  C --> D["04 · Custom Claims"] --> E["05 · HMAC"] --> F["06 · RSA"]
  F --> G["07 · ECDSA"] --> H["08 · RSA-PSS"] --> I["09 · EdDSA"]
  I --> J["10 · Headers & kid"] --> K["11 · JWKS & Rotation"] --> L["12 · Errors"]
  L --> M["13 · Cryptography"] --> N["14 · Security"] --> O["15 · Real-World"]
  O --> P["16 · Local IdP"]"""

    body = f"""
<section class="hero">
  <div class="hero-grid">
    <div>
      <span class="eyebrow">🔐 Signed, not encrypted</span>
      <h1 style="margin-top:18px">The <span class="gradient-text">PyJWT Codex</span></h1>
      <p class="lead">Learn JSON Web Tokens end-to-end — from the raw base64url bytes of a
      token to production OAuth2 / OIDC — with a deep, visual dive into the cryptography
      that makes it all work. <b>{totals['examples']} runnable, verified examples.</b></p>
      <div class="btn-row">
        <a class="btn btn-primary" href="m/{modules[0]['slug']}.html">Start the course →</a>
        <a class="btn btn-ghost" href="playground.html">▶ Open the JWT Playground</a>
      </div>
    </div>
    <div><div class="hero-lottie" data-lottie="assets/lottie/hero-shield.json" style="height:360px"></div></div>
  </div>
</section>

<section class="stats">
  <div class="stat reveal"><div class="n gradient-text">16</div><div class="l">Modules</div></div>
  <div class="stat reveal"><div class="n gradient-text">{totals['examples']}</div><div class="l">Examples</div></div>
  <div class="stat reveal"><div class="n gradient-text">5</div><div class="l">Algo families</div></div>
  <div class="stat reveal"><div class="n gradient-text">0</div><div class="l">npm deps</div></div>
</section>

<figure class="figure reveal"><img src="assets/svg/jwt-structure.svg" alt="JWT structure" style="max-width:680px">
<figcaption>A JWT is three base64url segments — <b style="color:var(--cyan)">header</b>.<b style="color:var(--violet)">payload</b>.<b style="color:var(--emerald)">signature</b> — joined by dots.</figcaption></figure>

<h2>🗺️ Your learning path</h2>
<div class="mermaid-wrap reveal"><div class="mermaid">{path}</div></div>

<h2>📚 All modules</h2>
<div class="grid">{''.join(cards)}</div>

<h2>🎨 Concepts, visualised</h2>
<div class="grid">
  <figure class="figure reveal"><img src="assets/svg/sign-verify-flow.svg" alt="sign and verify"><figcaption>Sign with the private key, verify with the public key.</figcaption></figure>
  <figure class="figure reveal"><img src="assets/svg/sym-vs-asym.svg" alt="symmetric vs asymmetric"><figcaption>Shared-secret (HMAC) vs. public/private keypairs.</figcaption></figure>
  <figure class="figure reveal"><img src="assets/svg/algorithm-families.svg" alt="algorithm families"><figcaption>The five signing families covered in this course.</figcaption></figure>
  <figure class="figure reveal"><img src="assets/svg/key-rotation.svg" alt="key rotation"><figcaption>A token's <code>kid</code> selects the matching key from a JWKS.</figcaption></figure>
</div>
"""
    crumb = "<b>Home</b>"
    (OUT / "index.html").write_text(
        page("The PyJWT Codex — Interactive JWT & Cryptography Course", crumb, body,
             modules, "home", depth=0), encoding="utf-8")


# --------------------------------------------------------------------------- #
# playground
# --------------------------------------------------------------------------- #
def build_playground(modules):
    sample = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtleS0xIn0."
              "eyJzdWIiOiJhbGljZSIsIm5hbWUiOiJBbGljZSBFeGFtcGxlIiwic2NvcGUiOiJyZWFkIHdyaXRlIiwicm9sZSI6ImFkbWluIiwiaXNzIjoiaHR0cHM6Ly9jb2RleC5sb2NhbCIsImF1ZCI6ImFwaTovL2NvZGV4IiwiaWF0IjoxNzAwMDAwMDAwLCJleHAiOjQwMDAwMDAwMDB9."
              "QFnX0n7iJYz3l3oS3Y0m2t8Yy0aQ2m0r2k7m1m0sJ0")
    body = f"""
<section class="hero" style="padding-bottom:8px">
  <span class="eyebrow">▶ Interactive</span>
  <h1 style="margin-top:18px">JWT <span class="gradient-text">Playground</span></h1>
  <p class="lead">Paste any JWT to decode it instantly in your browser — no token ever
  leaves this page. For <code>HS256/384/512</code> tokens you can also test a secret and
  watch the signature verify live via the Web Crypto API.</p>
</section>

<div class="pg-grid">
  <div class="pg-card reveal">
    <h3>1 · Paste a token</h3>
    <textarea id="token-in" class="token-in" spellcheck="false">{sample}</textarea>
    <h3 style="margin-top:18px">2 · Test an HMAC secret <span style="font-weight:500;color:var(--faint);font-size:.8rem">(HS* only)</span></h3>
    <input id="secret-in" class="secret-in" placeholder="shared secret…" spellcheck="false">
    <div id="verify-status" style="margin-top:12px"></div>
  </div>
  <div class="pg-card reveal">
    <h3>Decoded</h3>
    <div id="dec-status" style="margin-bottom:12px"></div>
    <div id="jwt-viz" class="jwt-viz"></div>
    <div id="dec-header" style="margin-top:16px"></div>
    <div id="dec-payload" style="margin-top:14px"></div>
  </div>
</div>

<h2>How decoding works</h2>
<p style="color:var(--muted)">The header and payload are just base64url-encoded JSON — readable by anyone.
That is why a JWT is <b>signed, not encrypted</b>. Only the signature requires a key, and only
to <em>verify</em> integrity (or, for HMAC, to also re-create it).</p>
<figure class="figure reveal"><img src="assets/svg/jwt-structure.svg" alt="jwt structure" style="max-width:640px"></figure>
"""
    crumb = '<a href="index.html">Home</a> &nbsp;/&nbsp; <b>Playground</b>'
    (OUT / "playground.html").write_text(
        page("JWT Playground · PyJWT Codex", crumb, body, modules, "playground", depth=0),
        encoding="utf-8")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
BLURBS = {
    "01": "Decode a token by hand: base64url, the three segments, and why JWTs are readable.",
    "02": "Your first encode/decode with HS256 — secrets, round-trips, str vs bytes.",
    "03": "The seven registered claims: iss, sub, aud, exp, nbf, iat, jti.",
    "04": "Custom claims plus the decode() control surface: options, require, leeway.",
    "05": "Symmetric HMAC signing — HS256 / HS384 / HS512 and the shared-secret model.",
    "06": "Asymmetric RSA — RS256/384/512, keypairs, and private-signs/public-verifies.",
    "07": "Elliptic-curve ECDSA — ES256/384/512/256K and the curve-to-algorithm binding.",
    "08": "Probabilistic RSA-PSS — PS256/384/512 and randomised signatures.",
    "09": "Modern EdDSA — Ed25519 / Ed448, deterministic and tiny.",
    "10": "The JOSE header, custom headers, and how kid drives key selection.",
    "11": "JWKS, the JWK format, PyJWKClient, and zero-downtime key rotation.",
    "12": "The exception hierarchy, leeway for clock skew, and robust validation.",
    "13": "Cryptography from primitives: hashing, HMAC, signatures, key formats.",
    "14": "alg=none, algorithm confusion, and the JWT security checklist.",
    "15": "FastAPI auth, access/refresh tokens, scopes, and OIDC validation.",
    "16": "A fully local OAuth2/OIDC identity provider — no Azure required.",
}


def main():
    folders = sorted(p for p in COURSE.iterdir()
                     if p.is_dir() and re.match(r"\d\d-", p.name))
    modules = []
    accents_by_slug = {}
    for i, folder in enumerate(folders):
        meta = module_meta(folder)
        meta["n"] = len(list(folder.glob("[0-9][0-9]_*.py")))
        meta["blurb"] = BLURBS.get(meta["num"], "")
        modules.append(meta)
        accents_by_slug[meta["slug"]] = ACCENTS[i % len(ACCENTS)]

    print(f"› {len(modules)} modules found")
    OUT.mkdir(exist_ok=True)
    copy_assets()
    vendor()

    cache = load_cache()
    total_examples = 0
    for i, folder in enumerate(folders):
        meta = modules[i]
        print(f"  building {meta['slug']} ({meta['n']} scripts)")
        build_module(folder, meta, accents_by_slug[meta["slug"]], modules, i, cache)
        total_examples += meta["n"]

    (CACHE / "outputs.json").write_text(json.dumps(cache), encoding="utf-8")
    build_index(modules, accents_by_slug, {"examples": total_examples})
    build_playground(modules)
    print(f"✓ built site → {OUT}  ({total_examples} examples across {len(modules)} modules)")


if __name__ == "__main__":
    main()
