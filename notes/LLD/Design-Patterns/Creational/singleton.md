# Singleton Pattern

> Category: **Creational** (controls how an object is *created* — ensures only one instance ever exists)

## What it is

- Ensures a class has **only one instance** in the whole application, and gives a **global access point** to it.
- **Layman:** There's only one "President" of a country at a time — everyone refers to the same one, nobody creates a new one.

## When to use it

- Shared resource where having multiple instances would cause bugs or waste resources: config managers, logging, connection pools, caches.

## 1) Basic (Lazy, NOT Thread-Safe)

```java
public class Singleton {
    private static Singleton instance;

    private Singleton() { }

    public static Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();   // created only when first needed
        }
        return instance;
    }
}
```

- "Lazy" = the instance is only created the first time `getInstance()` is called, not upfront.
- **Problem:** if two threads call `getInstance()` at the exact same time, both can see `instance == null` and both create a separate object → you end up with two instances. Breaks the whole point of Singleton.

---

## 2) Basic but Thread-Safe (Synchronized Method)

```java
public class Singleton {
    private static Singleton instance;

    private Singleton() { }

    public static synchronized Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}
```

- Adding `synchronized` on the method means only **one thread at a time** can enter `getInstance()` — fixes the race condition.
- **Problem:** every single call is synchronized (locked), even after `instance` is already created. Unnecessary performance cost since locking is only actually needed the *first* time.

---

## 3) Thread-Safe with Double-Checked Locking

```java
public class Singleton {
    private static volatile Singleton instance;

    private Singleton() { }

    public static Singleton getInstance() {
        if (instance == null) {                 // 1st check (no locking, fast path)
            synchronized (Singleton.class) {
                if (instance == null) {          // 2nd check (inside lock, safe)
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

- Only locks when `instance` is still `null` — once it's created, future calls skip the `synchronized` block entirely (fast path).
- Checked **twice** ("double-checked"): once before locking (cheap, fast), once after acquiring the lock (safe, avoids two threads both getting past the first check and both creating an instance).
- `volatile` is required — it stops the compiler/CPU from reordering instructions, which could otherwise let another thread see a half-built object (a subtle JVM optimization bug without it).

---

## 4) Bill Pugh Singleton (Static Inner Helper Class)

```java
public class Singleton {
    private Singleton() { }

    // Not loaded into memory until someone calls getInstance()
    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```

- Relies on how the JVM loads classes: the inner `Holder` class is **not loaded until it's actually referenced** (i.e., until `getInstance()` is first called).
- Once referenced, the JVM's class-loading mechanism guarantees `INSTANCE` is created **exactly once, in a thread-safe way** — no `synchronized`, no `volatile` needed, and it's still lazy.
- Widely considered the best general-purpose approach in Java — simple, lazy, and thread-safe with no locking overhead.

---

## 5) Enum-Based Singleton

```java
public enum Singleton {
    INSTANCE;

    public void doSomething() { ... }
}
// usage: Singleton.INSTANCE.doSomething();
```

- Java guarantees enum values are instantiated only **once**, and the JVM handles thread-safety for you automatically.
- Bonus: it's immune to attacks via **reflection** (can't normally invoke a private constructor twice) and **serialization/deserialization** (normal singletons can accidentally create a second instance when deserialized — enums don't have this problem).
- Considered the **safest** way to write a Singleton in Java, though it's not lazy in the traditional sense (loaded when the enum class is first used) and can feel unintuitive since it's not a typical class.

---

## Pitfalls

- **Overuse = hidden global state** → makes unit testing harder (hard to mock/replace).
- Can hide tight coupling — code quietly depends on a global object instead of explicit dependencies.
- In multi-threaded code, a naive (non-synchronized) lazy implementation can accidentally create two instances.

## Quick Recap

| Variant | Thread-Safe? | Lazy? | Notes |
|---|---|---|---|
| 1. Basic | ❌ No | ✅ Yes | Simple, but race condition can create 2 instances |
| 2. Basic + synchronized | ✅ Yes | ✅ Yes | Safe, but locks on every call (slow) |
| 3. Double-checked locking | ✅ Yes | ✅ Yes | Fast path after init, needs `volatile` |
| 4. Bill Pugh (static holder) | ✅ Yes | ✅ Yes | Best of both worlds, no locking needed |
| 5. Enum-based | ✅ Yes | ❌ Not really | Safest overall, immune to reflection/serialization attacks |

**General purpose:** Only one instance, globally accessible, via private constructor + static instance + static getter.
**Watch out for:** thread safety, hidden global coupling, harder unit testing.
