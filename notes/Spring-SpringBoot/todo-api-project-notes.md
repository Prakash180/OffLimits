# Todo API Project — Learning Notes

## Session 1: Project Setup & Architecture

### What We Built
- A complete Spring Boot REST API with 4 layers:
  - **Controller** (`@RestController`) — HTTP endpoints
  - **Service** (`@Service`) — Business logic
  - **Repository** (`@Repository`) — Database access
  - **Entity** (`@Entity`) — Data model

### Dependencies Used
- `spring-boot-starter-web` — For REST API
- `spring-boot-starter-data-jpa` — For database operations
- `h2` — In-memory database for development
- `lombok` — Reduces boilerplate code

### Key Takeaways

#### 1. Layered Architecture
```
Controller (HTTP)
    ↓
Service (Business Logic)
    ↓
Repository (Database)
```

Each layer has a specific responsibility — makes code organized and testable.

#### 2. Constructor Injection
We used constructor injection in both `TodoService` and `TodoController`:
```java
public TodoService(TodoRepository todoRepository) {
    this.todoRepository = todoRepository;
}
```

**Why?**
- Spring automatically wires dependencies
- Final variables can't be accidentally changed
- Easier to test (can pass mock objects)

#### 3. JpaRepository Magic
```java
public interface TodoRepository extends JpaRepository<Todo, Long> { ... }
```

`JpaRepository` automatically provides:
- `save()` — Create/Update
- `findById()` — Retrieve by ID
- `findAll()` — Retrieve all
- `deleteById()` — Delete
- Custom queries we define (`findByCompleted()`, `findByPriority()`)

#### 4. Spring Data JPA Custom Queries
```java
List<Todo> findByCompleted(boolean completed);
List<Todo> findByPriority(String priority);
```

Spring automatically generates SQL from method names! No need to write SQL.

### Next Steps
1. Run the project and test the endpoints
2. Add validation (validate input data)
3. Add exception handling (handle errors gracefully)
4. Add unit tests
5. Learn about authentication & security

---

## How to Extend This Project

### Adding User Accounts
```java
// User entity with one-to-many relationship to todos
@Entity
public class User {
    @Id
    private Long id;
    private String username;
    
    @OneToMany(mappedBy = "user")
    private List<Todo> todos;
}

// Todo entity modified
@Entity
public class Todo {
    ...
    @ManyToOne
    private User user;  // ← Link todo to user
}
```

### Adding Validation
```java
public class Todo {
    @NotBlank(message = "Title cannot be blank")
    private String title;
    
    @Size(min = 1, max = 500)
    private String description;
}
```

### Adding Global Exception Handling
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<String> handleNotFound(EntityNotFoundException e) {
        return new ResponseEntity<>(e.getMessage(), HttpStatus.NOT_FOUND);
    }
}
```

### Adding Pagination
```java
// In controller
@GetMapping
public Page<Todo> getAllTodos(
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "10") int size
) {
    return todoService.getTodos(PageRequest.of(page, size));
}
```

---

## Common Issues & Solutions

| Issue | Solution |
|---|---|
| "Could not find h2 dependency" | Make sure Gradle is configured correctly; run `./gradlew build` |
| "Port 8080 already in use" | Change port in `application.properties`: `server.port=8081` |
| "POST endpoint not accepting JSON" | Add `@RequestBody` annotation to method parameter |
| "Database queries not showing" | Enable in `application.properties`: `spring.jpa.show-sql=true` |

