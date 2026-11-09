# Spring Boot Quick Reference — Annotations & Patterns Cheat Sheet

A quick lookup guide for common Spring Boot annotations, patterns, and code templates.

---

## 🏷️ Core Annotations

### Component Stereotypes

| Annotation | Purpose | Where |
|---|---|---|
| `@Component` | Generic Spring component | Any class |
| `@Service` | Business logic layer | Service classes |
| `@Repository` | Data access layer | DAO/Repository interfaces |
| `@Controller` | Web request handler (returns HTML) | Web layer |
| `@RestController` | Web request handler (returns JSON) | API layer |
| `@Configuration` | Configuration class | Config classes |
| `@Bean` | Register a bean manually | Inside @Configuration |

---

## 📊 Entity Annotations

### Class-Level

```java
@Entity                                    // Mark as JPA entity
@Table(name = "users")                     // Specify table name
@MappedSuperclass                          // Parent class (not a table)
public class User { }
```

### Property-Level

```java
@Id                                        // Primary key
@GeneratedValue(strategy = GenerationType.IDENTITY)  // Auto-increment
@Column(name = "email", nullable = false)  // Column properties
@Transient                                 // Not a column (ignored)
@CreationTimestamp                         // Auto-set creation time
@UpdateTimestamp                           // Auto-set update time
private LocalDateTime createdAt;
```

### Relationships

```java
// One-to-Many: Parent has many children
@OneToMany(cascade = CascadeType.ALL, mappedBy = "parent")
@OrderBy("name")
private List<Child> children;

// Many-to-One: Child belongs to one parent
@ManyToOne
@JoinColumn(name = "parent_id")
private Parent parent;

// Many-to-Many: Bidirectional relationship
@ManyToMany(fetch = FetchType.EAGER)
@JoinTable(
    name = "user_roles",
    joinColumns = @JoinColumn(name = "user_id"),
    inverseJoinColumns = @JoinColumn(name = "role_id")
)
private Set<Role> roles;
```

### Validation

```java
@NotNull                                   // Cannot be null
@NotBlank                                  // Cannot be empty or whitespace
@NotEmpty                                  // Cannot be empty
@Email                                     // Must be valid email
@Pattern(regexp = "...")                   // Match regex
@Size(min = 5, max = 50)                   // String length
@Min(value = 18)                           // Minimum value
@Max(value = 100)                          // Maximum value
@Past                                      // Date in the past
@Future                                    // Date in the future
@DateTimeFormat(pattern = "yyyy-MM-dd")    // Date format
private LocalDate birthDate;
```

---

## 📦 Repository Annotations

### Method Naming Convention

```java
public interface UserRepository extends JpaRepository<User, Long> {
    
    // FIND QUERIES
    User findByEmail(String email);                    // =
    List<User> findByFirstNameAndLastName(..., ...);  // AND
    List<User> findByAgeGreaterThan(int age);         // >
    List<User> findByAgeLessThanOrEqual(int age);     // <=
    List<User> findByFirstNameContaining(String name);// LIKE %name%
    List<User> findByFirstNameStartingWith(String prefix);  // LIKE prefix%
    List<User> findByFirstNameEndingWith(String suffix);    // LIKE %suffix
    
    // ORDERING
    List<User> findAllByOrderByLastNameAsc();
    List<User> findAllByOrderByAgeDesc();
    
    // PAGINATION
    Page<User> findByAge(int age, Pageable pageable);
    Slice<User> findByFirstName(String name, Pageable pageable);
    
    // EXISTS/COUNT
    boolean existsByEmail(String email);
    long countByAge(int age);
    
    // DELETE
    void deleteByEmail(String email);
    long deleteByAge(int age);
    
    // CUSTOM QUERIES
    @Query("SELECT u FROM User u WHERE u.email = ?1")
    User findByEmailCustom(String email);
    
    @Query("SELECT u FROM User u WHERE u.age > :minAge ORDER BY u.lastName")
    List<User> findAdultUsers(@Param("minAge") int minAge);
    
    // NATIVE SQL
    @Query(value = "SELECT * FROM users WHERE email = ?1", nativeQuery = true)
    User findUserByEmail(String email);
}
```

