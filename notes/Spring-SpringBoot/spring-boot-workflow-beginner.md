# Spring Boot Development Workflow — Beginner's Guide

A step-by-step workflow to build Spring Boot applications correctly, from planning to deployment.

---

## 1. PROJECT PLANNING (Before You Code)

### Questions to Answer
- **What is the app?** (e.g., Todo API, User Management System)
- **What data do we store?** (e.g., Todos, Users, Posts)
- **What operations do we need?** (CRUD: Create, Read, Update, Delete)
- **Who uses it?** (Web browsers, mobile apps, other servers)

### For Multi-Table Todo + Blog System:
- ✅ App: Task & blog management system with users
- ✅ Data:
  - Users (username, email, password)
  - Todos (title, description, completed, priority, belongs to user)
  - Posts (title, content, author)
  - Comments (text, belongs to post, written by user)
- ✅ Operations: CRUD for all entities + filter by user, status, etc.
- ✅ Users: Frontend apps, Postman, curl

---

## 2. ARCHITECTURE DESIGN (Think Before Building)

### Layered Architecture Pattern

```
┌─────────────────────────────────────────┐
│         HTTP Layer (Browser/Client)     │
└────────────────────┬────────────────────┘
                     │
┌─────────────────────────────────────────┐
│    Controller Layer (@RestController)   │  ← Handles HTTP requests/responses
│    - Routes incoming requests           │
│    - Validates inputs                   │
│    - Returns responses (JSON)           │
└────────────────────┬────────────────────┘
                     │
┌─────────────────────────────────────────┐
│     Service Layer (@Service)            │  ← Contains business logic
│    - Business rules                     │
│    - Data processing                    │
│    - Complex calculations               │
└────────────────────┬────────────────────┘
                     │
┌─────────────────────────────────────────┐
│    Repository Layer (@Repository)       │  ← Database operations
│    - CRUD operations                    │
│    - Queries                            │
│    - Exception translation              │
└────────────────────┬────────────────────┘
                     │
┌─────────────────────────────────────────┐
│       Database (H2 / MySQL / etc)       │  ← Stores persistent data
│  ┌──────────┐  ┌──────────┐             │
│  │ Users    │  │ Posts    │             │
│  └──────────┘  └──────────┘             │
│  ┌──────────┐  ┌──────────┐             │
│  │ Todos    │  │ Comments │             │
│  └──────────┘  └──────────┘             │
└─────────────────────────────────────────┘
```

### Multi-Table Relationships

```
User (1) ────────── (Many) Todos
  │                    
  ├─────────────── (Many) Posts
  │                    
  └─────────────── (Many) Comments

Post (1) ────────── (Many) Comments
```

**Entity Relationships:**
- **User → Todos:** One user has many todos (1:N)
- **User → Posts:** One user has many posts (1:N)
- **User → Comments:** One user writes many comments (1:N)
- **Post → Comments:** One post has many comments (1:N)

### Why This Structure?
- **Separation of Concerns** — Each layer has one job
- **Testability** — Easy to test each layer independently
- **Maintainability** — Changes in one layer don't break others
- **Scalability** — Easy to add features without breaking existing code

---

## 3. DEVELOPMENT WORKFLOW (The Process)

### Step 1: Setup Phase
```
1. Create project folder
2. Configure build tool (Gradle/Maven)
3. Add dependencies
4. Configure database
5. Setup application entry point
```

### Step 2: Build Bottom-Up (Database → Controller)
Always build in this order:

```
1. DATA MODEL (Entity)
   ↓
2. DATA ACCESS (Repository)
   ↓
3. BUSINESS LOGIC (Service)
   ↓
4. HTTP ENDPOINTS (Controller)
```

**Why this order?**
- You define what data you're working with first (Entity)
- Then how to access it (Repository)
- Then what logic to apply (Service)
- Finally, expose it via HTTP (Controller)

### Step 3: Test Each Layer
As you build each layer, test it before moving to the next.

