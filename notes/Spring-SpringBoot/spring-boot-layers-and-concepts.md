# Spring Boot Layers & Core Concepts — Complete Guide

This guide covers the 5 essential layers in a Spring Boot application and the key concepts you need to master.

---

## Quick Reference: The 5 Layers

| Layer | Purpose | Annotations | Scope |
|-------|---------|-------------|-------|
| **Controller** | HTTP entry point | `@RestController`, `@RequestMapping` | Request/Response handling |
| **Service** | Business logic | `@Service` | Core application logic |
| **Repository** | Database access | `@Repository` | CRUD operations |
| **Entity** | Data model | `@Entity`, `@Table` | Database table representation |
| **Configuration** | App setup | `@Configuration`, `@Bean` | Spring initialization |

---

## LAYER 1: ENTITY (Data Model)

### What is an Entity?
An **Entity** is a Java class that represents a **database table**.
- Each entity = one table
- Each property = one column
- Each instance = one row

### Key Annotations

| Annotation | Purpose |
|-----------|---------|
| `@Entity` | Marks this class as a JPA entity (will map to database) |
| `@Table(name="...")` | Specifies table name (optional; defaults to class name) |
| `@Id` | Marks the primary key column |
| `@GeneratedValue(strategy=...)` | Auto-generates ID values |
| `@Column(name="...")` | Specifies column name and properties |
| `@OneToMany`, `@ManyToOne` | Defines relationships between entities |
| `@JoinColumn(name="...")` | Foreign key column name |

### Example 1: Simple User Entity

```java
package com.example.todos.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "username", nullable = false, unique = true)
    private String username;
    
    @Column(name = "email", nullable = false, unique = true)
    private String email;
    
    @Column(name = "password", nullable = false)
    private String password;
    
    // Getters & Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
```

