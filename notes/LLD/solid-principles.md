 # SOLID Principles

Five rules for writing OOP code that's easy to change without breaking things.
Coined by Robert C. Martin (Uncle Bob).

---

## S — Single Responsibility Principle (SRP)

> A class should have **only one reason to change**.

- One class = one job. Don't cram unrelated logic together.
- **Layman:** A chef cooks, a waiter serves. Don't make the chef also handle billing.

```java
// Bad: Invoice both calculates AND prints/saves — two reasons to change
class Invoice {
    double calculateTotal() { ... }
    void printInvoice() { ... }
    void saveToDatabase() { ... }
}

// Good: split responsibilities
class Invoice {
    double calculateTotal() { ... }
}
class InvoicePrinter {
    void print(Invoice invoice) { ... }
}
class InvoiceRepository {
    void save(Invoice invoice) { ... }
}
```

---

## O — Open/Closed Principle (OCP)

> Classes should be **open for extension, closed for modification**.

- Add new behavior by adding new code (e.g., a new subclass), not by editing existing tested code.
- **Layman:** Add a new topping to a pizza menu instead of rewriting the whole menu.

```java
// Bad: every new shape needs an if-else edit here
double area(Object shape) {
    if (shape instanceof Circle) { ... }
    else if (shape instanceof Square) { ... }
}

// Good: extend via polymorphism, no need to touch existing code
interface Shape {
    double area();
}
class Circle implements Shape {
    public double area() { return Math.PI * r * r; }
}
class Square implements Shape {
    public double area() { return side * side; }
}
```

---

## L — Liskov Substitution Principle (LSP)

> Subclasses must be **substitutable** for their base class without breaking the program.

- If `B extends A`, you should be able to use a `B` anywhere an `A` is expected — with no surprises.
- **Layman:** If a toy says "battery operated", any battery you put in should work the same way.

```java
// Bad: Square breaks the contract of Rectangle (setWidth/setHeight behave weirdly)
class Rectangle {
    void setWidth(int w) { ... }
    void setHeight(int h) { ... }
}
class Square extends Rectangle {
    void setWidth(int w) { width = height = w; } // surprise side effect!
}

// Good: don't force an inheritance relationship that doesn't truly hold
interface Shape {
    int area();
}
class Rectangle implements Shape { ... }
class Square implements Shape { ... }
```

---

## I — Interface Segregation Principle (ISP)

> Don't force a class to implement methods it **doesn't use**.

- Prefer several small, specific interfaces over one big fat interface.
- **Layman:** Don't give a basic phone user the "Pilot License" interface with 50 flight methods — give them just "Call" and "Text".

```java
// Bad: forces every worker to implement eat(), even robots
interface Worker {
    void work();
    void eat();
}

// Good: split into focused interfaces
interface Workable {
    void work();
}
interface Eatable {
    void eat();
}
class Robot implements Workable { ... }       // no eat() forced on it
class Human implements Workable, Eatable { ... }
```

---

## D — Dependency Inversion Principle (DIP)

> Depend on **abstractions (interfaces)**, not concrete implementations.

- High-level code shouldn't hard-wire itself to low-level details; both should depend on an interface.
- This is the principle behind Spring's `@Autowired` / dependency injection.
- **Layman:** A lamp works with "a switch" (interface), it doesn't care if it's a wall switch or a remote.

```java
// Bad: tightly coupled to a specific implementation
class Notification {
    EmailService emailService = new EmailService();
    void send(String msg) { emailService.send(msg); }
}

// Good: depend on an abstraction, inject the implementation
interface MessageService {
    void send(String msg);
}
class Notification {
    private final MessageService service;
    Notification(MessageService service) { this.service = service; } // injected
    void send(String msg) { service.send(msg); }
}
```

---

## Quick Recap

| Letter | Principle | One-liner |
|---|---|---|
| S | Single Responsibility | One class, one job |
| O | Open/Closed | Extend, don't modify |
| L | Liskov Substitution | Subclass shouldn't break parent's promise |
| I | Interface Segregation | Small, focused interfaces |
| D | Dependency Inversion | Depend on interfaces, not concrete classes |