---

## 4. DETAILED BUILD PROCESS

### PHASE 1: Setup

#### 1.1 Project Structure
```
blog-api/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/blogapi/
│   │   │       ├── BlogApiApplication.java    ← Entry point
│   │   │       ├── entity/
│   │   │       │   ├── User.java
│   │   │       │   ├── Todo.java
│   │   │       │   ├── Post.java
│   │   │       │   └── Comment.java
│   │   │       ├── repository/
│   │   │       │   ├── UserRepository.java
│   │   │       │   ├── TodoRepository.java
│   │   │       │   ├── PostRepository.java
│   │   │       │   └── CommentRepository.java
│   │   │       ├── service/
│   │   │       │   ├── UserService.java
│   │   │       │   ├── TodoService.java
│   │   │       │   ├── PostService.java
│   │   │       │   └── CommentService.java
│   │   │       └── controller/
│   │   │           ├── UserController.java
│   │   │           ├── TodoController.java
│   │   │           ├── PostController.java
│   │   │           └── CommentController.java
│   │   └── resources/
│   │       └── application.properties
│   └── test/
│       └── java/...
├── build.gradle
├── settings.gradle
└── .gitignore
```

#### 1.2 Build.gradle Minimal Setup
```gradle
// Dependencies needed for REST API + Database
dependencies {
    // Web API
    implementation 'org.springframework.boot:spring-boot-starter-web'
    
    // Database & ORM
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    
    // H2 (in-memory database for development)
    runtimeOnly 'com.h2database:h2'
    
    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

#### 1.3 Application.properties (Database Config)
```properties
# Database connection (H2 in-memory)
spring.datasource.url=jdbc:h2:mem:tododb
spring.datasource.driverClassName=org.h2.Driver

# JPA/Hibernate settings
spring.jpa.hibernate.ddl-auto=create-drop  # Auto-create tables
spring.jpa.show-sql=true                   # Show SQL queries
```

---

### PHASE 2: Entity Layer (Define Data)

#### Step 1: Create User Entity
```java
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String username;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    private String password;
    
    // One user has many todos
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Todo> todos = new ArrayList<>();
    
    // One user has many posts
    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Post> posts = new ArrayList<>();
    
    // One user has many comments
    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Comment> comments = new ArrayList<>();
}
```

#### Step 2: Create Todo Entity
```java
@Entity
@Table(name = "todos")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Todo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String title;
    
    private String description;
    
    @Column(nullable = false)
    private boolean completed = false;
    
    private String priority;  // HIGH, MEDIUM, LOW
    
    // Many todos belong to one user
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
}
```

#### Step 3: Create Post Entity
```java
@Entity
@Table(name = "posts")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Post {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String title;
    
    @Column(columnDefinition = "TEXT")
    private String content;
    
    private LocalDateTime createdAt = LocalDateTime.now();
    
    // Many posts belong to one author (user)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;
    
    // One post has many comments
    @OneToMany(mappedBy = "post", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Comment> comments = new ArrayList<>();
}
```

#### Step 4: Create Comment Entity
```java
@Entity
@Table(name = "comments")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Comment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, columnDefinition = "TEXT")
    private String text;
    
    private LocalDateTime createdAt = LocalDateTime.now();
    
    // Many comments belong to one post
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "post_id", nullable = false)
    private Post post;
    
    // Many comments belong to one author (user)
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private User author;
}
```

#### Understanding Relationships

**@OneToMany (1:N):**
- One user has many todos
- Used on the "one" side
- Typically a List of related entities
```java
@OneToMany(mappedBy = "user")
private List<Todo> todos;
```

**@ManyToOne (N:1):**
- Many todos belong to one user
- Used on the "many" side
- Typically a single related entity
```java
@ManyToOne
@JoinColumn(name = "user_id")
private User user;
```

**@JoinColumn:**
- Specifies the foreign key column name in the database
- Only on the "many" side of the relationship

**mappedBy:**
- Used in @OneToMany to specify the property that owns the relationship
- The value is the field name in the related entity

**cascade = CascadeType.ALL:**
- When you delete a user, all their todos/posts/comments are deleted too
- Automatically handles related deletes

**orphanRemoval = true:**
- Deletes comment when removed from post's comment list
- Prevents orphaned records

#### Database Schema Generated

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE todos (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    completed BOOLEAN NOT NULL,
    priority VARCHAR(255),
    user_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP,
    author_id BIGINT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE TABLE comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    text TEXT NOT NULL,
    created_at TIMESTAMP,
    post_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (author_id) REFERENCES users(id)
);
```

