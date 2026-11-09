# Spring Boot Learning Progression — Complete Roadmap

A structured learning path from Spring Boot basics to Microservices, with projects and resources.

---

## 🎯 Learning Goals

By the end of this journey, you'll understand:
- ✅ Spring Boot fundamentals (Entity, Repository, Service, Controller)
- ✅ Web MVC architecture (Spring Pet Clinic)
- ✅ REST API design and implementation
- ✅ Spring Security and authentication
- ✅ Microservices architecture
- ✅ Best practices and design patterns

---

## 📚 Phase 1: Spring Boot Basics (Weeks 1-2)

### Goals
- Understand Spring Boot layers and their responsibilities
- Learn dependency injection and IoC
- Get comfortable with annotations

### Study Resources

**Your Notes (Already Created):**
1. [Spring Boot Layers & Concepts](spring-boot-layers-and-concepts.md) ← Start here
2. [Spring Fundamentals](spring-fundamentals.md)
3. [Spring Boot Workflow](spring-boot-workflow-beginner.md)

### Hands-On Practice
```java
// TASK 1: Study Entity Layer
Read: spring-petclinic/src/main/java/org/springframework/samples/petclinic/model/
Read: spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/Owner.java
       spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/Pet.java
Understand: @Entity, @Table, @Column, @OneToMany, @ManyToOne
Practice: Draw the entity relationship diagram

// TASK 2: Study Repository Layer
Read: spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java
       spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/PetRepository.java
Understand: JpaRepository, derived queries, @Query
Practice: Write 5 custom query methods

// TASK 3: Study Controller Layer
Read: spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java
Understand: @Controller, @GetMapping, @PostMapping, @PathVariable
Practice: Trace one complete request (Create Owner → Save → Redirect)
```

### Concepts to Master
- [ ] IoC Container and Bean lifecycle
- [ ] Dependency Injection (Constructor, Setter, Field)
- [ ] Entity relationships (1:N, M:N)
- [ ] JPA/Hibernate basics
- [ ] CRUD operations
- [ ] Spring Data JPA repositories
- [ ] MVC pattern (Model-View-Controller)
- [ ] Form binding and validation
- [ ] Transaction management

### Code Review Exercises
1. **Why @MappedSuperclass?**
   - Answer: Allows inheritance without creating a table
   
2. **How does derived query work?**
   - Answer: Spring parses method name → generates SQL
   
3. **What does cascade=ALL do?**
   - Answer: Parent operations cascade to children (delete owner → delete pets)

---

## 📚 Phase 2: Spring Pet Clinic Deep Dive (Weeks 2-3)

### Resources
**Your Reverse Engineering Guide:**
- [Spring Pet Clinic Reverse Engineering Guide](spring-petclinic-reverse-engineering-guide.md)

