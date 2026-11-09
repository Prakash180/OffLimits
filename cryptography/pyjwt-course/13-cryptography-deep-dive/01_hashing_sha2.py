"""
01 · Hashing with SHA-2 — the foundation under every JWT signature
===================================================================

A *cryptographic hash function* takes an input of ANY size and produces a
fixed-size "digest". JWTs lean on the SHA-2 family (SHA-256/384/512): the "256"
in ``HS256`` / ``RS256`` / ``ES256`` literally means "SHA-256".

Three properties we demonstrate below:

1. **One-way (preimage resistance)** — given a digest you cannot feasibly
   recover the input. Hashing is NOT encryption; there is no "unhash".
2. **Fixed output size** — a 3-byte input and a 3-megabyte input both produce a
   256-bit (32-byte / 64 hex-char) digest for SHA-256.
3. **Avalanche effect** — flipping a single character changes ~half the output
   bits, producing a totally different-looking digest.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/01_hashing_sha2.py
"""

import hashlib


def digest(algorithm: str, data: str) -> str:
    """Return the hex digest of ``data`` using the named SHA-2 algorithm."""
    h = hashlib.new(algorithm)
    h.update(data.encode("utf-8"))
    return h.hexdigest()


def hamming_distance_hex(a: str, b: str) -> int:
    """Count how many *bits* differ between two equal-length hex digests."""
    a_int = int(a, 16)
    b_int = int(b, 16)
    return bin(a_int ^ b_int).count("1")


def main() -> None:
    print("=" * 70)
    print("SHA-2 DIGESTS OF THE SAME MESSAGE")
    print("=" * 70)
    message = "The quick brown fox jumps over the lazy dog"
    print(f"Message: {message!r}\n")

    for algorithm in ("sha256", "sha384", "sha512"):
        d = digest(algorithm, message)
        # Output is fixed size regardless of input length.
        print(f"{algorithm.upper():8} -> {d}")
        print(f"{'':8}    ({len(d) * 4} bits, {len(d)} hex chars)\n")

    print("=" * 70)
    print("FIXED OUTPUT SIZE — tiny vs huge input, same digest length")
    print("=" * 70)
    tiny = "hi"
    huge = "A" * 3_000_000  # ~3 MB of data
    tiny_d = digest("sha256", tiny)
    huge_d = digest("sha256", huge)
    print(f"SHA-256 of {len(tiny)}-byte input        -> {tiny_d} ({len(tiny_d)} hex)")
    print(f"SHA-256 of {len(huge):,}-byte input -> {huge_d} ({len(huge_d)} hex)")
    print("Both digests are exactly 64 hex chars. Size in, fixed size out.\n")

    print("=" * 70)
    print("AVALANCHE EFFECT — change one character, get a new universe")
    print("=" * 70)
    original = "Attack at dawn"
    tampered = "Attack at dusk"  # changed 'aw' -> 'us' (a couple of chars)
    od = digest("sha256", original)
    td = digest("sha256", tampered)
    bits_changed = hamming_distance_hex(od, td)
    total_bits = len(od) * 4
    print(f"Original: {original!r}")
    print(f"  -> {od}")
    print(f"Tampered: {tampered!r}")
    print(f"  -> {td}")
    print(
        f"\nBits changed: {bits_changed}/{total_bits} "
        f"(~{bits_changed / total_bits:.0%}). A small input change "
        f"scrambles half the output."
    )

    print("\n" + "=" * 70)
    print("ONE-WAY: there is no hashlib.unsha256(). You cannot reverse a digest.")
    print("This integrity property is exactly what JWT signatures are built on.")
    print("=" * 70)


if __name__ == "__main__":
    main()