#### Checklist
- [ ] User entity created with relationships
- [ ] Todo entity created with user relationship
- [ ] Post entity created with author and comments relationships
- [ ] Comment entity created with post and author relationships
- [ ] All @Id and @GeneratedValue annotations added
- [ ] @ManyToOne relationships with @JoinColumn
- [ ] @OneToMany relationships with mappedBy
- [ ] cascade = CascadeType.ALL set where appropriate
- [ ] Foreign keys properly configured

---

### PHASE 3: Repository Layer (Data Access)

#### Step 1: Create User Repository
```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
    Optional<User> findByEmail(String email);
    boolean existsByUsername(String username);
}
```

#### Step 2: Create Todo Repository
```java
@Repository
public interface TodoRepository extends JpaRepository<Todo, Long> {
    List<Todo> findByUser(User user);
    List<Todo> findByUserAndCompleted(User user, boolean completed);
    List<Todo> findByUserAndPriority(User user, String priority);
    List<Todo> findByCompleted(boolean completed);
}
```

#### Step 3: Create Post Repository
```java
@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    List<Post> findByAuthor(User author);
    List<Post> findByAuthorOrderByCreatedAtDesc(User author);
    List<Post> findAllByOrderByCreatedAtDesc();
}
```

#### Step 4: Create Comment Repository
```java
@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {
    List<Comment> findByPost(Post post);
    List<Comment> findByPostOrderByCreatedAtDesc(Post post);
    List<Comment> findByAuthor(User author);
    List<Comment> findByPostAndAuthor(Post post, User author);
}
```

#### What's Happening?
- Each repository extends `JpaRepository<Entity, Long>`
- Automatic CRUD methods: save(), findById(), findAll(), deleteById()
- Custom query methods defined by naming convention
  - `findByUser(User user)` → All entities for a specific user
  - `findByUserAndCompleted(User user, boolean completed)` → Filter by multiple fields
  - `findAllByOrderByCreatedAtDesc()` → Find all ordered by date descending

#### Checklist
- [ ] UserRepository created with email/username lookups
- [ ] TodoRepository created with user and status filters
- [ ] PostRepository created with author lookups and ordering
- [ ] CommentRepository created with post and author filters
- [ ] All custom query methods use correct naming convention

---

### PHASE 4: Service Layer (Business Logic)

#### Step 1: Create User Service
```java
@Service
public class UserService {
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public User createUser(User user) {
        if (userRepository.existsByUsername(user.getUsername())) {
            throw new IllegalArgumentException("Username already exists");
        }
        return userRepository.save(user);
    }
    
    public User getUserById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("User not found"));
    }
    
    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
            .orElseThrow(() -> new RuntimeException("User not found"));
    }
    
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}
```

