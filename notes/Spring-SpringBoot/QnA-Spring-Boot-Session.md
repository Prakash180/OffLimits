# Spring Boot Q&A — Session Notes

Quick reference for questions asked during this learning session with answers and explanations.

---

## Q1: Why Repository Methods Require Certain Parameters While Others Don't

**Question:**
```
List findByUserAndCompleted(User user, boolean completed);  // Pass completed
List findByAuthorOrderByCreatedAtDesc(User author);         // Don't pass CreatedAt
```
Why do we pass `completed` in the first but not `createdAt` in the second?

**Answer:**

The difference is between **filter conditions** (WHERE) and **sorting instructions** (ORDER BY).

**Filters need input** because they change per query:
```java
// Call 1: Find completed todos
findByUserAndCompleted(user, true);   // Returns only completed

// Call 2: Find incomplete todos
findByUserAndCompleted(user, false);  // Returns only incomplete
// ↑ Different boolean = Different results
```

**Sorting is always the same:**
```java
// Call 1: Get posts by author, sorted newest first
findByAuthorOrderByCreatedAtDesc(author1);

// Call 2: Get posts by another author, sorted newest first
findByAuthorOrderByCreatedAtDesc(author2);
// ↑ Same sort order = No parameter needed
```

**Key Insight:** Method parameters = filter values you pass. OrderBy clauses = sorting instructions built into the method (don't change per call).

**Common Patterns:**

| Method | Filters | Sort | Pass |
|---|---|---|---|
| `findByUser()` | User | None | user |
| `findByUserOrderByTitleAsc()` | User | Title ascending | user |
| `findByCompleted()` | Completed | None | completed |
| `findByUserAndCompleted()` | User, Completed | None | user, completed |
| `findByUserOrderByIdDesc()` | User | ID descending | user |
| `findAllOrderByCreatedAtDesc()` | None | Created date desc | nothing |

**Real World Analogy:** "Show me books by [THIS AUTHOR], sorted by date (newest first)" — You don't ask "sorted by which date?" — the sorting is always the same.

---

## Q2: @JoinColumn vs mappedBy

**Question:**
What's the difference between `@JoinColumn` and `mappedBy`? How do they relate to each other?

**Answer:**

**@JoinColumn(name = "user_id"):**
- Specifies the **FOREIGN KEY COLUMN NAME** in the **current table**
- Used only on the **"many" side** (@ManyToOne)
- Example: `@JoinColumn(name = "user_id")` creates a column named `user_id` in the current table

**mappedBy = "user":**
- Specifies the **JAVA FIELD NAME** in the **related entity** that owns the relationship
- Used only on the **"one" side** (@OneToMany)
- Example: `@OneToMany(mappedBy = "user")` means "the User entity has a field named `user`"

**Example:**

```java
// User entity (the "one" side)
@Entity
public class User {
    @OneToMany(mappedBy = "user")  // ← References the Java field name
    private List<Todo> todos;      //   "user" is defined in Todo class
}

// Todo entity (the "many" side)
@Entity
public class Todo {
    @ManyToOne
    @JoinColumn(name = "user_id")  // ← Names the database column
    private User user;             // ← This is the field name for mappedBy
}
```

**Database Result:**
```sql
CREATE TABLE todos (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,  -- ← Column name from @JoinColumn
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Key Points:**
- Foreign key column exists **only in the "many" side's table**
- `@JoinColumn` is database-focused (column name)
- `mappedBy` is Java-focused (field name)
- Only the "many" side has `@JoinColumn`; only the "one" side has `mappedBy`

---

## Q3: What is H2 Database?

**Question:**
What is H2? Why use it for development?

**Answer:**

**H2 is an in-memory database** — a database that runs in your computer's RAM (memory) instead of storing data on disk.

**Key Features:**
- **In-Memory**: Data lives in RAM, lost when app stops
- **Embedded**: Runs inside your Java app, no separate server
- **Zero Setup**: Just add to `build.gradle`, no installation needed

**Why Use H2 for Development?**
- ✅ Fast startup (no server to boot)
- ✅ No installation (just add dependency)
- ✅ Fresh database every run (no stale data)
- ✅ Perfect for learning (no complexity)
- ✅ Easy to test (no external dependencies)

**Disadvantages:**
- ❌ Data lost on restart (not for production)
- ❌ Single connection only (not for concurrent users)

**Configuration:**
```properties
spring.datasource.url=jdbc:h2:mem:tododb
spring.datasource.driverClassName=org.h2.Driver
spring.jpa.hibernate.ddl-auto=create-drop  # Auto-create tables
```

When you run your Spring Boot app, H2 creates tables from your Entity classes and stores everything in RAM. Perfect for development! 🚀

---

## Q4: What is Boilerplate Code?

**Question:**
What does "boilerplate setup" mean?

**Answer:**

**Boilerplate** = repetitive, standard code that you write the same way every time, even though it's not unique to your project.

**Example in Spring (without Spring Boot):**
Every time you create a Spring project, you had to manually:
1. Create XML configuration files
2. Define beans manually
3. Set up the ApplicationContext
4. Configure logging
5. Set up the web server

All necessary but boring and repetitive.

**Spring Boot solves this:**
- Pre-configured everything
- You skip all the boilerplate and jump straight to coding your business logic
- Saves hours of setup time

---

## Q5: What is Tomcat Server?

**Question:**
What is Tomcat and why is it necessary for hosting applications?

**Answer:**

**Tomcat is a web server** — a program that listens for HTTP requests from browsers and hands them off to your Java application.

**Why It's Necessary:**
- Your Java code alone can't talk to browsers directly
- Tomcat bridges the gap:
  1. **Listens** for incoming HTTP requests on port 8080
  2. **Routes** requests to the right method in your code
  3. **Sends back** the response to the browser

**In Spring Boot:**
- Tomcat is **embedded inside your application**
- You don't install Tomcat separately
- It starts automatically when your app runs
- `./gradlew bootRun` starts Tomcat + your app automatically

---

## Q6: One Entity = One Table

**Question:**
Is it true that for every table we need to create its own entity class?

**Answer:**

**YES! 1 Table = 1 Entity Class**

**Example: Blog System**

Database Tables:
- `users`
- `posts`
- `comments`
- `categories`

Entity Classes:
- `User.java`
- `Post.java`
- `Comment.java`
- `Category.java`

Each entity maps exactly one-to-one with a database table. The `@Entity` and `@Table` annotations tell Hibernate which class maps to which table.

---

## Q7: What is @Data Annotation?

**Question:**
What does `@Data` do?

**Answer:**

**`@Data` is a Lombok annotation** that automatically generates boilerplate code.

**What it generates:**
```java
@Data  // Auto-generates all of this:
public class User {
    private Long id;
    private String username;
}
// Generates:
// - getters (getId(), getUsername())
// - setters (setId(), setUsername())
// - toString()
// - equals()
// - hashCode()
```

**Without `@Data`, you'd write hundreds of lines manually!**

**Pro Tip:** Add Lombok to `build.gradle`:
```gradle
compileOnly 'org.projectlombok:lombok'
annotationProcessor 'org.projectlombok:lombok'
```

---

## Q8: Should Entity Classes Have Business Logic Functions?

**Question:**
Is it correct that entity classes don't have functions and only represent table data?

**Answer:**

**YES! Entity classes should be "dumb data containers"** — they should NOT contain business logic.

**✅ CORRECT - Entity is just data:**
```java
@Entity
@Data
public class User {
    @Id
    private Long id;
    private String username;
    private String email;
    
    // No functions here!
}
```

**❌ WRONG - Don't add business logic to entities:**
```java
@Entity
public class User {
    // ❌ Never do this!
    public void validateEmail() { ... }
    public void hashPassword() { ... }
    public void sendNotification() { ... }
}
```

**Where should logic go?**
- **Services** → Business logic (UserService)
- **Controllers** → HTTP handling (UserController)
- **Entities** → Pure data only

This keeps code clean, testable, and maintainable.

---

## Q9: @ManyToOne and fetch = FetchType.LAZY Explained

**Question:**
Can you explain `@ManyToOne(fetch = FetchType.LAZY)` and `@JoinColumn`?

**Answer:**

### @ManyToOne
Tells JPA that many of these entities belong to one of another entity.

**Example:**
- Many **Todos** belong to one **User**
- Many **Comments** belong to one **Post**

### fetch = FetchType.LAZY
Controls **WHEN** the related entity is loaded from the database.

**LAZY (Lazy Loading):**
```java
@ManyToOne(fetch = FetchType.LAZY)
private User user;

Todo todo = todoRepository.findById(1);  // Loads ONLY todo
todo.getUser().getUsername();  // NOW loads the user (second query)
```
- Benefit: Faster initial query (only loads what you need)
- Problem: LazyInitializationException if accessed outside transaction

**EAGER (Eager Loading):**
```java
@ManyToOne(fetch = FetchType.EAGER)
private User user;

Todo todo = todoRepository.findById(1);  // Loads todo AND user
todo.getUser().getUsername();  // Already loaded, no extra query
```
- Benefit: No error when accessing related entity
- Problem: Always loads related data even if you don't need it

### @JoinColumn(name = "user_id")
Specifies the **foreign key column name** in THIS table (the "many" side).

**Database:**
```sql
CREATE TABLE todos (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,  -- ← Foreign key (from @JoinColumn)
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Q10: How LAZY Loading Actually Works

**Question:**
So when I retrieve a todo with LAZY loading, only the todo fields are loaded, and the user object stays empty. When I access a user-specific function, it then pulls a new query to fetch and initialize the user object. Am I getting this right?

**Answer:**

**YES! 100% correct!** 🎯

**Step-by-step execution:**

### Step 1: Retrieve Todo
```java
Todo todo = todoRepository.findById(1);
```
**Query 1 executed:**
```sql
SELECT * FROM todos WHERE id = 1;
```
**Result:**
```
todo.id = 1          ✅ Loaded
todo.title = "..."   ✅ Loaded
todo.user = null     ⏳ NOT loaded yet (lazy)
```

### Step 2: Access Todo Fields
```java
System.out.println(todo.getTitle());
```
**No query!** Title already loaded from Step 1.

### Step 3: Access User Field
```java
System.out.println(todo.getUser().getUsername());
```
**Query 2 triggered:**
```sql
SELECT * FROM users WHERE id = 1;
```
**Result:**
```
todo.user.id = 1              ✅ NOW loaded
todo.user.username = "john"   ✅ NOW loaded
```

**Total queries: 2** (one for todo, one for user when accessed)

---

## Q11: @JoinColumn Defines Foreign Key in Current Table

**Question:**
In the Post entity, `@JoinColumn(name = "author_id")` is used, but there's no `author_id` column in the User entity. How does this work?

**Answer:**

**`author_id` is NOT in the User table — it's in the POSTS table!**

`@JoinColumn(name = "author_id")` specifies a foreign key **in this table** (the "many" side), NOT in the related table.

**Database Schema:**
```sql
-- USERS table (no author_id here)
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255)
);

-- POSTS table (author_id is HERE)
CREATE TABLE posts (
    id BIGINT PRIMARY KEY,
    title VARCHAR(255),
    author_id BIGINT,  ← Foreign key pointing to users.id
    FOREIGN KEY (author_id) REFERENCES users(id)
);
```

**Key Rule:**
> Foreign key exists **only on the "many" side** of the relationship, never on the "one" side.

---

## Q12: Entity Field vs Database Column

**Question:**
In the Post entity class, there is an `author_id` column in the database, but there's no `author_id` field in the entity class. Why?

**Answer:**

**Exactly!** This is the key mapping concept:

| Context | Name | Type | What It Represents |
|---|---|---|---|
| **Java Entity** | `author` | `User` object | The actual Java field |
| **Database Table** | `author_id` | `BIGINT` | The foreign key column |

### In Java:
```java
private User author;  // ← Java field (User object)
post.setAuthor(user);
```

### In Database:
```sql
INSERT INTO posts (id, title, author_id) VALUES (1, 'My Post', 42);
                                                           ↑
                                                    Store the ID number
```

### The Mapping:
```java
@ManyToOne
@JoinColumn(name = "author_id")  // ← Maps Java field 'author' 
private User author;             //   to database column 'author_id'
```

**Summary:**
- ✅ **Yes, there IS an `author_id` column in the database**
- ✅ **NO `author_id` field in the entity class**
- ✅ **Entity has `author` (a User object) instead**
- ✅ **Hibernate automatically translates between them**

When you save a Post, Hibernate extracts the author's ID and stores it as `author_id` in the database! 🪄

---