**Database Table Generated:**
```
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

### Example 2: Todo Entity with Relationship

```java
package com.example.todos.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "todos")
public class Todo {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "title", nullable = false)
    private String title;
    
    @Column(name = "description")
    private String description;
    
    @Column(name = "completed", nullable = false)
    private Boolean completed = false;
    
    // Relationship: Many todos belong to one user
    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    // Getters & Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public Boolean getCompleted() { return completed; }
    public void setCompleted(Boolean completed) { this.completed = completed; }
    
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
}
```

**Database Table Generated:**
```
CREATE TABLE todos (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Key Concepts
- **@Entity** tells Spring this is a mapped database entity
- **@Id** defines the primary key
- **@GeneratedValue** auto-increments the ID
- **@ManyToOne** = "many todos belong to one user"
- **@JoinColumn** specifies the foreign key column name
- **nullable = false** makes the column required (NOT NULL in SQL)
- **unique = true** ensures values are unique (UNIQUE constraint)

---

## LAYER 2: REPOSITORY (Data Access)

### What is a Repository?
A **Repository** is an interface that handles all database operations (CRUD = Create, Read, Update, Delete).
- You don't write SQL queries (usually)
- Spring Data JPA generates SQL for you
- Simplifies database interaction

### Why Separate Repository from Service?
- **Separation of Concerns** — Repository = "how to access data", Service = "what to do with data"
- **Testability** — Easy to mock database operations
- **Reusability** — Multiple services can use the same repository
- **Maintainability** — Database changes only affect repository

### Built-in Methods (from JpaRepository)

```java
// All these are FREE — you don't write implementation!
List<T> findAll();                    // Get all records
T findById(ID id);                    // Get one by ID
T save(T entity);                     // Insert or update
void deleteById(ID id);               // Delete by ID
void delete(T entity);                // Delete entity
boolean existsById(ID id);            // Check if exists
long count();                         // Count all records
```

### Example: User Repository

```java
package com.example.todos.repository;

import com.example.todos.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // Custom query methods (Spring generates SQL automatically)
    User findByUsername(String username);
    User findByEmail(String email);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}
```

**How Spring generates these methods:**
- `findByUsername(String username)` → `SELECT * FROM users WHERE username = ?`
- `findByEmail(String email)` → `SELECT * FROM users WHERE email = ?`
- `existsByUsername(String username)` → `SELECT COUNT(*) > 0 FROM users WHERE username = ?`

### Example: Todo Repository

```java
package com.example.todos.repository;

import com.example.todos.entity.Todo;
import com.example.todos.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface TodoRepository extends JpaRepository<Todo, Long> {
    
    // Find all todos for a specific user
    List<Todo> findByUser(User user);
    
    // Find all completed todos for a user
    List<Todo> findByUserAndCompletedTrue(User user);
    
    // Find all incomplete todos for a user
    List<Todo> findByUserAndCompletedFalse(User user);
    
    // Count completed todos for a user
    long countByUserAndCompletedTrue(User user);
}
```

### Key Concepts
- **@Repository** marks this as a data access component
- **JpaRepository<T, ID>** — T = entity class, ID = primary key type
- Custom methods follow naming convention: `findBy[FieldName]`, `countBy[FieldName]`
- Spring automatically implements these methods — you only define the interface!

---

## LAYER 3: SERVICE (Business Logic)

### What is a Service?
A **Service** contains the **business logic** of your application.
- Validates data
- Performs calculations
- Orchestrates operations
- Handles errors
- Uses repositories to access data

### Why Separate Service from Controller?
- **Controller** should only handle HTTP (not business logic)
- **Service** can be reused by multiple controllers
- **Service** can be tested independently
- **Service** knows nothing about HTTP — it's pure Java logic

### Example: User Service

```java
package com.example.todos.service;

import com.example.todos.entity.User;
import com.example.todos.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    // Create a new user
    public User createUser(String username, String email, String password) {
        // Validate input
        if (username == null || username.isEmpty()) {
            throw new IllegalArgumentException("Username cannot be empty");
        }
        if (email == null || email.isEmpty()) {
            throw new IllegalArgumentException("Email cannot be empty");
        }
        if (password == null || password.length() < 6) {
            throw new IllegalArgumentException("Password must be at least 6 characters");
        }
        
        // Check if user already exists
        if (userRepository.existsByUsername(username)) {
            throw new IllegalArgumentException("Username already exists");
        }
        if (userRepository.existsByEmail(email)) {
            throw new IllegalArgumentException("Email already exists");
        }
        
        // Create user
        User user = new User();
        user.setUsername(username);
        user.setEmail(email);
        user.setPassword(password); // In real app, HASH this password!
        
        // Save to database
        return userRepository.save(user);
    }
    
    // Get user by ID
    public User getUserById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new IllegalArgumentException("User not found with id: " + id));
    }
    
    // Get user by username
    public User getUserByUsername(String username) {
        User user = userRepository.findByUsername(username);
        if (user == null) {
            throw new IllegalArgumentException("User not found with username: " + username);
        }
        return user;
    }
    
    // Update user
    public User updateUser(Long id, String username, String email) {
        User user = getUserById(id);
        if (username != null && !username.isEmpty()) {
            user.setUsername(username);
        }
        if (email != null && !email.isEmpty()) {
            user.setEmail(email);
        }
        return userRepository.save(user);
    }
    
    // Delete user
    public void deleteUser(Long id) {
        User user = getUserById(id);
        userRepository.delete(user);
    }
}
```

### Example: Todo Service

```java
package com.example.todos.service;

import com.example.todos.entity.Todo;
import com.example.todos.entity.User;
import com.example.todos.repository.TodoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class TodoService {
    
    @Autowired
    private TodoRepository todoRepository;
    
    @Autowired
    private UserService userService;
    
    // Create a new todo
    public Todo createTodo(Long userId, String title, String description) {
        // Validate input
        if (title == null || title.isEmpty()) {
            throw new IllegalArgumentException("Title cannot be empty");
        }
        
        // Get user (and verify they exist)
        User user = userService.getUserById(userId);
        
        // Create todo
        Todo todo = new Todo();
        todo.setTitle(title);
        todo.setDescription(description);
        todo.setCompleted(false);
        todo.setUser(user);
        
        return todoRepository.save(todo);
    }
    
    // Get all todos for a user
    public List<Todo> getTodosByUser(Long userId) {
        User user = userService.getUserById(userId);
        return todoRepository.findByUser(user);
    }
    
    // Get completed todos for a user
    public List<Todo> getCompletedTodos(Long userId) {
        User user = userService.getUserById(userId);
        return todoRepository.findByUserAndCompletedTrue(user);
    }
    
    // Get incomplete todos for a user
    public List<Todo> getIncompleteTodos(Long userId) {
        User user = userService.getUserById(userId);
        return todoRepository.findByUserAndCompletedFalse(user);
    }
    
    // Mark todo as complete
    public Todo completeTodo(Long todoId) {
        Todo todo = todoRepository.findById(todoId)
            .orElseThrow(() -> new IllegalArgumentException("Todo not found with id: " + todoId));
        todo.setCompleted(true);
        return todoRepository.save(todo);
    }
    
    // Mark todo as incomplete
    public Todo incompleteTodo(Long todoId) {
        Todo todo = todoRepository.findById(todoId)
            .orElseThrow(() -> new IllegalArgumentException("Todo not found with id: " + todoId));
        todo.setCompleted(false);
        return todoRepository.save(todo);
    }
}
```

### Key Concepts
- **@Service** marks this as a business logic component
- **@Autowired** injects the repository
- Service contains validation, error handling, complex logic
- Service doesn't know about HTTP — it's reusable Java code
- Service throws exceptions — controller decides how to respond

---

## LAYER 4: CONTROLLER (HTTP Endpoint)

### What is a Controller?
A **Controller** handles HTTP requests and returns HTTP responses.
- Receives HTTP requests (GET, POST, PUT, DELETE)
- Calls service methods
- Returns HTTP responses (JSON)
- Handles routing

### @RestController vs @Controller

| | @RestController | @Controller |
|---|---|---|
| Response type | JSON (default) | HTML page |
| When to use | REST APIs | MVC web apps with views |
| Annotation | `@RestController` | `@Controller` |
| Returns | Objects (auto JSON) | View names (HTML) |

**For REST APIs: always use @RestController**

### HTTP Methods Mapping

| Method | Purpose | Annotation | Use Case |
|--------|---------|-----------|----------|
| GET | Retrieve data | `@GetMapping` | Get user, list todos |
| POST | Create new data | `@PostMapping` | Create new user |
| PUT | Update existing data | `@PutMapping` | Update user info |
| DELETE | Delete data | `@DeleteMapping` | Delete todo |

### Example: User Controller

```java
package com.example.todos.controller;

import com.example.todos.entity.User;
import com.example.todos.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")  // Base URL: /api/users
public class UserController {
    
    @Autowired
    private UserService userService;
    
    // POST /api/users
    // Create new user
    @PostMapping
    public User createUser(
            @RequestParam String username,
            @RequestParam String email,
            @RequestParam String password) {
        return userService.createUser(username, email, password);
    }
    
    // GET /api/users/{id}
    // Get user by ID
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) {
        return userService.getUserById(id);
    }
    
    // GET /api/users/username/{username}
    // Get user by username
    @GetMapping("/username/{username}")
    public User getUserByUsername(@PathVariable String username) {
        return userService.getUserByUsername(username);
    }
    
    // PUT /api/users/{id}
    // Update user
    @PutMapping("/{id}")
    public User updateUser(
            @PathVariable Long id,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String email) {
        return userService.updateUser(id, username, email);
    }
    
    // DELETE /api/users/{id}
    // Delete user
    @DeleteMapping("/{id}")
    public String deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return "User deleted successfully";
    }
}
```

### Example: Todo Controller

```java
package com.example.todos.controller;

import com.example.todos.entity.Todo;
import com.example.todos.service.TodoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/todos")  // Base URL: /api/todos
public class TodoController {
    
    @Autowired
    private TodoService todoService;
    
    // POST /api/todos
    // Create new todo
    @PostMapping
    public Todo createTodo(
            @RequestParam Long userId,
            @RequestParam String title,
            @RequestParam(required = false) String description) {
        return todoService.createTodo(userId, title, description);
    }
    
    // GET /api/todos/user/{userId}
    // Get all todos for a user
    @GetMapping("/user/{userId}")
    public List<Todo> getTodosByUser(@PathVariable Long userId) {
        return todoService.getTodosByUser(userId);
    }
    
    // GET /api/todos/user/{userId}/completed
    // Get completed todos
    @GetMapping("/user/{userId}/completed")
    public List<Todo> getCompletedTodos(@PathVariable Long userId) {
        return todoService.getCompletedTodos(userId);
    }
    
    // GET /api/todos/user/{userId}/incomplete
    // Get incomplete todos
    @GetMapping("/user/{userId}/incomplete")
    public List<Todo> getIncompleteTodos(@PathVariable Long userId) {
        return todoService.getIncompleteTodos(userId);
    }
    
    // PUT /api/todos/{id}/complete
    // Mark todo as complete
    @PutMapping("/{id}/complete")
    public Todo completeTodo(@PathVariable Long id) {
        return todoService.completeTodo(id);
    }
    
    // PUT /api/todos/{id}/incomplete
    // Mark todo as incomplete
    @PutMapping("/{id}/incomplete")
    public Todo incompleteTodo(@PathVariable Long id) {
        return todoService.incompleteTodo(id);
    }
}
```

### Key Annotations Explained

| Annotation | Purpose | Example |
|-----------|---------|---------|
| `@RestController` | Marks class as HTTP handler, returns JSON | `@RestController` |
| `@RequestMapping` | Base URL path | `@RequestMapping("/api/users")` |
| `@GetMapping` | Handles GET requests | `@GetMapping("/{id}")` |
| `@PostMapping` | Handles POST requests | `@PostMapping` |
| `@PutMapping` | Handles PUT requests | `@PutMapping("/{id}")` |
| `@DeleteMapping` | Handles DELETE requests | `@DeleteMapping("/{id}")` |
| `@PathVariable` | Gets value from URL path | `@PathVariable Long id` |
| `@RequestParam` | Gets value from query string | `@RequestParam String username` |

### Example API Calls (Using curl or Postman)

```bash
# Create user
curl -X POST "http://localhost:8080/api/users?username=john&email=john@example.com&password=pass123"

# Get user by ID
curl -X GET "http://localhost:8080/api/users/1"

# Create todo
curl -X POST "http://localhost:8080/api/todos?userId=1&title=Learn Spring&description=Study Spring Boot"

# Get todos for user
curl -X GET "http://localhost:8080/api/todos/user/1"

# Mark todo as complete
curl -X PUT "http://localhost:8080/api/todos/1/complete"

# Delete user
curl -X DELETE "http://localhost:8080/api/users/1"
```

### Key Concepts
- **@RestController** = HTTP entry point
- **@RequestMapping** = base URL
- **@PathVariable** = gets value from URL path (e.g., `/users/{id}`)
- **@RequestParam** = gets value from query string (e.g., `?username=john`)
- Controller should NOT contain business logic — delegate to service
- Controller's job: parse HTTP request → call service → return response

---

## LAYER 5: CONFIGURATION

### What is Configuration?
Configuration tells Spring how to set up your application.
- Database connection
- Enable certain features
- Create beans
- Set properties

### Key Files

#### application.properties
```properties
# Server settings
server.port=8080

# Database settings (H2 - in-memory)
spring.datasource.url=jdbc:h2:mem:tododb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA/Hibernate settings
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create-drop  # Auto-create/drop tables
spring.jpa.show-sql=true                   # Print SQL queries

# Logging settings
logging.level.root=INFO
logging.level.com.example.todos=DEBUG
```

#### Database Configuration (Optional - More Control)

```java
package com.example.todos.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Bean;
import javax.sql.DataSource;
import org.springframework.boot.jdbc.DataSourceBuilder;

@Configuration
public class DatabaseConfig {
    
    @Bean
    public DataSource dataSource() {
        return DataSourceBuilder.create()
            .driverClassName("org.h2.Driver")
            .url("jdbc:h2:mem:tododb")
            .username("sa")
            .password("")
            .build();
    }
}
```

### Key Concepts
- `@Configuration` marks the class as a configuration component
- `@Bean` tells Spring to create an object and manage it
- `application.properties` is the easiest way to configure basics
- Configuration files are loaded automatically on startup

---

## COMPLETE REQUEST FLOW (Example)

Let's trace a request from start to finish:

### Scenario: Create a new user

**1. HTTP Request**
```
POST /api/users?username=john&email=john@example.com&password=pass123
```

**2. Controller receives request**
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @PostMapping
    public User createUser(
            @RequestParam String username,
            @RequestParam String email,
            @RequestParam String password) {
        // Called here
        return userService.createUser(username, email, password);
    }
}
```

**3. Service processes business logic**
```java
@Service
public class UserService {
    public User createUser(String username, String email, String password) {
        // Validate
        if (username == null) throw new IllegalArgumentException("...");
        
        // Check if exists
        if (userRepository.existsByUsername(username)) 
            throw new IllegalArgumentException("...");
        
        // Create object
        User user = new User();
        user.setUsername(username);
        user.setEmail(email);
        user.setPassword(password);
        
        // Save to database
        return userRepository.save(user);  // Called here
    }
}
```

**4. Repository saves to database**
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    // Spring automatically calls SQL INSERT
    // INSERT INTO users (username, email, password) VALUES (?, ?, ?)
}
```