**Official Resources:**
- [Spring Pet Clinic GitHub](https://github.com/spring-projects/spring-petclinic)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Spring Data JPA Reference](https://spring.io/projects/spring-data-jpa)

### Study Plan

**Week 1: Entity & Repository Layers**
```
Day 1: Entity layer patterns
  - BaseEntity inheritance hierarchy
  - @Entity vs @MappedSuperclass
  - One-to-Many relationships
  - Many-to-Many with join tables

Day 2: Repository layer
  - JpaRepository methods
  - Derived query methods
  - @Query annotations
  - Pagination

Day 3: Hands-on
  - Create your own entity with relationships
  - Write custom repository methods
  - Test queries in a simple app
```

**Week 2: Controller & View Layers**
```
Day 1: Controller basics
  - @Controller (returns HTML) vs @RestController (returns JSON)
  - @GetMapping, @PostMapping, @PathVariable
  - Model & ModelAndView
  - BindingResult & validation

Day 2: Form handling & validation
  - Data binding (@InitBinder)
  - Validation (@Valid, @NotBlank, @Email, etc)
  - Error handling and display
  - Redirect vs forward

Day 3: Application flow
  - Trace: Request → Controller → Repository → Database → Response
  - Understand HTTP status codes
  - Understand GET/POST/PUT/DELETE operations
```

### Hands-On Assignments

**Assignment 1: Create a Simple Todo App**
```
Requirements:
- User can create a todo with title and description
- User can mark todo as complete/incomplete
- User can view all their todos
- User can delete a todo

Implementation:
- Entity: Todo (extends BaseEntity)
- Entity: User (extends Person)
- Repository: TodoRepository
- Repository: UserRepository
- Controller: TodoController (web MVC)
- Template: todo-list.html, create-todo-form.html
```

**Assignment 2: Add Pet Features to Pet Clinic**
```
Requirements:
- Add "Pet Age" calculation based on birth date
- Add "Last Visited" field to pet
- Add "Total Visits" count
- Add "Favorite Vet" field

Implementation:
- Modify Pet entity
- Add validation
- Modify PetRepository with custom queries
- Update PetController to show new fields
- Update templates to display new info
```

---

## 📚 Phase 3: REST API Development (Weeks 3-4)

### The Difference

| Aspect | Web MVC (Pet Clinic) | REST API |
|--------|-------------------|----------|
| Returns | HTML Pages | JSON |
| Annotation | `@Controller` | `@RestController` |
| Purpose | Web application | API for other apps |
| Client | Browser | Postman, Mobile app, etc |
| Status codes | Less critical | Critical (200, 201, 400, 404, 500) |

### Official REST Version

**Project:** [spring-petclinic-rest](https://github.com/spring-projects/spring-petclinic-rest)
- Same domain as MVC version
- REST endpoints instead of HTML
- Service layer (new!)
- DTOs (Data Transfer Objects)
- Proper HTTP status codes

### Study Resources

**To Study:**
```bash
# Clone the REST version
git clone https://github.com/spring-projects/spring-petclinic-rest.git
cd spring-petclinic-rest

# Explore structure
- src/main/java/.../model/          ← Same entities
- src/main/java/.../repository/     ← Same repositories
- src/main/java/.../service/        ← NEW: Business logic
- src/main/java/.../rest/           ← NEW: REST controllers
- src/main/java/.../rest/dto/       ← NEW: Data transfer objects
```

### Key Differences

1. **Service Layer** (NEW)
   ```java
   @Service
   public class OwnerService {
       private final OwnerRepository ownerRepository;
       
       public Owner create(Owner owner) {
           // Validation
           if (ownerRepository.existsByLastName(owner.getLastName())) {
               throw new Exception("Owner already exists");
           }
           return ownerRepository.save(owner);
       }
   }
   ```

2. **REST Controllers** (instead of Web Controllers)
   ```java
   @RestController
   @RequestMapping("/api/owners")
   public class OwnerRestController {
       
       private final OwnerService ownerService;
       
       @PostMapping
       @ResponseStatus(HttpStatus.CREATED)  // 201 Created
       public OwnerDto create(@RequestBody OwnerDto dto) {
           Owner owner = ownerService.create(dto.toEntity());
           return new OwnerDto(owner);
       }
       
       @GetMapping("/{id}")
       public OwnerDto getOwner(@PathVariable int id) {
           Owner owner = ownerService.get(id);
           return new OwnerDto(owner);
       }
   }
   ```

3. **DTOs** (Data Transfer Objects)
   ```java
   public class OwnerDto {
       private int id;
       private String firstName;
       private String lastName;
       // Only expose what we want to clients
   }
   ```

4. **Exception Handling**
   ```java
   @ExceptionHandler(NotFoundException.class)
   @ResponseStatus(HttpStatus.NOT_FOUND)  // 404
   public ErrorDto handleNotFound(NotFoundException e) {
       return new ErrorDto(e.getMessage());
   }
   ```

### Hands-On Assignments

**Assignment 1: Convert Todo App to REST API**
```
Before (Web MVC):
  POST /todos → returns HTML redirect
  GET /todos → returns HTML page
  
After (REST API):
  POST /api/todos → returns JSON + 201 Created
  GET /api/todos → returns JSON array + 200 OK
  PUT /api/todos/{id} → returns JSON + 200 OK
  DELETE /api/todos/{id} → returns 204 No Content

Test with Postman or curl
```

**Assignment 2: Add Service Layer to Pet Clinic REST**
```
Create:
- OwnerService with validation
- PetService with business logic
- VisitService with calculations

Modify:
- REST controllers to use services
- Add proper exception handling
- Add HTTP status codes
```

---

## 📚 Phase 4: Spring Security & Authentication (Weeks 4-5)

### Goals
- Understand authentication (login)
- Understand authorization (roles, permissions)
- Implement JWT tokens for stateless auth

### Topics to Study
- [ ] Spring Security architecture
- [ ] Authentication vs Authorization
- [ ] Password encryption (BCrypt)
- [ ] JWT (JSON Web Tokens)
- [ ] CORS (Cross-Origin Resource Sharing)
- [ ] OAuth 2.0

### Project: Secure Pet Clinic REST

```java
// 1. Add User authentication
@Entity
public class User {
    private String username;
    
    @JsonIgnore
    private String password;  // Hash with BCrypt
    
    @ManyToMany
    private Set<Role> roles;  // USER, ADMIN
}

// 2. Add authentication controller
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    
    @PostMapping("/login")
    public AuthResponse login(@RequestBody LoginRequest request) {
        // Authenticate user
        // Generate JWT token
        return new AuthResponse(token);
    }
}

// 3. Secure endpoints
@RestController
@RequestMapping("/api/owners")
public class OwnerRestController {
    
    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")  // Only admins can view all
    public List<OwnerDto> list() { ... }
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")  // Only admins can create
    public OwnerDto create(@RequestBody OwnerDto dto) { ... }
}
```

### Resources
- [spring-petclinic-microservices](https://github.com/spring-projects/spring-petclinic-microservices) (has security examples)
- [Spring Security Documentation](https://spring.io/projects/spring-security)
- Your notes on OAuth2 (already created)

---

## 📚 Phase 5: Microservices Architecture (Weeks 5-6)

### Goals
- Understand microservices philosophy
- Learn service-to-service communication
- Learn API Gateway pattern
- Learn config management

### Architecture

```
┌─────────────────────────────────────┐
│         Client (Web/Mobile)         │
└──────────────┬──────────────────────┘
               │
┌──────────────────────────────────────┐
│       API Gateway (Zuul)             │  ← Routes requests
│  - Authentication                    │
│  - Request routing                   │
│  - Load balancing                    │
└──────────────┬───────────────────────┘
               │
       ┌───────┼───────┬─────────────┐
       │       │       │             │
  ┌────▼──┐┌──▼───┐┌──▼───┐┌────────▼──┐
  │Owner  ││Pet   ││Visit ││Vet Service│
  │Service││Svc   ││Svc   │└───────────┘
  └────┬──┘└──┬───┘└──┬───┘
       │      │       │
  ┌────▼──┬───▼──┬────▼───┐
  │  Owner│ Pet  │ Visit   │
  │   DB  │  DB  │   DB    │
  └───────┴──────┴─────────┘
```

### Split Pet Clinic into Microservices

**Service 1: Owner Service**
- Manages owners
- Port: 8081
- Entities: Owner
- Repository: OwnerRepository

**Service 2: Pet Service**
- Manages pets
- Calls Owner Service to get owner data
- Port: 8082
- Entities: Pet, PetType
- Repository: PetRepository

**Service 3: Visit Service**
- Manages visits
- Calls Pet Service to get pet data
- Port: 8083
- Entities: Visit
- Repository: VisitRepository

**Service 4: Vet Service**
- Manages vets
- Port: 8084
- Entities: Vet, Specialty

**API Gateway**
- Routes to all services
- Port: 8080
- Uses Zuul or Spring Cloud Gateway

### Communication Patterns

**Synchronous (REST)**
```java
// Pet Service calls Owner Service
RestTemplate restTemplate = new RestTemplate();
Owner owner = restTemplate.getForObject(
    "http://owner-service:8081/api/owners/{id}",
    Owner.class,
    ownerId
);
```

**Asynchronous (Messaging)**
```java
// Pet Service publishes event
kafkaTemplate.send("pet-events", new PetCreatedEvent(pet));

// Notification Service listens
@KafkaListener(topics = "pet-events")
public void handlePetCreated(PetCreatedEvent event) {
    notificationService.sendEmail("New pet created");
}
```

### Resources
- [spring-petclinic-microservices](https://github.com/spring-projects/spring-petclinic-microservices)
- Spring Cloud Netflix (Eureka, Zuul)
- Spring Cloud Config
- Kafka for messaging

---

## 🎓 Complete Study Checklist

### Phase 1: Basics (2 weeks)
- [ ] Read Spring Boot Layers guide
- [ ] Understand IoC and DI
- [ ] Create simple Todo app
- [ ] Understand entity relationships
- [ ] Learn repository pattern

### Phase 2: Pet Clinic Deep Dive (2 weeks)
- [ ] Study entity layer
- [ ] Study repository layer
- [ ] Study controller layer
- [ ] Install Java 17+ ⚠️
- [ ] Run Spring Pet Clinic locally
- [ ] Create/read/update/delete owners
- [ ] Create/read pets
- [ ] Record visits
- [ ] Complete all assignments

### Phase 3: REST API (2 weeks)
- [ ] Clone spring-petclinic-rest
- [ ] Understand @RestController
- [ ] Understand DTOs
- [ ] Study service layer
- [ ] Understand HTTP status codes
- [ ] Test with Postman
- [ ] Convert Todo app to REST

### Phase 4: Security (2 weeks)
- [ ] Understand authentication vs authorization
- [ ] Learn Spring Security
- [ ] Implement BCrypt password hashing
- [ ] Learn JWT tokens
- [ ] Secure Pet Clinic REST API
- [ ] Test with JWT

### Phase 5: Microservices (2 weeks)
- [ ] Study microservices philosophy
- [ ] Understand service boundaries
- [ ] Learn service-to-service communication
- [ ] Learn API Gateway
- [ ] Study distributed tracing
- [ ] Split Pet Clinic into microservices

---

## ⚠️ IMPORTANT: Java Version Required

**Current:** Java 11.0.32  
**Required:** Java 17+ (LTS recommended: Java 21)

### How to Install Java 17+

**Option 1: Using Adoptium (Recommended)**
```bash
# Download from https://adoptium.net
# Select Java 21 (LTS)
# Install and verify
java -version
```

**Option 2: Using SDKMAN**
```bash
# Install SDKMAN from https://sdkman.io
# Then run
sdk install java 21.0.1-tem
sdk use java 21.0.1-tem
java -version
```

**Option 3: Using Chocolatey (Windows)**
```powershell
choco install openjdk21
java -version
```

---

## 📖 Additional Learning Resources

### Official Spring Documentation
- [Spring Boot Official](https://spring.io/projects/spring-boot)
- [Spring Data JPA](https://spring.io/projects/spring-data-jpa)
- [Spring Security](https://spring.io/projects/spring-security)
- [Spring Cloud](https://spring.io/projects/spring-cloud)

### Online Courses
- Baeldung (Medium articles on Spring)
- Spring Academy (by Spring team)
- Udemy/Coursera Spring Boot courses

### GitHub Repositories to Study
1. [spring-petclinic](https://github.com/spring-projects/spring-petclinic) (Web MVC)
2. [spring-petclinic-rest](https://github.com/spring-projects/spring-petclinic-rest) (REST API)
3. [spring-petclinic-microservices](https://github.com/spring-projects/spring-petclinic-microservices) (Full stack)
4. [spring-boot-examples](https://github.com/spring-projects/spring-boot/tree/main/spring-boot-samples) (Official examples)

### Books
- "Spring in Action" (Craig Walls) — Comprehensive Spring guide
- "Microservices Patterns" (Chris Richardson) — Microservices design

---

## 🎯 Success Metrics

By the end of each phase, you should be able to:

**Phase 1:**
- ✅ Explain IoC and DI in your own words
- ✅ Draw entity relationships
- ✅ Write a simple repository interface
- ✅ Understand MVC pattern

**Phase 2:**
- ✅ Run Spring Pet Clinic locally
- ✅ Add a new entity with relationships
- ✅ Write custom repository methods
- ✅ Trace a complete request flow

**Phase 3:**
- ✅ Build a REST API from scratch
- ✅ Return proper HTTP status codes
- ✅ Use Postman to test endpoints
- ✅ Understand DTOs and their purpose

**Phase 4:**
- ✅ Implement user login
- ✅ Hash passwords with BCrypt
- ✅ Generate and validate JWT tokens
- ✅ Restrict endpoints by role

**Phase 5:**
- ✅ Design a microservices architecture
- ✅ Implement service-to-service communication
- ✅ Deploy multiple services
- ✅ Understand eventual consistency

---

## 📝 Notes for Your Learning Journey

Remember these key principles as you progress:

1. **Start Simple** - Master Todo app before studying Pet Clinic
2. **Understand Patterns** - Spring uses well-known patterns everywhere
3. **Read Real Code** - Pet Clinic is production-ready code
4. **Hands-On Practice** - Don't just read; build and break things
5. **Test Your Understanding** - Can you explain concepts to someone else?
6. **Progress Gradually** - Web MVC → REST → Security → Microservices
7. **Review Frequently** - Concepts build on each other

---

## 🚀 Quick Start Guide

```bash
# 1. Install Java 17+
# Check version
java -version

# 2. Clone Spring Pet Clinic
cd c:\Workspace\OffLimits
git clone https://github.com/spring-projects/spring-petclinic.git

# 3. Start the app
cd spring-petclinic
./mvnw spring-boot:run    # or mvnw.cmd spring-boot:run on Windows

# 4. Open in browser
# http://localhost:8080

# 5. Explore the app
# - Create owner
# - Add pet
# - Record visit

# 6. Study the code
# - src/main/java/org/springframework/samples/petclinic/model/
# - src/main/java/org/springframework/samples/petclinic/owner/
# - src/main/java/org/springframework/samples/petclinic/vet/
```

---

Good luck on your Spring Boot learning journey! 🎓
