"""
06 · Public-key intuition — trapdoor functions & why you can publish a key
===========================================================================

Why is it *safe* to hand your public key to the entire internet?

Because asymmetric crypto is built on **trapdoor functions**: math that is easy
to compute one way but infeasible to reverse without a secret "trapdoor".

* **RSA** rests on *integer factorisation*. Multiplying two 1024-bit primes is
  instant; factoring the 2048-bit product back into those primes is infeasible.
  The public key reveals the product; the private key IS the factors.

* **ECDSA / EdDSA** rest on the *elliptic-curve discrete log problem*. Computing
  ``Q = d · G`` (a point multiplied by a scalar) is easy; recovering the scalar
  ``d`` from ``Q`` and ``G`` is infeasible. The public key is the point ``Q``;
  the private key is the scalar ``d``.

So a public key is a "padlock you can mass-produce": anyone can snap it shut
(verify), only the trapdoor holder can have produced what fits (sign).

This script keeps it conceptual + tiny demos.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/13-cryptography-deep-dive/06_public_key_crypto_intuition.py
"""

from cryptography.hazmat.primitives.asymmetric import ec, rsa


def main() -> None:
    print("=" * 70)
    print("TRAPDOOR #1 — RSA & integer factorisation (toy demo with small primes)")
    print("=" * 70)
    # Real RSA uses ~1024-bit primes; these tiny ones just illustrate the idea.
    p, q = 61, 53
    n = p * q  # public-ish: easy to compute
    print(f"pick two primes p={p}, q={q}  (PRIVATE)")
    print(f"publish their product n = p*q = {n}  (PUBLIC)")
    print(f"easy forward : {p} * {q} = {n}")
    print("hard reverse : given only n, find p and q.")
    print("At 2048 bits, that reverse would take longer than the age of the")
    print("universe on all computers on Earth — that's the trapdoor.\n")

    print("=" * 70)
    print("TRAPDOOR #2 — Elliptic curves & the discrete log problem")
    print("=" * 70)
    print("private key d : a random scalar (a big secret number)")
    print("public  key Q : the curve point Q = d · G  (G is a fixed base point)")
    print("easy forward  : multiply the point G by d to get Q")
    print("hard reverse  : recover d from Q and G (elliptic-curve discrete log)\n")

    print("=" * 70)
    print("REAL KEYS — one-liners with the cryptography library")
    print("=" * 70)
    # RSA: factorisation-based.
    rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    rsa_numbers = rsa_key.public_key().public_numbers()
    print(f"RSA-2048 public modulus n has {rsa_numbers.n.bit_length()} bits")
    print(f"RSA public exponent e = {rsa_numbers.e}")

    # ECDSA: discrete-log-based. P-256 is the curve behind ES256.
    ec_key = ec.generate_private_key(ec.SECP256R1())
    ec_pub = ec_key.public_key().public_numbers()
    print("\nECDSA P-256 (ES256) public point:")
    print(f"  x = {hex(ec_pub.x)[:34]}... ({ec_pub.x.bit_length()} bits)")
    print(f"  y = {hex(ec_pub.y)[:34]}... ({ec_pub.y.bit_length()} bits)")

    print("\n" + "=" * 70)
    print("RSA vs. ECDSA — same security, very different sizes")
    print("=" * 70)
    print("RSA-2048  ~ 112-bit security, ~256-byte signatures, ~294-byte pubkey")
    print("EC P-256  ~ 128-bit security, ~64-byte  signatures, ~91-byte  pubkey")
    print("EdDSA     ~ 128-bit security, 64-byte   signatures, deterministic")
    print("\nWhy publish the public key safely? Because reversing the trapdoor")
    print("to recover the private key is computationally infeasible.")


if __name__ == "__main__":
    main()
