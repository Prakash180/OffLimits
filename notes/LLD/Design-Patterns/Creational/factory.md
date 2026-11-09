# Factory Design Pattern

> Category: **Creational** (controls how objects are *created*, hides the `new` keyword from the caller)

## What it is

- Instead of the client calling `new SomeClass()` directly, it asks a **factory** to create the object for it.
- The factory decides **which concrete class** to instantiate, based on some input — the client only knows the common interface/abstract type, not the exact class.
- **Layman:** You order "a coffee" at a counter — you don't know (or care) exactly which machine/recipe made it. The barista (factory) decides how to make it based on what you asked for.

## Why use it

- Removes tight coupling between client code and concrete classes — client depends only on an interface/abstract type.
- Centralizes object-creation logic in one place — easy to add new types later without touching client code (ties in with **Open/Closed Principle**).

---

## Why Do We Even Need It? (The Real Problem)

Say the app sends notifications, and the user picks Email, SMS or Push. **Without a factory**, every place that needs a notifier decides and builds it itself:

```java
// OrderService.java
Notifier n;
if (type.equals("EMAIL"))    n = new EmailNotifier(smtpHost, smtpPort, creds);
else if (type.equals("SMS")) n = new SmsNotifier(twilioKey);
else                         n = new PushNotifier(fcmToken);
n.send("Order placed");

// PaymentService.java   -> same if-else block again
// ReminderService.java  -> same if-else block again
// ... 15 more places
```

Problems:

1. **Duplication**: same if-else and same setup details (SMTP host, API keys) copy-pasted everywhere.
2. **Tight coupling**: every service knows `EmailNotifier`, `SmsNotifier`, `PushNotifier` and how to configure each.
3. **Painful change**: adding `WhatsAppNotifier` means editing 15+ places. Miss one = bug.

**With a factory**, creation lives in one place:

```java
Notifier n = NotifierFactory.create(type);   // every service does just this
n.send("Order placed");
```

- Adding WhatsApp = one edit, inside the factory. No service changes.
- Services only know the `Notifier` interface, not which class they got or how it was configured.
- Setup details exist in exactly one place.

**Core idea:** move "which class, and how to build it" out of the code that *uses* the object. The user of the object should care about *what it does* (`send()`), not *what it is* or *how it's built*.

### When the need is real

| Situation | Why a factory helps |
|---|---|
| Type only known at **runtime** (user choice, config, request data) | The if-else is unavoidable, so keep it in one place |
| Building the object is **complicated** (dependencies, config, setup) | Callers shouldn't repeat that |
| You want to **swap implementations** (fake notifier in tests, different provider in prod) | Only the factory changes |
| New types keep **arriving** | One edit instead of many |

### When you DON'T need it

```java
List<String> names = new ArrayList<>();   // just use new
```

One concrete class, no variations, simple construction = a factory is needless indirection. Tutorials often force the pattern onto such cases, which is why it can feel pointless.

### You already use factories

- `Calendar.getInstance()`, `List.of(...)`
- `DriverManager.getConnection(url)` returns the right DB driver connection for the URL
- Spring: the container is a giant factory deciding what to build and inject.

### Why 3 flavours exist (each fixes a weakness of the previous)

- **Simple Factory**: still has an if-else you edit for every new type.
- **Factory Method**: removes the if-else, one subclass per type (add a class instead of editing a method).
- **Abstract Factory**: when you need several **matching** objects together.

---

## The Factory Family at a Glance

"Factory" is really 3 related ideas. Don't mix them up:

| | Simple Factory | Factory Method | Abstract Factory |
|---|---|---|---|
| Is it GoF? | No (just a handy idiom) | Yes | Yes |
| Creates | **One** product, chosen by input | **One** product, chosen by subclass | A **family of related** products |
| How it decides | `switch`/`if` on a parameter | Subclass overrides a method | Pick one concrete factory; it builds the whole family |
| Uses | A static method | Inheritance | Composition (factory object passed in) |
| Layman | One barista, you say "coffee" or "tea" | Each cafe branch makes its own coffee | A whole themed kit: Windows kit or Mac kit |
| Pick it when | Few, stable types | New types keep arriving | Products must **match each other** |