---

## 🎮 Controller Annotations

### Request Mapping

```java
@RestController
@RequestMapping("/api/users")              // Base URL
@RequestMapping(method = RequestMethod.GET)  // HTTP method (old style)
public class UserController {
    
    // GET REQUESTS
    @GetMapping                             // GET /api/users
    public List<User> getAll() { }
    
    @GetMapping("/{id}")                    // GET /api/users/{id}
    public User getById(@PathVariable Long id) { }
    
    @GetMapping("/email/{email}")           // GET /api/users/email/john@example.com
    public User getByEmail(@PathVariable String email) { }
    
    // POST REQUESTS
    @PostMapping                            // POST /api/users
    public User create(@RequestBody User user) { }
    
    // PUT REQUESTS
    @PutMapping("/{id}")                    // PUT /api/users/{id}
    public User update(@PathVariable Long id, @RequestBody User user) { }
    
    // DELETE REQUESTS
    @DeleteMapping("/{id}")                 // DELETE /api/users/{id}
    public void delete(@PathVariable Long id) { }
    
    // PATCH REQUESTS
    @PatchMapping("/{id}")                  // PATCH /api/users/{id}
    public User partialUpdate(@PathVariable Long id, @RequestBody User user) { }
}
```

### Parameter Binding

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    // Path variables
    @GetMapping("/{id}")
    public User get(@PathVariable("id") Long userId) { }  // From URL path
    
    // Query parameters
    @GetMapping
    public List<User> search(@RequestParam String name,
                             @RequestParam(required = false) Integer age) { }
    // GET /api/users?name=john&age=30
    
    // Request body
    @PostMapping
    public User create(@RequestBody User user) { }        // From request body
    
    // Headers
    @GetMapping
    public User get(@RequestHeader("Authorization") String token) { }
    
    // Default values
    @GetMapping
    public List<User> list(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size) { }
    
    // Optional
    @GetMapping("/{id}")
    public User get(@PathVariable Optional<Long> id) { }
}
```

### Response Control

```java
@RestController
public class UserController {
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)     // 201 Created (instead of 200)
    public User create(@RequestBody User user) { }
    
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)  // 204 No Content
    public void delete(@PathVariable Long id) { }
    
    // Return ResponseEntity for full control
    @GetMapping("/{id}")
    public ResponseEntity<User> get(@PathVariable Long id) {
        User user = userService.get(id);
        if (user == null) {
            return ResponseEntity.notFound().build();    // 404
        }
        return ResponseEntity.ok(user);                  // 200 + body
    }
    
    @PostMapping
    public ResponseEntity<User> create(@RequestBody User user) {
        User saved = userService.save(user);
        return ResponseEntity
            .created(URI.create("/users/" + saved.getId()))
            .body(saved);
    }
}
```

---

## 🔄 Dependency Injection Patterns

### Constructor Injection (Recommended)

```java
@Service
public class UserService {
    
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    // Constructor injection (best practice)
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}
```

### Setter Injection

```java
@Service
public class UserService {
    
    private UserRepository userRepository;
    
