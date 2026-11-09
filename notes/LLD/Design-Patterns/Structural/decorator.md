# Decorator Pattern

> Category: **Structural** (composes objects into bigger structures — here, by **wrapping** an object to add behavior)

## What it is

- Lets you **add new behavior to an object dynamically** by wrapping it inside another object that has the **same interface**.
- Each wrapper (decorator) does its own extra work, then passes the call to the object it wraps.
- You can stack many wrappers, in any order.
- **Layman:** Ordering a coffee. Start with plain coffee, then add milk, then sugar, then whipped cream. Each add-on wraps the previous drink: it adds its own cost/description and still *is* a drink.

## Why use it

- Add features **without changing** the original class (Open/Closed Principle).
- Avoids a **class explosion** from inheritance (`CoffeeWithMilk`, `CoffeeWithMilkAndSugar`, `CoffeeWithSugarAndCream`...).
- Combine features **at runtime** in any mix, not fixed at compile time.
- Each decorator has **one small job** (Single Responsibility Principle).

---

## Structure

- **Component** (interface): the common contract.
- **Concrete Component**: the plain object (e.g., `Espresso`).
- **Decorator** (abstract class): implements the same interface **and holds a reference** to a Component.
- **Concrete Decorators**: add extra behavior before/after calling the wrapped object.

```
Client -> MilkDecorator -> SugarDecorator -> Espresso
              (+milk)         (+sugar)        (base)
```

---

## Example: Coffee Shop

```java
// Component - common contract
interface Coffee {
    String description();
    int cost();
}

// Concrete component - the plain object
class Espresso implements Coffee {
    public String description() { return "Espresso"; }
    public int cost() { return 100; }
}

// Decorator - same interface + HAS-A Coffee inside
abstract class CoffeeDecorator implements Coffee {
    protected final Coffee coffee;   // the wrapped object

    CoffeeDecorator(Coffee coffee) {
        this.coffee = coffee;
    }
}

// Concrete decorators - each adds its own bit
class Milk extends CoffeeDecorator {
    Milk(Coffee coffee) { super(coffee); }

    public String description() { return coffee.description() + ", Milk"; }
    public int cost() { return coffee.cost() + 20; }
}

class Sugar extends CoffeeDecorator {
    Sugar(Coffee coffee) { super(coffee); }

    public String description() { return coffee.description() + ", Sugar"; }
    public int cost() { return coffee.cost() + 5; }
}

class WhippedCream extends CoffeeDecorator {
    WhippedCream(Coffee coffee) { super(coffee); }

    public String description() { return coffee.description() + ", Whipped Cream"; }
    public int cost() { return coffee.cost() + 30; }
}

// Client code
Coffee order = new Espresso();
order = new Milk(order);
order = new Sugar(order);
order = new WhippedCream(order);

System.out.println(order.description());  // Espresso, Milk, Sugar, Whipped Cream
System.out.println(order.cost());         // 100 + 20 + 5 + 30 = 155
```

- Each decorator **wraps** the previous one, so a call travels inward through the layers, then results bubble back out.
- Want a double milk coffee? `new Milk(new Milk(new Espresso()))`. No new class needed.
- Adding `Caramel`? Write one new class; nothing else changes.

---

## Without Decorator (the problem it solves)

```java
// Bad: a subclass for every combination
class EspressoWithMilk extends Espresso { ... }
class EspressoWithSugar extends Espresso { ... }
class EspressoWithMilkAndSugar extends Espresso { ... }
class EspressoWithMilkSugarAndCream extends Espresso { ... }
// 3 add-ons -> 7+ classes. 10 add-ons -> 1000+ classes.
```

- Inheritance is **fixed at compile time**; you can't add or remove a topping at runtime.
- Number of classes grows exponentially with each new option.

---

## Real-World Java Example: I/O Streams

```java
InputStream in = new BufferedInputStream(
                    new FileInputStream("data.txt"));
```

- `FileInputStream` = the base object (reads bytes from a file).
- `BufferedInputStream` = decorator that adds buffering.
- Others: `DataInputStream`, `GZIPInputStream`, `Collections.unmodifiableList(...)` (wraps a list to make it read-only).
- Spring examples: `HttpServletRequestWrapper`, `BeanPostProcessor`-style wrapping.

---

## Decorator vs Similar Patterns

| Pattern | Intent | Difference |
|---|---|---|
| **Decorator** | Add behavior to the same interface | Same interface, **stackable**, adds responsibilities |
| **Proxy** | Control access (lazy load, auth, caching) | Usually one proxy, manages access rather than adding features (see [proxy-and-reverse-proxy.md](../../../System%20Design/proxy-and-reverse-proxy.md) for the network version) |
| **Adapter** | Make an incompatible interface fit | **Changes** the interface; decorator keeps it |
| **Strategy** | Swap an algorithm | Replaces behavior; decorator **adds to** behavior (see [strategy.md](../Behavioural/strategy.md)) |
| **Inheritance** | Extend at compile time | Static; decorator is dynamic |

---

## When to use it

- You want to add responsibilities to individual objects **at runtime**, without affecting others.
- Subclassing would cause too many combinations.
- Cross-cutting add-ons: logging, caching, compression, encryption, validation, retry, metrics, UI borders/scrollbars.

## Pitfalls

- Lots of small classes, which can be hard to read.
- Deep wrapper chains are hard to debug (stack traces go through many layers).
- **Order matters** (e.g., encrypt then compress is not the same as compress then encrypt).
- Identity checks (`instanceof`, `==`) on the decorated object can behave unexpectedly, since the outer wrapper is what you hold.
- Don't use it if there's only one fixed variation; a simple subclass or a flag is enough.

## Quick Recap

| Aspect | Detail |
|---|---|
| Purpose | Add behavior to an object dynamically by wrapping it |
| Key trick | Decorator **implements the same interface** and **holds a reference** to the wrapped object |
| Replaces | Subclass-per-combination explosion |
| Related principle | Open/Closed + Single Responsibility; prefers composition over inheritance |
| Java examples | `BufferedInputStream`, `Collections.unmodifiableList` |
| Remember | "Wrap it, don't subclass it" |

## Practical Exercise

- In `SideProject`, build a `Notifier` interface with `send(String msg)`. Create `EmailNotifier` as the base, then decorators `SmsDecorator`, `SlackDecorator`, and `LoggingDecorator`. Stack them so one `send()` call goes through all channels.