- **Factory Method** = one product, **subclass** decides.
- **Abstract Factory** = many related products, **factory object** decides (often a factory of factory methods).

---

## 1) Simple Factory (not a full GoF pattern, but the common starting point)

```java
// Common interface (the "product")
interface Notifier {
    void send(String message);
}

class EmailNotifier implements Notifier {
    public void send(String message) { System.out.println("Email: " + message); }
}

class SmsNotifier implements Notifier {
    public void send(String message) { System.out.println("SMS: " + message); }
}

class PushNotifier implements Notifier {
    public void send(String message) { System.out.println("Push: " + message); }
}

// The factory — one place that knows how to create each Notifier
class NotifierFactory {
    public static Notifier create(String type) {
        switch (type) {
            case "EMAIL": return new EmailNotifier();
            case "SMS":   return new SmsNotifier();
            case "PUSH":  return new PushNotifier();
            default: throw new IllegalArgumentException("Unknown notifier: " + type);
        }
    }
}

// Client code — never writes `new EmailNotifier()` etc.
Notifier notifier = NotifierFactory.create("EMAIL");   // type may come from user/config
notifier.send("Order placed");                          // -> "Email: Order placed"
```

- Client only talks to `Notifier` (interface) and `NotifierFactory` — it never mentions `EmailNotifier`/`SmsNotifier`/`PushNotifier` directly.
- In real code the constructors take config (SMTP host, API keys). That setup lives **only** inside the factory.
- **Downside:** adding `WhatsAppNotifier` means editing the `switch` inside `NotifierFactory` — technically violates Open/Closed Principle (this is what the real **Factory Method** pattern fixes).

---

## 2) Factory Method Pattern (the actual GoF pattern)

> Define a method for creating an object, but let **subclasses decide** which class to instantiate.

```java
// Product interface
interface Notifier {
    void send(String message);
}
class EmailNotifier implements Notifier {
    public void send(String message) { System.out.println("Email: " + message); }
}
class SmsNotifier implements Notifier {
    public void send(String message) { System.out.println("SMS: " + message); }
}
class PushNotifier implements Notifier {
    public void send(String message) { System.out.println("Push: " + message); }
}

// Creator — declares the factory method, but doesn't know the concrete product
abstract class NotificationService {
    abstract Notifier createNotifier();        // the "factory method"

    void notifyUser(String message) {          // shared logic, works with ANY notifier
        Notifier notifier = createNotifier();
        System.out.println("Logging: about to send");
        notifier.send(message);
    }
}

// Concrete creators — each decides which product to instantiate
class EmailService extends NotificationService {
    Notifier createNotifier() { return new EmailNotifier(); }
}
class SmsService extends NotificationService {
    Notifier createNotifier() { return new SmsNotifier(); }
}
class PushService extends NotificationService {
    Notifier createNotifier() { return new PushNotifier(); }
}

// Client code
NotificationService service = new EmailService();
service.notifyUser("Order placed");   // -> "Email: Order placed"
```

- Adding `WhatsAppNotifier` means adding a new `WhatsAppService` subclass — **no existing code is modified**, only extended. This fully satisfies Open/Closed Principle, unlike the Simple Factory's `switch`.
- The "factory method" (`createNotifier()`) is abstract in the base class — each subclass overrides it to return its own product.
- The base class holds the **common workflow** (`notifyUser`) and only the "which notifier?" step varies. That is the real reason to prefer this over a plain `switch`.

---

## 3) Abstract Factory Pattern (GoF)

> Provide an interface for creating a **family of related objects**, without naming their concrete classes.

- Factory Method makes **one** product. Abstract Factory makes **several products that must go together** (same "theme"/family).
- **Layman:** Furniture shop with two collections, Modern and Victorian. A Modern chair must come with a Modern table. You pick the collection (the factory) once, and every piece it gives you matches.