#### Step 2: Create Todo Service
```java
@Service
public class TodoService {
    private final TodoRepository todoRepository;
    private final UserRepository userRepository;
    
    public TodoService(TodoRepository todoRepository, UserRepository userRepository) {
        this.todoRepository = todoRepository;
        this.userRepository = userRepository;
    }
    
    public Todo createTodo(Long userId, Todo todo) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
        todo.setUser(user);
        return todoRepository.save(todo);
    }
    
    public Todo getTodoById(Long id) {
        return todoRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Todo not found"));
    }
    
    public List<Todo> getUserTodos(Long userId) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
        return todoRepository.findByUser(user);
    }
    
    public List<Todo> getCompletedTodos(Long userId) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
        return todoRepository.findByUserAndCompleted(user, true);
    }
    
    public Todo updateTodo(Long id, Todo todoDetails) {
        Todo todo = getTodoById(id);
        if (todoDetails.getTitle() != null) {
            todo.setTitle(todoDetails.getTitle());
        }
        if (todoDetails.getDescription() != null) {
            todo.setDescription(todoDetails.getDescription());
        }
        todo.setCompleted(todoDetails.isCompleted());
        if (todoDetails.getPriority() != null) {
            todo.setPriority(todoDetails.getPriority());
        }
        return todoRepository.save(todo);
    }
    
    public void deleteTodo(Long id) {
        todoRepository.deleteById(id);
    }
}
```

#### Step 3: Create Post Service
```java
@Service
public class PostService {
    private final PostRepository postRepository;
    private final UserRepository userRepository;
    
    public PostService(PostRepository postRepository, UserRepository userRepository) {
        this.postRepository = postRepository;
        this.userRepository = userRepository;
    }
    
    public Post createPost(Long userId, Post post) {
        User author = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
        post.setAuthor(author);
        return postRepository.save(post);
    }
    
    public Post getPostById(Long id) {
        return postRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Post not found"));
    }
    
    public List<Post> getAllPosts() {
        return postRepository.findAllByOrderByCreatedAtDesc();
    }
    
    public List<Post> getAuthorPosts(Long userId) {
        User author = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
        return postRepository.findByAuthorOrderByCreatedAtDesc(author);
    }
    
    public Post updatePost(Long id, Post postDetails) {
        Post post = getPostById(id);
        if (postDetails.getTitle() != null) {
            post.setTitle(postDetails.getTitle());
        }
        if (postDetails.getContent() != null) {
            post.setContent(postDetails.getContent());
        }
        return postRepository.save(post);
    }
    
    public void deletePost(Long id) {
        postRepository.deleteById(id);
    }
}
```

#### Step 4: Create Comment Service
```java
@Service
public class CommentService {
    private final CommentRepository commentRepository;
    private final PostRepository postRepository;
    private final UserRepository userRepository;
    
    public CommentService(CommentRepository commentRepository, 
                         PostRepository postRepository, 
                         UserRepository userRepository) {
        this.commentRepository = commentRepository;
        this.postRepository = postRepository;
        this.userRepository = userRepository;
    }
    
    public Comment createComment(Long postId, Long userId, Comment comment) {
        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new RuntimeException("Post not found"));
        User author = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
        
        comment.setPost(post);
        comment.setAuthor(author);
        return commentRepository.save(comment);
    }
    
    public Comment getCommentById(Long id) {
        return commentRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Comment not found"));
    }
    
    public List<Comment> getPostComments(Long postId) {
        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new RuntimeException("Post not found"));
        return commentRepository.findByPostOrderByCreatedAtDesc(post);
    }
    
    public List<Comment> getUserComments(Long userId) {
        User author = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("User not found"));
        return commentRepository.findByAuthor(author);
    }
    
    public Comment updateComment(Long id, Comment commentDetails) {
        Comment comment = getCommentById(id);
        if (commentDetails.getText() != null) {
            comment.setText(commentDetails.getText());
        }
        return commentRepository.save(comment);
    }
    
    public void deleteComment(Long id) {
        commentRepository.deleteById(id);
    }
}
```

#### What's Happening?
- Each service has constructor injection of repositories
- Services handle validation (user exists, etc.)
- Services manage relationships (setting user on todo, author on post, etc.)
- Error handling for missing entities
- Business logic methods for common queries

#### Checklist
- [ ] UserService created with user CRUD and validation
- [ ] TodoService created with user association logic
- [ ] PostService created with author tracking
- [ ] CommentService created with post and author associations
- [ ] All services use constructor injection for repositories
- [ ] Proper error handling with orElseThrow()
- [ ] Relationships properly managed (setting user, author, etc.)