    @Autowired
    public void setUserRepository(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}
```

### Field Injection

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;  // Less testable
}
```

---

## 🔍 Repository Query Examples

### Derived Query Examples

```java
// Given entities:
@Entity
public class User {
    private String firstName;
    private String lastName;
    private int age;
    private String email;
}

@Entity
public class Post {
    private String title;
    @ManyToOne
    private User author;
}

public interface UserRepository extends JpaRepository<User, Long> {
    
    // ===== SIMPLE QUERIES =====
    User findByEmail(String email);                    // Single result
    List<User> findByLastName(String name);            // Multiple results
    
    // ===== COMPOUND CONDITIONS =====
    List<User> findByFirstNameAndLastName(String fname, String lname);
    List<User> findByFirstNameOrEmail(String name, String email);
    
    // ===== COMPARISONS =====
    List<User> findByAgeGreaterThan(int age);         // age > ?
    List<User> findByAgeGreaterThanEqual(int age);    // age >= ?
    List<User> findByAgeLessThan(int age);            // age < ?
    List<User> findByAgeLessThanEqual(int age);       // age <= ?
    List<User> findByAgeBetween(int min, int max);    // age between
    
    // ===== STRING OPERATIONS =====
    List<User> findByFirstNameContaining(String text);     // LIKE %text%
    List<User> findByFirstNameNotContaining(String text);  // NOT LIKE %text%
    List<User> findByFirstNameStartingWith(String prefix); // LIKE prefix%
    List<User> findByFirstNameEndingWith(String suffix);   // LIKE %suffix
    
    // ===== NEGATION =====
    List<User> findByAgeNot(int age);                 // age != ?
    List<User> findByEmailIsNull();
    List<User> findByEmailIsNotNull();
    List<User> findByEmailIsNot(String email);
    
    // ===== COLLECTIONS =====
    List<User> findByAgeIn(List<Integer> ages);       // age IN (?, ?, ?)
    List<User> findByAgeNotIn(List<Integer> ages);
    
    // ===== ORDERING =====
    List<User> findAllByOrderByAgeAsc();
    List<User> findAllByOrderByAgeDesc();
    List<User> findByLastNameOrderByFirstNameAsc(String lastName);
    
    // ===== PAGINATION =====
    Page<User> findByAge(int age, Pageable pageable);
    
    // ===== RELATIONSHIPS =====
    List<User> findByEmail(String email);
    List<Post> findByAuthorEmail(String email);       // Via relationship
}
```

---

## 📋 Service Layer Patterns

### Basic Service Pattern

```java
@Service
public class UserService {
    
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
    
    // CREATE
    @Transactional
    public User create(UserCreateRequest request) {
        // Validation
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new UserAlreadyExistsException("Email already in use");
        }
        
        // Business logic
        User user = new User();
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setEmail(request.getEmail());
        user.setPassword(encryptPassword(request.getPassword()));
        
        // Persist
        User saved = userRepository.save(user);
        
        // Side effects (send email, etc)
        emailService.sendWelcomeEmail(saved);
        
        return saved;
    }
    
    // READ
    public User getById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
    }
    
    // UPDATE
    @Transactional
    public User update(Long id, UserUpdateRequest request) {
        User user = getById(id);
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        return userRepository.save(user);
    }
    
    // DELETE
    @Transactional
    public void delete(Long id) {
        User user = getById(id);
        userRepository.delete(user);
    }
    
    // LIST with pagination
    public Page<User> listAll(Pageable pageable) {
        return userRepository.findAll(pageable);
    }
    
    // SEARCH
    public List<User> search(String keyword) {
        return userRepository.findByFirstNameContainingOrLastNameContaining(keyword, keyword);
    }
}
```

### Transaction Management

```java
@Service
public class OrderService {
    
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;
    private final NotificationService notificationService;
    
    // Automatic rollback if exception occurs
    @Transactional
    public Order placeOrder(OrderCreateRequest request) {
        // 1. Create order
        Order order = new Order();
        order.setTotal(request.getTotal());
        Order saved = orderRepository.save(order);
        
        // 2. Process payment (if fails, entire transaction rolls back)
        paymentService.charge(saved.getId(), saved.getTotal());
        
        // 3. Send notification
        notificationService.sendOrderConfirmation(saved);
        
        return saved;  // All changes committed
    }
    
    // Read-only (no transaction needed)
    @Transactional(readOnly = true)
    public List<Order> getUserOrders(Long userId) {
        return orderRepository.findByUserId(userId);
    }
}
```

---

## 🛡️ Exception Handling

### Custom Exceptions

```java
public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String message) {
        super(message);
    }
}

public class UserAlreadyExistsException extends RuntimeException {
    public UserAlreadyExistsException(String message) {
        super(message);
    }
}
```

### Global Exception Handler

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleUserNotFound(UserNotFoundException ex) {
        return new ErrorResponse("NOT_FOUND", ex.getMessage());
    }
    
