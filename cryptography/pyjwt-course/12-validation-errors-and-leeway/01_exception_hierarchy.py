"""01 · The PyJWT exception hierarchy.

When validation fails, PyJWT raises a *specific* exception — and those exceptions
form a tidy inheritance tree. Knowing the tree lets you catch broadly
(``PyJWTError`` for "anything JWT went wrong") or narrowly
(``ExpiredSignatureError`` for "just this case").

The hierarchy (rooted at ``PyJWTError``):

    PyJWTError
    └── InvalidTokenError
        ├── DecodeError
        │   └── InvalidSignatureError
        ├── ExpiredSignatureError
        ├── InvalidAudienceError
        ├── InvalidIssuerError
        ├── InvalidIssuedAtError
        ├── ImmatureSignatureError        (nbf in the future)
        ├── InvalidKeyError
        ├── InvalidAlgorithmError
        └── MissingRequiredClaimError

Because almost everything subclasses ``InvalidTokenError``, a single
``except InvalidTokenError`` is a safe catch-all for "reject this token", while
``except PyJWTError`` also covers encoding-side problems.

This script uses ``inspect`` to print each class's Method Resolution Order (MRO),
which *is* its ancestry chain.

Run:
    /home/astro/catalyst/jwt-test/.venv/bin/python \
        pyjwt-course/12-validation-errors-and-leeway/01_exception_hierarchy.py
"""

import inspect

import jwt.exceptions as exc

# The classes we want to map, in a sensible teaching order.
CLASSES = [
    exc.PyJWTError,
    exc.InvalidTokenError,
    exc.DecodeError,
    exc.InvalidSignatureError,
    exc.ExpiredSignatureError,
    exc.InvalidAudienceError,
    exc.InvalidIssuerError,
    exc.ImmatureSignatureError,
    exc.MissingRequiredClaimError,
    exc.InvalidAlgorithmError,
    exc.InvalidKeyError,
]


def main() -> None:
    print("PyJWT exception ancestry (each line = class -> its base classes):")
    print()
    for cls in CLASSES:
        # MRO without 'object' and the class itself = its real ancestors.
        ancestors = [c.__name__ for c in inspect.getmro(cls) if c not in (cls, object)]
        chain = " -> ".join(ancestors) if ancestors else "(root)"
        print(f"  {cls.__name__:<25} : {chain}")
    print()

    # Demonstrate the practical payoff: broad vs. narrow catching.
    print("Subclass checks (why catch-alls work):")
    print(f"  ExpiredSignatureError is an InvalidTokenError? "
          f"{issubclass(exc.ExpiredSignatureError, exc.InvalidTokenError)}")
    print(f"  InvalidSignatureError is a DecodeError?        "
          f"{issubclass(exc.InvalidSignatureError, exc.DecodeError)}")
    print(f"  Every error is a PyJWTError?                   "
          f"{all(issubclass(c, exc.PyJWTError) for c in CLASSES)}")
    print()
    print("✅ Catch InvalidTokenError to reject any bad token; subclasses for detail.")


if __name__ == "__main__":
    main()