---

### PHASE 5: Controller Layer (HTTP Endpoints)

#### Step 1: Create User Controller
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        return new ResponseEntity<>(userService.getAllUsers(), HttpStatus.OK);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        return new ResponseEntity<>(userService.getUserById(id), HttpStatus.OK);
    }
    
    @GetMapping("/username/{username}")
    public ResponseEntity<User> getUserByUsername(@PathVariable String username) {
        return new ResponseEntity<>(userService.getUserByUsername(username), HttpStatus.OK);
    }
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        return new ResponseEntity<>(userService.createUser(user), HttpStatus.CREATED);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

#### Step 2: Create Todo Controller
```java
@RestController
@RequestMapping("/api/users/{userId}/todos")
public class TodoController {
    private final TodoService todoService;
    
    public TodoController(TodoService todoService) {
        this.todoService = todoService;
    }
    
    @GetMapping
    public ResponseEntity<List<Todo>> getUserTodos(@PathVariable Long userId) {
        return new ResponseEntity<>(todoService.getUserTodos(userId), HttpStatus.OK);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Todo> getTodoById(@PathVariable Long id) {
        return new ResponseEntity<>(todoService.getTodoById(id), HttpStatus.OK);
    }
    
    @GetMapping("/status/completed")
    public ResponseEntity<List<Todo>> getCompletedTodos(@PathVariable Long userId) {
        return new ResponseEntity<>(todoService.getCompletedTodos(userId), HttpStatus.OK);
    }
    
    @PostMapping
    public ResponseEntity<Todo> createTodo(@PathVariable Long userId, @RequestBody Todo todo) {
        return new ResponseEntity<>(todoService.createTodo(userId, todo), HttpStatus.CREATED);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<Todo> updateTodo(@PathVariable Long id, @RequestBody Todo todoDetails) {
        return new ResponseEntity<>(todoService.updateTodo(id, todoDetails), HttpStatus.OK);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTodo(@PathVariable Long id) {
        todoService.deleteTodo(id);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

#### Step 3: Create Post Controller
```java
@RestController
@RequestMapping("/api/posts")
public class PostController {
    private final PostService postService;
    
    public PostController(PostService postService) {
        this.postService = postService;
    }
    
