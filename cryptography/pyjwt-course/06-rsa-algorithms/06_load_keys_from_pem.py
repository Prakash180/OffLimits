"""06_load_keys_from_pem.py — Serialize keys to PEM and load them back.

In the real world your keys live OUTSIDE your program — in files, secret
managers, or environment variables — as PEM text. This script shows the full
round trip:

  1. Generate a keypair.
  2. Serialize to PEM (private = PKCS#8, public = SubjectPublicKeyInfo).
  3. Write the PEMs to temporary files (tempfile).
  4. Read them back and re-parse with
     serialization.load_pem_private_key / load_pem_public_key.
  5. Use the loaded keys with PyJWT.

PyJWT can also take the raw PEM bytes directly; we demonstrate that too.
"""

import os
import tempfile

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# --- 1) Generate + 2) serialize -----------------------------------------
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# --- 3) Write the PEMs to temporary files --------------------------------
tmpdir = tempfile.mkdtemp(prefix="jwt-keys-")
priv_path = os.path.join(tmpdir, "private.pem")
pub_path = os.path.join(tmpdir, "public.pem")
with open(priv_path, "wb") as fh:
    fh.write(private_pem)
with open(pub_path, "wb") as fh:
    fh.write(public_pem)
print("Wrote PEM files to:")
print(" ", priv_path)
print(" ", pub_path, "\n")

# --- 4) Load them back into key objects ----------------------------------
with open(priv_path, "rb") as fh:
    loaded_private = serialization.load_pem_private_key(fh.read(), password=None)
with open(pub_path, "rb") as fh:
    loaded_public = serialization.load_pem_public_key(fh.read())
print("Reloaded key objects:")
print("  private:", type(loaded_private).__name__)
print("  public :", type(loaded_public).__name__, "\n")

# --- 5a) Use the LOADED key objects with PyJWT ---------------------------
token = jwt.encode({"sub": "from-loaded-keys"}, loaded_private, algorithm="RS256")
print("Signed with loaded private key:")
print(" ", jwt.decode(token, loaded_public, algorithms=["RS256"]), "\n")

# --- 5b) Hand the raw PEM bytes straight to PyJWT ------------------------
# PyJWT parses PEM strings/bytes for you, so files aren't strictly required.
token2 = jwt.encode({"sub": "from-raw-pem"}, private_pem, algorithm="RS256")
print("Signed using raw PEM bytes directly:")
print(" ", jwt.decode(token2, public_pem, algorithms=["RS256"]))

# --- Cleanup -------------------------------------------------------------
os.remove(priv_path)
os.remove(pub_path)
os.rmdir(tmpdir)
print("\nTemporary key files cleaned up.")
