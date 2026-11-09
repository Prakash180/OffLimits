# Spring Stereotype Annotations — Deep Dive

These annotations tell Spring: **"Hey, manage this class for me. Create an instance of it and store it in the IoC Container."**

---

## **`@Component`** — The Generic Bean

```java
@Component
public class EmailSender {
    public void sendEmail(String to, String message) {
        System.out.println("Sending email to " + to);
    }
}
```

**What it does:**
- Marks any class as a Spring-managed bean
- Spring automatically detects it, creates an instance, and stores it in the container
- Any other class can request it via `@Autowired`

**When to use it:**
- For utility classes that don't fit the other categories
- General-purpose components

---

## **`@Service`** — Business Logic Layer

```java
@Service
public class OrderService {
    private final PaymentService paymentService;
    
    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
    
    public void processOrder(Order order) {
        // Complex business logic here
        paymentService.charge(order.getAmount());
        // Update inventory, send notification, etc.
    }
}
```

**What it does:**
- Functionally **identical to `@Component`** — Spring treats it the same way
- But it **signals intent**: "This class contains business logic"

**When to use it:**
- For classes in the **service/business logic layer**
- Classes that handle core business operations
- Example: `OrderService`, `UserService`, `PaymentService`

**Why have it if it's the same as `@Component`?**
- Code clarity — developers reading your code know this is where the business logic lives
- Makes the architecture obvious

---

## **`@Repository`** — Data Access Layer

```java
@Repository
public class UserRepository {
    private JdbcTemplate jdbcTemplate;
    
    public User findById(Long id) {
        // Query the database
        return jdbcTemplate.queryForObject("SELECT * FROM users WHERE id=?", User.class, id);
    }
    
    public void save(User user) {
        // Insert into database
    }
}
```

**What it does:**
- Functionally **identical to `@Component`** — Spring manages it
- But it adds **special exception handling**: translates database exceptions into Spring exceptions
- Signals intent: "This class talks to the database"

**When to use it:**
- For classes in the **data access layer** (DAO = Data Access Object)
- Classes that interact with databases or external data sources
- Example: `UserRepository`, `OrderRepository`, `ProductRepository`

**Why special exception handling matters:**
- Different databases throw different exceptions
- Spring translates all of them into consistent, predictable exceptions
- Your service layer doesn't need to know about database-specific errors

---

## **`@Controller`** — Web Layer (MVC - returns HTML/Views)

```java
@Controller
public class UserController {
    private UserService userService;
    
    @GetMapping("/users/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.findById(id);
        model.addAttribute("user", user);
        return "user-profile";  // ← Returns the name of an HTML template
    }
}
```

**What it does:**
- Marks a class as handling **HTTP requests**
- Functionally `@Component` + the ability to map HTTP routes (`@GetMapping`, `@PostMapping`, etc.)
- Returns **HTML pages** (views)

**When to use it:**
- For **traditional web apps** that render HTML pages
- Classic MVC architecture (Model-View-Controller)
- Example: A blog where users see HTML pages

**How it works:**
- Browser sends request → `@Controller` method handles it → returns HTML template name → template engine renders HTML → sent back to browser

---

## **`@RestController`** — Web Layer (REST - returns JSON/XML)

```java
@RestController
@RequestMapping("/api/users")
public class UserRestController {
    private UserService userService;
    
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);  // ← Returns the object directly as JSON
    }
    
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }
}
```

**What it does:**
- Shorthand for `@Controller` + `@ResponseBody`
- Handles HTTP requests but returns **JSON/XML data** instead of HTML
- Perfect for **APIs** (Application Programming Interfaces)

**When to use it:**
- For **REST APIs** where clients are other applications, not browsers
- Mobile apps, frontend apps (React, Vue, etc.) that make API calls
- Example: `/api/users/{id}` returning `{"id": 1, "name": "John", "email": "john@example.com"}`

**The difference:**
```
@Controller      → HTTP request → @GetMapping method → returns "user-profile" → HTML template renders → HTML sent back
@RestController  → HTTP request → @GetMapping method → returns User object → converted to JSON → JSON sent back
```

---

## Quick Reference

| Annotation | Layer | Returns | Use Case |
|---|---|---|---|
| `@Component` | Any | — | Utility classes, general purpose |
| `@Service` | Business Logic | — | Classes with business rules |
| `@Repository` | Data Access | — | Classes talking to databases |
| `@Controller` | Web | HTML | Traditional web apps (server-rendered pages) |
| `@RestController` | Web | JSON/XML | APIs for mobile/frontend apps |

---

## Real-World Example: An Order System

```java
// Web layer - handles HTTP requests
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private OrderService orderService;  // ← Injected @Service
    
    @PostMapping
    public Order createOrder(@RequestBody Order order) {
        return orderService.processOrder(order);
    }
}

// Business logic layer
@Service
public class OrderService {
    private OrderRepository orderRepository;  // ← Injected @Repository
    private PaymentService paymentService;   // ← Injected @Service
    
    public Order processOrder(Order order) {
        paymentService.charge(order.getAmount());
        return orderRepository.save(order);
    }
}

// Data access layer
@Repository
public class OrderRepository {
    private JdbcTemplate jdbcTemplate;
    
    public Order save(Order order) {
        // Insert into database
    }
}
```

**Flow:**
1. Browser/Mobile app → POST request to `/api/orders` (JSON body)
2. `OrderController` receives it (`@RestController`)
3. Controller calls `OrderService.processOrder()` (`@Service`)
4. Service calls `OrderRepository.save()` (`@Repository`)
5. Repository talks to the database
6. Returns Order object → automatically converted to JSON → sent back

All these classes are **managed by Spring's IoC Container** thanks to their stereotype annotations.
