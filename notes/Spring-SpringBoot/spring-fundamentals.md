# Spring & Spring Boot Fundamentals

---

## Spring vs Spring Boot

| | Spring | Spring Boot |
|---|---|---|
| What it is | A framework for building Java apps | A layer on top of Spring that removes boilerplate setup |
| Configuration | You configure everything manually (XML or Java config) | Auto-configured out of the box |
| Server setup | You deploy to an external server (e.g., Tomcat) | Comes with an embedded server (Tomcat built-in) |
| Starting a project | Tedious — lots of setup | Quick — use Spring Initializr, run immediately |
| Use case | Full control over config | Faster development, microservices |

**In short:** Spring Boot is Spring, just with the setup work already done for you.

---

## IoC — Inversion of Control

- Normally, **you** create objects: `UserService service = new UserService();`
- With IoC, **Spring creates and manages objects** for you
- You just say "I need this object" and Spring hands it to you
- The container that manages all these objects is called the **IoC Container** (also called the Application Context)

**Why bother?**
- You don't worry about creating dependencies manually
- Easier to swap implementations
- Easier to test (mock objects)

---

## DI — Dependency Injection

DI is **how** IoC is applied in practice.

Instead of a class creating its own dependencies, they are **injected from outside**.

### 3 ways to inject:

**1. Constructor Injection** ← recommended
```java
@Service
public class OrderService {
    private final PaymentService paymentService;

    public OrderService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }
}
```

**2. Setter Injection**
```java
@Autowired
public void setPaymentService(PaymentService paymentService) {
    this.paymentService = paymentService;
}
```

**3. Field Injection** ← convenient but harder to test
```java
@Autowired
private PaymentService paymentService;
```

---

## DI in Spring vs Spring Boot

| | Spring (plain) | Spring Boot |
|---|---|---|
| How beans are registered | You define them in XML or a `@Configuration` class | Auto-detected via component scanning |
| Component scan setup | You manually configure which packages to scan | Automatically scans from the main class package downward |
| Wiring | Same `@Autowired` annotations | Same — no difference here |

**Example in plain Spring** — you'd need this:
```xml
<!-- applicationContext.xml -->
<bean id="paymentService" class="com.example.PaymentService"/>
```
or
```java
@Configuration
public class AppConfig {
    @Bean
    public PaymentService paymentService() {
        return new PaymentService();
    }
}
```

**In Spring Boot** — just annotate the class and it's auto-detected:
```java
@Service
public class PaymentService { ... }
```

---

## Common Annotations

### Stereotype Annotations (mark a class as a Spring-managed bean)

| Annotation | Used on | Purpose |
|---|---|---|
| `@Component` | Any class | Generic bean — tells Spring to manage this class |
| `@Service` | Service layer | Same as `@Component`, but signals business logic |
| `@Repository` | Data access layer | Same as `@Component`, adds DB exception translation |
| `@Controller` | Web layer (MVC) | Handles HTTP requests, returns views |
| `@RestController` | Web layer (REST) | `@Controller` + `@ResponseBody` — returns JSON/XML |

> `@Service`, `@Repository`, `@Controller` are all just `@Component` with a label. Functionally the same, but they communicate intent.

---

### Wiring Annotations

**`@Autowired`**
- Tells Spring to inject a dependency automatically
- Can be on a field, setter, or constructor
```java
@Autowired
private UserRepository userRepository;
```

**`@Qualifier`**
- Used when there are **multiple beans of the same type**
- Tells Spring which one to inject
```java
@Autowired
@Qualifier("emailNotificationService")
private NotificationService notificationService;
```

**`@Primary`**
- When multiple beans exist, mark one as the **default** choice
- Avoids needing `@Qualifier` everywhere
```java
@Primary
@Service
public class EmailNotificationService implements NotificationService { ... }
```

---

### Configuration Annotations

**`@Configuration`**
- Marks a class as a source of bean definitions
- Used with `@Bean` methods

**`@Bean`**
- Declares a method's return value as a Spring bean
- Used inside `@Configuration` classes
```java
@Configuration
public class AppConfig {
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

**`@ComponentScan`**
- Tells Spring which packages to scan for `@Component` and friends
- In Spring Boot, this is automatic from the main class package

---

### Spring Boot Specific

**`@SpringBootApplication`**
- The main annotation on the entry-point class
- It's a combo of three annotations:
  - `@Configuration` — this class can define beans
  - `@EnableAutoConfiguration` — let Spring Boot auto-configure things
  - `@ComponentScan` — scan this package and sub-packages for beans

```java
@SpringBootApplication
public class MyApp {
    public static void main(String[] args) {
        SpringApplication.run(MyApp.class, args);
    }
}
```

**`@Value`**
- Injects a value from `application.properties`
```java
@Value("${app.timeout}")
private int timeout;
```

---

## Quick Mental Model

```
@SpringBootApplication starts up
    → IoC Container (ApplicationContext) is created
    → Spring scans for @Component / @Service / @Repository etc.
    → Creates beans and stores them
    → Wherever @Autowired is found, Spring injects the right bean
```
