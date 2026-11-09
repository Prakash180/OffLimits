# LLD Design Patterns - Interview Cheatsheet

Quick revision sheet. Full notes are linked in each row. Update this file whenever a new pattern note is added.

## 1. One-Line Summary (Covered Patterns)

| Pattern | Category | One-liner | Layman analogy | Notes |
|---|---|---|---|---|
| **Singleton** | Creational | Only **one instance** of a class, globally accessible | One President of a country | [singleton.md](Creational/singleton.md) |
| **Factory** | Creational | A factory decides **which concrete class** to create; client uses only the interface | Order "a coffee", barista decides how to make it | [factory.md](Creational/factory.md) |
| **Abstract Factory** | Creational | A factory that creates a **family of related objects** that must match | Furniture shop: pick "Modern" and every piece matches | [factory.md](Creational/factory.md) |
| **Decorator** | Structural | **Wrap** an object (same interface) to add behavior at runtime | Coffee + milk + sugar + cream layers | [decorator.md](Structural/decorator.md) |
| **Strategy** | Behavioural | Swap **interchangeable algorithms** at runtime via a common interface | Google Maps: drive / walk / cycle | [strategy.md](Behavioural/strategy.md) |
| **Observer** | Behavioural | Subject **notifies all subscribers** when its state changes | YouTube channel subscribers | [observer.md](Behavioural/observer.md) |

## 2. Problem -> Pattern (What to Say in the Interview)

| If the problem says... | Reach for | Why |
|---|---|---|
| "Only one object should exist" (config, logger, connection pool) | Singleton | Shared resource, one instance |
| "Creating objects based on type / input, without `new` everywhere" | Factory | Decouples client from concrete classes |
| "Several related objects must be created together and stay consistent" (UI theme per OS, DB kit per vendor) | Abstract Factory | One factory = one whole matching family |
| "Lots of `if-else` choosing between algorithms" (payment, sorting, discount) | Strategy | One class per algorithm, swap at runtime |
| "Add features in many combinations, subclasses would explode" | Decorator | Stack wrappers, no class per combination |
| "When X changes, many others must react" (events, notifications, feeds) | Observer | Push-based, loosely coupled |

## 3. Key Trick of Each (The Part to Remember)

| Pattern | Key trick | Code shape |
|---|---|---|
| Singleton | Private constructor + static instance + static getter | `getInstance()` |
| Factory | Return an **interface** type; the factory picks the class | `Product p = factory.create(type)` |
| Abstract Factory | Factory interface with **one create method per product**; one concrete factory per family | `UIFactory f = new MacUIFactory(); f.createButton(); f.createCheckbox();` |
| Decorator | Implements the **same interface** AND **holds** one (HAS-A + IS-A) | `new Milk(new Sugar(new Espresso()))` |
| Strategy | Context holds a strategy reference and **delegates** | `cart.setPayment(new Upi())` |
| Observer | Subject keeps `List<Observer>`, loops and calls `update()` | `subscribe()`, `unsubscribe()`, `notifyObservers()` |

## 4. Variants Worth Knowing

**Singleton**

| Variant | Thread-safe | Lazy | Note |
|---|---|---|---|
| Basic | No | Yes | Race condition, can create 2 instances |
| `synchronized` method | Yes | Yes | Locks on every call (slow) |
| Double-checked locking | Yes | Yes | Needs `volatile` |
| **Bill Pugh (static holder)** | Yes | Yes | Best general choice, no locks |
| **Enum** | Yes | Not really | Safest (reflection + serialization proof) |

**Factory**

| Variant | Idea | Downside |
|---|---|---|
| Simple Factory | One class with `switch` | Edit it for every new type (breaks OCP) |
| Factory Method | Abstract creator, subclasses pick the product | More classes |
| Abstract Factory | Factory object creates a whole family of products | New product type = edit every factory |

**Observer**

| Variant | Notification carries | Trade-off |
|---|---|---|
| Push | The actual data | Signature grows, observer may get unneeded data |
| Pull | Reference to the Subject (observer calls getters) | More coupling to the Subject API |

## 5. Pitfalls (Common Follow-Up Questions)

| Pattern | Watch out for |
|---|---|
| Singleton | Hidden global state, hard to unit test, thread safety |
| Factory | Giant `switch` growth, overkill for 2-3 stable types |
| Abstract Factory | Class explosion (products x families), new product type touches all factories |
| Decorator | Many small classes, **order of wrapping matters**, deep chains hard to debug |
| Strategy | More classes, client must know which strategy to pick |
| Observer | **Memory leaks** if you never unsubscribe, undefined notification order, notification storms |

## 6. Similar Patterns - Don't Mix Them Up

| Pair | Difference |
|---|---|
| **Strategy vs Decorator** | Strategy **replaces** behavior; Decorator **adds to** behavior |
| **Decorator vs Proxy** | Decorator adds responsibilities (stackable); Proxy **controls access** (lazy load, auth, cache) |
| **Decorator vs Adapter** | Decorator **keeps** the interface; Adapter **changes** it |
| **Factory vs Strategy** | Factory = *which object to create*; Strategy = *which algorithm to run* |
| **Factory Method vs Abstract Factory** | Factory Method = **one** product, chosen by **subclass** (inheritance); Abstract Factory = **family** of related products, chosen by a **factory object** (composition) |
| **Strategy vs State** | Strategy: client picks the algorithm; State: object switches behavior by itself as its state changes |
| **Observer vs Pub-Sub** | Observer: subject knows its observers directly; Pub-Sub: a broker sits between them (see [message-queues.md](../../System%20Design/message-queues.md)) |

## 5-Second Revision Chant

- **Singleton**: one and only one.
- **Factory**: don't say `new`, ask the factory.
- **Abstract Factory**: pick the kit once, everything matches.
- **Decorator**: wrap it, don't subclass it.
- **Strategy**: swap the algorithm, kill the `if-else`.
- **Observer**: don't call me, I'll call you.

---

## 7. Still To Cover (Quick One-Liners)

Not yet in detailed notes. Move each row up into the tables above once its note is written.

| Pattern | Category | One-liner |
|---|---|---|
| Builder | Creational | Build complex objects step by step (`new Pizza.Builder().cheese().build()`) |
| Prototype | Creational | Create new objects by **cloning** an existing one |
| Adapter | Structural | Convert one interface into the one the client expects (EU plug to US socket) |
| Facade | Structural | One simple entry point hiding a complicated subsystem |
| Proxy | Structural | Stand-in that controls access (lazy load, auth, caching) |
| Composite | Structural | Treat single objects and groups the same (file/folder tree) |
| Bridge | Structural | Separate abstraction from implementation so both vary independently |
| Flyweight | Structural | Share common data between many objects to save memory |
| Command | Behavioural | Wrap a request as an object (undo/redo, queues) |
| State | Behavioural | Object changes behavior when its internal state changes |
| Template Method | Behavioural | Base class fixes the skeleton, subclasses fill in steps |
| Chain of Responsibility | Behavioural | Pass a request along handlers until one handles it |
| Iterator | Behavioural | Traverse a collection without exposing its internals |
| Mediator | Behavioural | A central object coordinates communication between others |
| Memento | Behavioural | Save and restore an object's state (undo snapshots) |
| Visitor | Behavioural | Add new operations to a class hierarchy without modifying it |

## 8. Pairs Well With

- SOLID principles: [solid-principles.md](../solid-principles.md). Strategy, Decorator and Factory Method all mostly serve **Open/Closed**.
- Core idea behind most patterns: **program to an interface, favor composition over inheritance**.
