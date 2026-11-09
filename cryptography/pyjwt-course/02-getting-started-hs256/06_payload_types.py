"""
06 · Payload value types
========================

A JWT payload is JSON, so claim VALUES must be JSON-serializable. PyJWT happily
accepts the standard JSON types:

  * str, int, float, bool, None
  * list (array) and dict (object), nested as deep as you like

Additionally, for the *date-related registered claims* (exp, nbf, iat), PyJWT
lets you pass a Python `datetime` and converts it to a NumericDate (a Unix
timestamp integer) for you. This script demonstrates both behaviours.
"""

import datetime

import jwt

SECRET = "teaching-secret-at-least-32-bytes-long!!"

print("=" * 60)
print("STANDARD JSON VALUE TYPES IN A PAYLOAD")
print("=" * 60)
payload = {
    "a_string": "hello",
    "an_int": 42,
    "a_float": 3.14,
    "a_bool": True,
    "a_none": None,
    "a_list": [1, 2, "three"],
    "a_dict": {"nested": {"deeply": True}},
}
token = jwt.encode(payload, SECRET, algorithm="HS256")
decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
for key, value in decoded.items():
    print(f"  {key:10} -> {value!r:30} ({type(value).__name__})")
print()
print("Round-trip preserved all types (note: tuples would become lists, since")
print("JSON has no tuple type).")
print()

print("=" * 60)
print("datetime IS CONVERTED FOR DATE CLAIMS (exp, nbf, iat)")
print("=" * 60)
now = datetime.datetime.now(tz=datetime.UTC)
exp = now + datetime.timedelta(hours=1)
date_payload = {
    "user": "alice",
    "iat": now,  # issued-at: pass a datetime...
    "exp": exp,  # expiry: ...and PyJWT stores it as an integer timestamp
}
date_token = jwt.encode(date_payload, SECRET, algorithm="HS256")
date_decoded = jwt.decode(date_token, SECRET, algorithms=["HS256"])
print(f"passed iat as datetime: {now}")
print(f"stored/decoded iat as : {date_decoded['iat']} ({type(date_decoded['iat']).__name__})")
print(f"passed exp as datetime: {exp}")
print(f"stored/decoded exp as : {date_decoded['exp']} ({type(date_decoded['exp']).__name__})")
print()
print("PyJWT converts the datetime to a Unix timestamp (seconds since epoch),")
print("which is the JWT spec's 'NumericDate' format. On decode you get the int")
print("back; PyJWT uses it internally to enforce expiry (covered in module 03).")