**5. Database stores data**
```
users table:
id | username | email              | password
1  | john     | john@example.com   | pass123
```

**6. Response returned**
```json
{
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "password": "pass123"
}
```

---

## Common Dependencies (build.gradle)

```gradle
dependencies {
    // Spring Web (REST APIs)
    implementation 'org.springframework.boot:spring-boot-starter-web'
    
    // Spring Data JPA (Database ORM)
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    
    // Jakarta Persistence (replaces javax.persistence)
    implementation 'jakarta.persistence:jakarta.persistence-api'
    
    // H2 Database (development/testing)
    runtimeOnly 'com.h2database:h2'
    
    // Logging
    implementation 'org.springframework.boot:spring-boot-starter-logging'
    
    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

---

## Summary: Layers Quick Recap

```
REQUEST FLOW:
Client Browser/Postman
    ↓
HTTP Request
    ↓
┌─────────────────────┐
│ CONTROLLER          │  ← Receives HTTP request
│ (Parses, Validates) │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ SERVICE             │  ← Business logic, calculations
│ (Business Rules)    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ REPOSITORY          │  ← CRUD operations
│ (Data Access)       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ DATABASE            │  ← Stores persistent data
│ (SQL Tables)        │
└─────────────────────┘
    ↓
RESPONSE:
HTTP 200 JSON
    ↓
Client Browser/Postman
```

---

## Next Steps to Learn

1. **Build a simple Todo App** — User and Todo entities
2. **Write CRUD Repositories** — findBy methods
3. **Write Services** — validation and business logic
4. **Write Controllers** — expose as REST API
5. **Test endpoints** — use Postman or curl
6. **Add relationships** — OneToMany, ManyToOne
7. **Error handling** — Custom exceptions and error responses
8. **Authentication** — Spring Security (later)
9. **Data validation** — @NotNull, @Email, etc.
10. **Pagination & filtering** — Large datasets

---