```java
// Product interfaces - two related product types
interface Button   { void render(); }
interface Checkbox { void render(); }

// Family 1: Windows
class WindowsButton implements Button {
    public void render() { System.out.println("Windows button"); }
}
class WindowsCheckbox implements Checkbox {
    public void render() { System.out.println("Windows checkbox"); }
}

// Family 2: Mac
class MacButton implements Button {
    public void render() { System.out.println("Mac button"); }
}
class MacCheckbox implements Checkbox {
    public void render() { System.out.println("Mac checkbox"); }
}

// Abstract Factory - one creation method PER product in the family
interface UIFactory {
    Button createButton();
    Checkbox createCheckbox();
}

// Concrete factories - each builds one complete, matching family
class WindowsUIFactory implements UIFactory {
    public Button createButton()     { return new WindowsButton(); }
    public Checkbox createCheckbox() { return new WindowsCheckbox(); }
}
class MacUIFactory implements UIFactory {
    public Button createButton()     { return new MacButton(); }
    public Checkbox createCheckbox() { return new MacCheckbox(); }
}

// Client - only knows UIFactory, Button, Checkbox
class Application {
    private final Button button;
    private final Checkbox checkbox;

    Application(UIFactory factory) {          // factory injected
        this.button = factory.createButton();
        this.checkbox = factory.createCheckbox();
    }
    void render() { button.render(); checkbox.render(); }
}

// Pick the family ONCE, e.g. from the OS / config
UIFactory factory = isMac ? new MacUIFactory() : new WindowsUIFactory();
new Application(factory).render();   // -> Mac button, Mac checkbox (never mixed)
```

- The client can never end up with a Mac button next to a Windows checkbox. The factory guarantees the family stays consistent.
- Adding a new family (e.g., Linux) = new product classes + one new `LinuxUIFactory`. Client code is untouched.
- **Downside:** adding a new product **type** (e.g., `Slider`) means changing `UIFactory` and **every** concrete factory.
- Each method on an Abstract Factory (`createButton()`) is basically a Factory Method, which is why it is called a "factory of factory methods".

---

## Simple Factory vs Factory Method vs Abstract Factory

| Aspect | Simple Factory | Factory Method | Abstract Factory |
|---|---|---|---|
| Structure | One factory class with if/switch logic | Abstract creator + one subclass per product | Factory interface with several `create...()` methods + one factory per family |
| Products per factory | One (any type via parameter) | One | Many, related |
| Adding new type | Edit existing factory class | Add a new subclass (no existing code touched) | New family: add a new factory. New product type: edit all factories |
| Mechanism | Conditional logic | Inheritance (subclass overrides) | Composition (factory object injected) |
| OOP purity | Not a real GoF pattern | Real GoF pattern | Real GoF pattern |
| Complexity | Simple, good for small/fixed sets of types | More classes, but scales better | Most classes, best for whole families |

**Rule of thumb:** one product, few types -> Simple Factory. One product, open-ended types -> Factory Method. Several products that must match -> Abstract Factory.

**Interview one-liner:** "Factory Method creates one product via inheritance. Abstract Factory creates a family of related products via composition."

---

## When to use it

- You don't know ahead of time exactly which concrete class you'll need (decided at runtime based on config, input, environment, etc.).
- You want to decouple client code from concrete classes so new types can be added without breaking existing code.
- **Abstract Factory specifically:** you need **sets of objects that must be used together** (UI themes per OS, database kits like connection + command + reader per vendor, cross-platform widgets) and want to swap the whole set in one place.

## Pitfalls

- Simple Factory can become a maintenance bottleneck (one giant `switch`/`if-else` growing over time).
- Factory Method means more classes overall — can feel like overkill for just 2-3 simple types.
- Don't reach for Factory Method if there's truly only ever going to be one implementation — adds unnecessary indirection.
- Abstract Factory explodes in class count (products x families), and adding a new product type touches every factory. Skip it if you only have one family or unrelated products.

## Quick Recap

| Aspect | Detail |
|---|---|
| Purpose | Hide object creation logic from the client, decouple from concrete classes |
| Key trick | Client depends on interface/abstract type; a factory decides the concrete class |
| Simple Factory | One factory method with conditional logic (not a true GoF pattern) |
| Factory Method | Abstract creator class, subclasses override to supply the concrete product |
| Abstract Factory | Factory interface that creates a whole **family of related products**; swap the factory to swap the family |
| Remember | Simple Factory = `switch`. Factory Method = one product, subclass decides. Abstract Factory = many matching products, factory object decides |
| Related principle | Open/Closed Principle — extend via new subclasses, don't modify existing factory logic |
