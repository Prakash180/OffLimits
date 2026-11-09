# Strategy Pattern

> Category: **Behavioural** (controls how objects *communicate/behave* — lets you swap an algorithm at runtime)

## What it is

- Defines a **family of interchangeable algorithms**, puts each one behind a common interface, and lets the client pick/swap which one to use **at runtime**.
- Instead of hardcoding `if-else`/`switch` logic for "which algorithm to run", you delegate the behavior to a separate "strategy" object.
- **Layman:** Google Maps lets you pick "Driving", "Walking", or "Cycling" to get directions. The destination doesn't change, but *how* you get there (the strategy) does — and you can switch it anytime.

## Why use it

- Avoids giant `if-else`/`switch` blocks that pick behavior based on a type/flag.
- New algorithms can be added as new classes — existing code doesn't need to change (Open/Closed Principle).
- Behavior can be swapped **at runtime**, not just fixed at compile time.

---

## Example: Payment Methods

```java
// Strategy interface — common contract for all algorithms
interface PaymentStrategy {
    void pay(int amount);
}

// Concrete strategies — each is one interchangeable algorithm
class CreditCardPayment implements PaymentStrategy {
    public void pay(int amount) {
        System.out.println("Paid " + amount + " using Credit Card");
    }
}

class UpiPayment implements PaymentStrategy {
    public void pay(int amount) {
        System.out.println("Paid " + amount + " using UPI");
    }
}

class PayPalPayment implements PaymentStrategy {
    public void pay(int amount) {
        System.out.println("Paid " + amount + " using PayPal");
    }
}

// Context — holds a reference to a strategy, delegates the work to it
class ShoppingCart {
    private PaymentStrategy paymentStrategy;   // the chosen algorithm

    // strategy can be injected/changed at runtime
    void setPaymentStrategy(PaymentStrategy strategy) {
        this.paymentStrategy = strategy;
    }

    void checkout(int amount) {
        paymentStrategy.pay(amount);   // doesn't care HOW payment happens, just delegates
    }
}

// Client code
ShoppingCart cart = new ShoppingCart();

cart.setPaymentStrategy(new UpiPayment());
cart.checkout(500);                       // -> "Paid 500 using UPI"

cart.setPaymentStrategy(new CreditCardPayment());
cart.checkout(1200);                      // -> "Paid 1200 using Credit Card"
```

- `ShoppingCart` (the **context**) never has `if (type.equals("UPI")) ... else if (type.equals("CARD")) ...` — it just calls `paymentStrategy.pay()` and lets the strategy object handle the details.
- Adding a new payment method (e.g., `NetBankingPayment`) means writing a new class — `ShoppingCart` code is untouched.

---

## Without Strategy (the problem it solves)

```java
// Bad: one class with branching logic for every algorithm variant
class ShoppingCart {
    void checkout(int amount, String method) {
        if (method.equals("UPI")) {
            System.out.println("Paid " + amount + " using UPI");
        } else if (method.equals("CARD")) {
            System.out.println("Paid " + amount + " using Credit Card");
        } else if (method.equals("PAYPAL")) {
            System.out.println("Paid " + amount + " using PayPal");
        }
        // every new payment method = editing this method again
    }
}
```

- Violates Open/Closed Principle — every new strategy requires modifying this existing, already-tested method.
- Hard to test one algorithm in isolation — it's all tangled together in one method.

---

## When to use it

- You have multiple ways of doing the **same task** (sorting, payment, compression, route calculation, discount rules) and want to switch between them easily.
- You see repeated `if-else`/`switch` blocks that just select between different variations of behavior.
- You want to test each algorithm independently (each is now its own class).

## Pitfalls

- Adds more classes/files — can feel like overkill if you only ever have one or two simple variants that never change.
- Client must know about the different strategy classes to pick the right one (someone still has to decide which strategy to inject).

## Quick Recap

| Aspect | Detail |
|---|---|
| Purpose | Swap interchangeable algorithms/behaviors at runtime |
| Key trick | Common interface + concrete strategy classes + a "context" that delegates to the current strategy |
| Replaces | Long `if-else`/`switch` chains that pick behavior by type/flag |
| Related principle | Open/Closed Principle — add new strategies without touching existing code |