    @ExceptionHandler(UserAlreadyExistsException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public ErrorResponse handleUserAlreadyExists(UserAlreadyExistsException ex) {
        return new ErrorResponse("CONFLICT", ex.getMessage());
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidationError(MethodArgumentNotValidException ex) {
        return new ErrorResponse("BAD_REQUEST", "Validation failed");
    }
}
```

---

## 🔒 Validation Example

```java
@Service
public class UserService {
    
    @Transactional
    public User create(@Valid UserCreateRequest request, BindingResult result) {
        // Manual validation
        if (result.hasErrors()) {
            throw new ValidationException(result.getFieldError().getDefaultMessage());
        }
        
        // Business validation
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new UserAlreadyExistsException("Email already in use");
        }
        
        // Create and save
        User user = new User();
        user.setEmail(request.getEmail());
        return userRepository.save(user);
    }
}

// Request DTO with validations
@Data
public class UserCreateRequest {
    
    @NotBlank(message = "First name is required")
    private String firstName;
    
    @NotBlank(message = "Last name is required")
    private String lastName;
    
    @Email(message = "Email must be valid")
    private String email;
    
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$",
             message = "Password must be 8+ chars with letters and numbers")
    private String password;
}
```

---

## 📝 Common Code Templates

### CREATE Entity + Repository + Service + Controller

**1. Entity**
```java
@Entity
@Table(name = "products")
public class Product extends BaseEntity {
    
    @Column(nullable = false)
    @NotBlank
    private String name;
    
    @Column
    private String description;
    
    @Column(nullable = false)
    @Min(0)
    private BigDecimal price;
}
```

**2. Repository**
```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByNameContaining(String name);
    List<Product> findByPriceLessThan(BigDecimal price);
}
```

**3. Service**
```java
@Service
public class ProductService {
    
    private final ProductRepository productRepository;
    
    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }
    
    @Transactional
    public Product create(ProductCreateRequest request) {
        Product product = new Product();
        product.setName(request.getName());
        product.setDescription(request.getDescription());
        product.setPrice(request.getPrice());
        return productRepository.save(product);
    }
    
    public Product getById(Long id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Product not found"));
    }
    
    public List<Product> search(String keyword) {
        return productRepository.findByNameContaining(keyword);
    }
}
```

**4. Controller**
```java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    private final ProductService productService;
    
    public ProductController(ProductService productService) {
        this.productService = productService;
    }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ProductDto create(@Valid @RequestBody ProductCreateRequest request) {
        Product product = productService.create(request);
        return new ProductDto(product);
    }
    
    @GetMapping("/{id}")
    public ProductDto getById(@PathVariable Long id) {
        Product product = productService.getById(id);
        return new ProductDto(product);
    }
    
    @GetMapping
    public List<ProductDto> search(@RequestParam String keyword) {
        return productService.search(keyword)
            .stream()
            .map(ProductDto::new)
            .toList();
    }
}
```

---

## 🎯 Quick Tips

1. **Always use constructor injection** — More testable, clearer dependencies
2. **Make services immutable** — Use `final` for dependencies
3. **Validate at service layer** — Not just at controller
4. **Use @Transactional carefully** — Can hide performance issues
5. **Name repositories clearly** — `findBy*`, `existsBy*`, `countBy*`
6. **Use DTOs** — Don't expose entities directly in APIs
7. **Return proper HTTP status codes** — Not everything is 200 OK
8. **Use @RestControllerAdvice** — Centralize exception handling
9. **Write meaningful error messages** — Help API consumers debug
10. **Keep methods small and focused** — Single responsibility principle

---

## 📚 Related Study Materials

- [Spring Boot Layers & Concepts](spring-boot-layers-and-concepts.md)
- [Spring Pet Clinic Guide](spring-petclinic-reverse-engineering-guide.md)
- [Complete Learning Roadmap](spring-boot-complete-learning-roadmap.md)

---