    @GetMapping
    public ResponseEntity<List<Post>> getAllPosts() {
        return new ResponseEntity<>(postService.getAllPosts(), HttpStatus.OK);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Post> getPostById(@PathVariable Long id) {
        return new ResponseEntity<>(postService.getPostById(id), HttpStatus.OK);
    }
    
    @GetMapping("/author/{userId}")
    public ResponseEntity<List<Post>> getAuthorPosts(@PathVariable Long userId) {
        return new ResponseEntity<>(postService.getAuthorPosts(userId), HttpStatus.OK);
    }
    
    @PostMapping
    public ResponseEntity<Post> createPost(@RequestParam Long userId, @RequestBody Post post) {
        return new ResponseEntity<>(postService.createPost(userId, post), HttpStatus.CREATED);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<Post> updatePost(@PathVariable Long id, @RequestBody Post postDetails) {
        return new ResponseEntity<>(postService.updatePost(id, postDetails), HttpStatus.OK);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePost(@PathVariable Long id) {
        postService.deletePost(id);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

#### Step 4: Create Comment Controller
```java
@RestController
@RequestMapping("/api/posts/{postId}/comments")
public class CommentController {
    private final CommentService commentService;
    
    public CommentController(CommentService commentService) {
        this.commentService = commentService;
    }
    
    @GetMapping
    public ResponseEntity<List<Comment>> getPostComments(@PathVariable Long postId) {
        return new ResponseEntity<>(commentService.getPostComments(postId), HttpStatus.OK);
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<Comment> getCommentById(@PathVariable Long id) {
        return new ResponseEntity<>(commentService.getCommentById(id), HttpStatus.OK);
    }
    
    @PostMapping
    public ResponseEntity<Comment> createComment(
        @PathVariable Long postId,
        @RequestParam Long userId,
        @RequestBody Comment comment
    ) {
        return new ResponseEntity<>(commentService.createComment(postId, userId, comment), HttpStatus.CREATED);
    }
    
    @PutMapping("/{id}")
    public ResponseEntity<Comment> updateComment(@PathVariable Long id, @RequestBody Comment commentDetails) {
        return new ResponseEntity<>(commentService.updateComment(id, commentDetails), HttpStatus.OK);
    }
    
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteComment(@PathVariable Long id) {
        commentService.deleteComment(id);
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
```

#### API Endpoints Summary

**Users:**
- `GET /api/users` — Get all users
- `GET /api/users/{id}` — Get user by ID
- `GET /api/users/username/{username}` — Get user by username
- `POST /api/users` — Create user
- `DELETE /api/users/{id}` — Delete user

**Todos (nested under user):**
- `GET /api/users/{userId}/todos` — Get user's todos
- `GET /api/users/{userId}/todos/{id}` — Get specific todo
- `GET /api/users/{userId}/todos/status/completed` — Get user's completed todos
- `POST /api/users/{userId}/todos` — Create todo for user
- `PUT /api/users/{userId}/todos/{id}` — Update todo
- `DELETE /api/users/{userId}/todos/{id}` — Delete todo

**Posts:**
- `GET /api/posts` — Get all posts
- `GET /api/posts/{id}` — Get specific post
- `GET /api/posts/author/{userId}` — Get posts by author
- `POST /api/posts?userId=1` — Create post
- `PUT /api/posts/{id}` — Update post
- `DELETE /api/posts/{id}` — Delete post

**Comments (nested under post):**
- `GET /api/posts/{postId}/comments` — Get comments on post
- `GET /api/posts/{postId}/comments/{id}` — Get specific comment
- `POST /api/posts/{postId}/comments?userId=1` — Add comment to post
- `PUT /api/posts/{postId}/comments/{id}` — Update comment
- `DELETE /api/posts/{postId}/comments/{id}` — Delete comment

#### Checklist
- [ ] UserController created with CRUD endpoints
- [ ] TodoController created with nested path for user association
- [ ] PostController created with author tracking
- [ ] CommentController created with post and user association
- [ ] All @RequestMapping paths consistent
- [ ] @PathVariable for URL parameters
- [ ] @RequestBody for JSON input
- [ ] @RequestParam for query parameters
- [ ] Correct HTTP status codes (200, 201, 204, etc.)

---

### PHASE 6: Application Entry Point

#### Step 1: Create Main Class
```java
@SpringBootApplication
public class TodoApiApplication {
    public static void main(String[] args) {
        SpringApplication.run(TodoApiApplication.class, args);
    }
}
```

#### What's Happening?
- `@SpringBootApplication` — Enables auto-configuration
- `SpringApplication.run()` — Starts the Spring Boot app
- Tomcat server starts automatically on port 8080

#### Checklist
- [ ] Main class created with @SpringBootApplication
- [ ] main() method added with SpringApplication.run()

---

## 5. TESTING THE APPLICATION

### Step 1: Build the Project
```bash
cd c:\Workspace\OffLimits\todo-api
./gradlew build
```

### Step 2: Run the Application
```bash
./gradlew bootRun
```

You should see:
```
Tomcat initialized with port(s): 8080 (http)
Started TodoApiApplication in 3.5 seconds
```

### Step 3: Test Endpoints

#### Using curl:

**Create a todo:**
```bash
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Spring", "priority": "HIGH"}'
```

**Get all todos:**
```bash
curl http://localhost:8080/api/todos
```

**Get completed todos:**
```bash
curl http://localhost:8080/api/todos/status/completed
```

**Update a todo:**
```bash
curl -X PUT http://localhost:8080/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Mastered Spring", "completed": true}'
```

**Delete a todo:**
```bash
curl -X DELETE http://localhost:8080/api/todos/1
```

#### Using Postman:
1. Create collection "Todo API"
2. Create requests for each endpoint
3. Test each one

---

## 6. COMMON PATTERNS & BEST PRACTICES

### Constructor Injection Pattern
```java
@Service
public class MyService {
    private final MyRepository repository;
    
    // ✅ Recommended
    public MyService(MyRepository repository) {
        this.repository = repository;
    }
}
```

**Why?**
- Dependencies are explicit
- Immutable (final keyword)
- Easy to test with mock objects
- Spring autowires automatically

### ResponseEntity Pattern
```java
// ✅ Good — Control status codes
return new ResponseEntity<>(todo, HttpStatus.CREATED);

// ❌ Avoid — No status code control
return todo;
```

### Optional Handling
```java
// ✅ Good — Handle missing data
return todoRepository.findById(id)
    .orElseThrow(() -> new TodoNotFoundException("Todo not found"));

// ❌ Avoid — Nullable
Todo todo = todoRepository.findById(id).orElse(null);
```

### Method Naming Convention (Spring Data)
```java
// Spring Data automatically generates SQL from method names

// Find by single field
List<Todo> findByCompleted(boolean completed);
// SQL: SELECT * FROM todos WHERE completed = ?

// Find by multiple fields
List<Todo> findByCompletedAndPriority(boolean completed, String priority);
// SQL: SELECT * FROM todos WHERE completed = ? AND priority = ?

// Find and order by
List<Todo> findByCompletedOrderByIdDesc(boolean completed);
// SQL: SELECT * FROM todos WHERE completed = ? ORDER BY id DESC
```

---

## 7. TROUBLESHOOTING

| Problem | Cause | Solution |
|---|---|---|
| "Port 8080 already in use" | Another app using port 8080 | Change port in `application.properties`: `server.port=8081` |
| "Could not find dependency" | Gradle not synced | Run `./gradlew build` or refresh in IDE |
| "Controller not responding" | Missing @RequestMapping | Add `@RequestMapping("/api/todos")` on class |
| "Dependency injection error" | Missing constructor | Add public constructor with dependency parameter |
| "Endpoint returns 404" | Wrong URL path | Check @RequestMapping and @GetMapping values |
| "Null pointer exception" | Service not autowired | Use constructor injection, not @Autowired on field |

---

## 8. NEXT STEPS AFTER BUILDING

Once the basic Todo API works, learn these topics to make it production-ready:

1. **Input Validation** — Validate data before saving
   - Use `@NotBlank`, `@Size`, `@Min`, etc.

2. **Global Exception Handling** — Handle errors gracefully
   - Use `@RestControllerAdvice`

3. **Authentication & Security** — Secure your API
   - Learn Spring Security

4. **Testing** — Write unit and integration tests
   - JUnit, Mockito

5. **Pagination & Filtering** — Handle large datasets
   - `PageRequest`, `Specification`

6. **Transactions** — Handle multi-step operations
   - `@Transactional`

7. **API Documentation** — Document your API
   - Swagger/SpringFox

---

## SUMMARY: Build Order

```
1. Create build.gradle with dependencies
2. Configure application.properties
3. Create Entities (User, Todo, Post, Comment with relationships)
4. Create Repositories (UserRepo, TodoRepo, PostRepo, CommentRepo)
5. Create Services (UserService, TodoService, PostService, CommentService)
6. Create Controllers (UserController, TodoController, PostController, CommentController)
7. Create Main class (BlogApiApplication)
8. Build & Run
9. Test all endpoints
```

**Key Points:**
- Build bottom-up (Entity → Repository → Service → Controller)
- Define relationships in Entity layer (@OneToMany, @ManyToOne)
- Handle relationships in Service layer (setting user, author, etc.)
- Expose related endpoints through Controller layer
- Use nested paths for related resources (/users/{userId}/todos)

Good luck! 🚀
