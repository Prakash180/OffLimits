/* ============================================================================
   The PyJWT Codex — interactions
   ========================================================================== */
(function () {
  "use strict";

  /* ---- starfield canvas --------------------------------------------------- */
  function starfield() {
    var c = document.getElementById("stars");
    if (!c || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    var ctx = c.getContext("2d"), stars = [], DPR = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      c.width = innerWidth * DPR; c.height = innerHeight * DPR;
      c.style.width = innerWidth + "px"; c.style.height = innerHeight + "px";
      stars = [];
      var n = Math.min(150, Math.floor(innerWidth * innerHeight / 14000));
      for (var i = 0; i < n; i++) stars.push({
        x: Math.random() * c.width, y: Math.random() * c.height,
        z: Math.random() * 0.8 + 0.2, r: Math.random() * 1.4 + 0.3,
        hue: Math.random() < 0.5 ? "34,211,238" : "167,139,250"
      });
    }
    function tick() {
      ctx.clearRect(0, 0, c.width, c.height);
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        s.y += s.z * 0.25 * DPR;
        if (s.y > c.height) { s.y = 0; s.x = Math.random() * c.width; }
        ctx.beginPath();
        ctx.fillStyle = "rgba(" + s.hue + "," + (0.15 + s.z * 0.5) + ")";
        ctx.arc(s.x, s.y, s.r * DPR, 0, 7);
        ctx.fill();
      }
      requestAnimationFrame(tick);
    }
    addEventListener("resize", resize); resize(); tick();
  }

  /* ---- lottie animations -------------------------------------------------- */
  function lottie() {
    if (!window.lottie) return;
    document.querySelectorAll("[data-lottie]").forEach(function (el) {
      try {
        window.lottie.loadAnimation({
          container: el, renderer: "svg", loop: true, autoplay: true,
          path: el.getAttribute("data-lottie")
        });
      } catch (e) {}
    });
  }

  /* ---- mermaid ------------------------------------------------------------ */
  function mermaidInit() {
    if (!window.mermaid) return;
    try {
      window.mermaid.initialize({
        startOnLoad: false, securityLevel: "loose",
        theme: "base",
        themeVariables: {
          background: "transparent", primaryColor: "#13203a",
          primaryTextColor: "#e6ecf5", primaryBorderColor: "#22d3ee",
          lineColor: "#a78bfa", secondaryColor: "#1b1340", tertiaryColor: "#0f172a",
          fontFamily: "Inter, system-ui, sans-serif", fontSize: "14px",
          actorBkg: "#13203a", actorBorder: "#22d3ee", actorTextColor: "#e6ecf5",
          signalColor: "#a78bfa", signalTextColor: "#c7d2e8", noteBkgColor: "#1b1340", noteTextColor: "#e6ecf5"
        }
      });
      window.mermaid.run({ querySelector: ".mermaid" });
    } catch (e) {}
  }

  /* ---- copy buttons ------------------------------------------------------- */
  function copyButtons() {
    document.querySelectorAll(".copy").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var pre = btn.closest(".codewin").querySelector("pre");
        navigator.clipboard.writeText(pre.innerText).then(function () {
          var old = btn.textContent; btn.textContent = "✓ copied";
          setTimeout(function () { btn.textContent = old; }, 1400);
        });
      });
    });
  }

  /* ---- example tabs ------------------------------------------------------- */
  function tabs() {
    document.querySelectorAll(".tabs").forEach(function (group) {
      group.addEventListener("click", function (e) {
        var tab = e.target.closest(".tab"); if (!tab) return;
        var wrap = group.parentElement, name = tab.dataset.pane;
        group.querySelectorAll(".tab").forEach(function (t) { t.classList.toggle("active", t === tab); });
        wrap.querySelectorAll(":scope > .pane").forEach(function (p) {
          p.classList.toggle("active", p.dataset.pane === name);
        });
      });
    });
  }

  /* ---- scroll reveal ------------------------------------------------------ */
  function reveal() {
    var els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) { els.forEach(function (e) { e.classList.add("in"); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.08 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* ---- top progress + active nav ------------------------------------------ */
  function progress() {
    var bar = document.querySelector(".progress-bar");
    function onScroll() {
      if (bar) {
        var h = document.documentElement.scrollHeight - innerHeight;
        bar.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + "%";
      }
    }
    addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  /* ---- mobile sidebar ----------------------------------------------------- */
  function mobileNav() {
    var btn = document.querySelector(".menu-btn"), sb = document.querySelector(".sidebar");
    if (!btn || !sb) return;
    btn.addEventListener("click", function () { sb.classList.toggle("open"); });
    sb.addEventListener("click", function (e) { if (e.target.tagName === "A") sb.classList.remove("open"); });
  }

  /* ---- JWT decoder (playground) ------------------------------------------- */
  function b64urlToStr(seg) {
    seg = seg.replace(/-/g, "+").replace(/_/g, "/");
    while (seg.length % 4) seg += "=";
    try { return decodeURIComponent(escape(atob(seg))); } catch (e) { return atob(seg); }
  }
  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); }

  function decoder() {
    var input = document.getElementById("token-in");
    if (!input) return;
    var vizEl = document.getElementById("jwt-viz"),
        headEl = document.getElementById("dec-header"),
        payEl = document.getElementById("dec-payload"),
        statusEl = document.getElementById("dec-status"),
        secretEl = document.getElementById("secret-in"),
        verifyEl = document.getElementById("verify-status");

    function kvTable(obj) {
      var rows = "", well = { iss: "issuer", sub: "subject", aud: "audience", exp: "expires", nbf: "not before", iat: "issued at", jti: "JWT id", alg: "algorithm", typ: "type", kid: "key id", scope: "scope", nonce: "nonce" };
      Object.keys(obj).forEach(function (k) {
        var v = obj[k], extra = "";
        if (["exp", "nbf", "iat"].indexOf(k) >= 0 && typeof v === "number") {
          var d = new Date(v * 1000); extra = ' <span class="seg-d">// ' + d.toUTCString() + "</span>";
        }
        rows += '<div class="k" title="' + (well[k] || "") + '">' + esc(k) + '</div><div class="v">' + esc(typeof v === "object" ? JSON.stringify(v) : v) + extra + "</div>";
      });
      return '<div class="kv">' + rows + "</div>";
    }

    function render() {
      var t = input.value.trim();
      if (!t) { vizEl.innerHTML = '<span class="seg-d">paste a token above…</span>'; headEl.innerHTML = payEl.innerHTML = ""; statusEl.innerHTML = ""; verifyEl.innerHTML = ""; return; }
      var parts = t.split(".");
      if (parts.length < 2) { statusEl.innerHTML = '<span class="badge bad">Not a JWT — need at least header.payload</span>'; return; }
      vizEl.innerHTML = '<span class="seg-h">' + esc(parts[0]) + '</span><span class="seg-d">.</span><span class="seg-p">' + esc(parts[1]) + '</span>' + (parts[2] !== undefined ? '<span class="seg-d">.</span><span class="seg-s">' + esc(parts[2]) + "</span>" : "");
      var head, pay;
      try { head = JSON.parse(b64urlToStr(parts[0])); } catch (e) { statusEl.innerHTML = '<span class="badge bad">Header is not valid JSON</span>'; return; }
      try { pay = JSON.parse(b64urlToStr(parts[1])); } catch (e) { statusEl.innerHTML = '<span class="badge bad">Payload is not valid JSON</span>'; return; }
      headEl.innerHTML = "<h4>🔵 Header</h4>" + kvTable(head);
      payEl.innerHTML = "<h4>🟣 Payload</h4>" + kvTable(pay);

      var msgs = [];
      if (pay.exp) {
        var now = Date.now() / 1000;
        msgs.push(pay.exp < now ? '<span class="badge bad">⌛ expired</span>' : '<span class="badge ok">valid for ' + Math.round((pay.exp - now) / 60) + " min</span>");
      }
      msgs.push('<span class="badge warn">alg: ' + esc(head.alg || "?") + "</span>");
      statusEl.innerHTML = msgs.join(" ");
      verifyHS(parts, head);
    }

    function verifyHS(parts, head) {
      verifyEl.innerHTML = "";
      var secret = secretEl ? secretEl.value : "";
      if (!secret || !/^HS(256|384|512)$/.test(head.alg || "") || parts.length < 3 || !window.crypto || !crypto.subtle) {
        if (secret && head.alg && head.alg.indexOf("HS") !== 0) verifyEl.innerHTML = '<span class="seg-d">Browser verify supports HS256/384/512 only. ' + esc(head.alg) + " uses public-key crypto.</span>";
        return;
      }
      var hashName = "SHA-" + head.alg.slice(2);
      var enc = new TextEncoder();
      crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: hashName }, false, ["sign"])
        .then(function (key) { return crypto.subtle.sign("HMAC", key, enc.encode(parts[0] + "." + parts[1])); })
        .then(function (sig) {
          var b = new Uint8Array(sig), s = "";
          for (var i = 0; i < b.length; i++) s += String.fromCharCode(b[i]);
          var b64 = btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
          verifyEl.innerHTML = b64 === parts[2]
            ? '<span class="badge ok">✓ signature verified with this secret</span>'
            : '<span class="badge bad">✗ signature does NOT match this secret</span>';
        }).catch(function () {});
    }

    input.addEventListener("input", render);
    if (secretEl) secretEl.addEventListener("input", render);
    render();
  }

  /* ---- boot --------------------------------------------------------------- */
  function boot() {
    starfield(); lottie(); mermaidInit(); copyButtons(); tabs();
    reveal(); progress(); mobileNav(); decoder();
  }
  if (document.readyState !== "loading") boot();
  else document.addEventListener("DOMContentLoaded", boot);
})();
