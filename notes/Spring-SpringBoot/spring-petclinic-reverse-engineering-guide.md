# Spring Pet Clinic — Complete Reverse Engineering Guide

A deep dive into the official Spring Boot project to understand all layers and concepts.

**Repository:** https://github.com/spring-projects/spring-petclinic  
**Located at:** `c:\Workspace\OffLimits\spring-petclinic`

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Project Structure](#project-structure)
4. [Entity Layer Deep Dive](#entity-layer-deep-dive)
5. [Repository Layer Deep Dive](#repository-layer-deep-dive)
6. [Controller Layer Deep Dive](#controller-layer-deep-dive)
7. [Data Flow Examples](#data-flow-examples)
8. [Running the Application](#running-the-application)
9. [Key Patterns & Best Practices](#key-patterns--best-practices)
10. [Study Checklist](#study-checklist)

---

## Project Overview

### What is Pet Clinic?
A sample veterinary clinic management system where:
- **Owners** register with their contact info
- **Owners** bring their **Pets** to the clinic
- **Vets** (veterinarians) with **Specialties** treat the pets
- **Visits** are recorded for each pet visit

### Domain Model
```
Owner (1) ─────────── (Many) Pet
  │ name                 │ name
  │ address              │ birthDate
  │ city                 │ type
  │ telephone            │
                         └─────────── (Many) Visit
                            │ date
                            │ description
                            └─────────── (Many) Vet

Vet (1) ─────────── (Many) Specialty
  │ name                 │ name (e.g., "Dentistry")
  │
  └─────────── (Many) Visit
```

### Tech Stack
- **Spring Boot 4.1.0** (Latest)
- **Java 17+**
- **Maven** (build tool)
- **JPA/Hibernate** (ORM)
- **H2 Database** (in-memory)
- **Spring MVC** (Web framework - returns HTML views)
- **Thymeleaf** (Template engine)

---

## Architecture & Design

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Web Browser (HTTP)                    │
└────────────────────────┬────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│           Web Layer (Controllers)                       │
│  @Controller (returns HTML views to browser)           │
│  ├── OwnerController                                   │
│  ├── PetController                                     │
│  ├── VisitController                                   │
│  └── VetController                                     │
└────────────────────────┬────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│         Domain Layer (Entities & Models)                │
│  Pure Java classes representing data                    │
│  ├── Owner                                              │
│  ├── Pet                                                │
│  ├── Visit                                              │
│  ├── Vet                                                │
│  └── Specialty                                          │
└────────────────────────┬────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│      Data Access Layer (Repositories)                   │
│  Interfaces that Spring implements automatically       │
│  ├── OwnerRepository (JpaRepository)                   │
│  ├── PetRepository (JpaRepository)                     │
│  ├── VetRepository (JpaRepository)                     │
│  └── PetTypeRepository (JpaRepository)                 │
└────────────────────────┬────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│               Database (H2 or MySQL)                    │
│  ├── owners table                                       │
│  ├── pets table                                         │
│  ├── visits table                                       │
│  ├── vets table                                         │
│  ├── specialties table                                  │
│  └── vet_specialties table (join table)                │
└─────────────────────────────────────────────────────────┘
```

### Key Design Patterns Used

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Repository Pattern** | OwnerRepository, PetRepository, etc. | Abstracts data access |
| **MVC Pattern** | Controller → View → Model | Separates concerns |
| **Inheritance** | BaseEntity → NamedEntity → Person → Owner/Vet | Code reuse |
| **Dependency Injection** | @Controller → OwnerRepository | Loose coupling |
| **Template Method** | BaseEntity.isNew() | Common functionality |

---

## Project Structure

### Full Directory Layout

```
spring-petclinic/
├── src/
│   ├── main/
│   │   ├── java/org/springframework/samples/petclinic/
│   │   │   ├── PetClinicApplication.java         ← Main entry point
│   │   │   ├── model/                            ← Base entity classes
│   │   │   │   ├── BaseEntity.java               ← ID, getId(), isNew()
│   │   │   │   ├── NamedEntity.java              ← Adds name field
│   │   │   │   └── Person.java                   ← Adds firstName, lastName
│   │   │   ├── owner/                            ← Owner domain & controllers
│   │   │   │   ├── Owner.java                    ← Entity (extends Person)
│   │   │   │   ├── Pet.java                      ← Entity
│   │   │   │   ├── Visit.java                    ← Entity
│   │   │   │   ├── PetType.java                  ← Entity (dog, cat, etc)
│   │   │   │   ├── OwnerRepository.java          ← JpaRepository
│   │   │   │   ├── PetRepository.java            ← JpaRepository
│   │   │   │   ├── PetTypeRepository.java        ← JpaRepository
│   │   │   │   ├── OwnerController.java          ← Web controller
│   │   │   │   ├── PetController.java            ← Web controller
│   │   │   │   ├── VisitController.java          ← Web controller
│   │   │   │   ├── PetValidator.java             ← Validation logic
│   │   │   │   └── PetTypeFormatter.java         ← Data formatting
│   │   │   ├── vet/                              ← Vet domain & controllers
│   │   │   │   ├── Vet.java                      ← Entity (extends Person)
│   │   │   │   ├── Specialty.java                ← Entity
│   │   │   │   ├── Vets.java                     ← Data transfer object
│   │   │   │   ├── VetRepository.java            ← JpaRepository
│   │   │   │   └── VetController.java            ← Web controller
│   │   │   └── system/                           ← System utilities
│   │   │       └── WelcomeController.java        ← Home page
│   │   └── resources/
│   │       ├── application.properties            ← Configuration
│   │       ├── data.sql                          ← Initial data (schema creation)
│   │       └── templates/                        ← Thymeleaf HTML templates
│   │           ├── owners/                       ← Owner pages
│   │           │   ├── ownersList.html
│   │           │   ├── ownerDetails.html
│   │           │   ├── createOrUpdateOwnerForm.html
│   │           ├── pets/                         ← Pet pages
│   │           ├── visits/                       ← Visit pages
│   │           └── vets/                         ← Vet pages
│   └── test/
│       └── java/org/springframework/samples/petclinic/
│           └── (Test classes)
├── pom.xml                                        ← Maven configuration
├── Dockerfile                                     ← Container setup
├── docker-compose.yml                            ← Multi-container setup
└── README.md
```

---

## Entity Layer Deep Dive

### 1. Base Entity Hierarchy

Pet Clinic uses **entity inheritance** — a clever pattern to avoid repeating common code.

#### BaseEntity.java
```java
@MappedSuperclass  // Not a table — parent for other entities
public class BaseEntity implements Serializable {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    
    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    
    public boolean isNew() {
        return this.id == null;  // New if not yet saved
    }
}
```

**Key Concept: @MappedSuperclass**
- Does NOT create a table for BaseEntity
- Child classes inherit id and methods
- All child entities have auto-generated ID
- Avoids duplicating ID code across entities

#### NamedEntity.java
```java
@MappedSuperclass
public class NamedEntity extends BaseEntity {
    
    @Column(name = "name")
    private String name;
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}
```

#### Person.java
```java
@MappedSuperclass
public class Person extends NamedEntity {
    
    @Column(name = "first_name")
    private String firstName;
    
    @Column(name = "last_name")
    private String lastName;
    
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
}
```

**Inheritance Chain:**
```
BaseEntity (has: id)
    ↓
NamedEntity (has: id, name)
    ↓
Person (has: id, name, firstName, lastName)
    ↓
Owner (has: id, name, firstName, lastName, address, city, telephone, pets)
```

### 2. Owner Entity

```java
@Entity
@Table(name = "owners")
public class Owner extends Person {
    
    @Column(name = "address")
    @NotBlank
    private String address;
    
    @Column(name = "city")
    @NotBlank
    private String city;
    
    @Column(name = "telephone")
    @NotBlank
    private String telephone;
    
    // One owner can have many pets
    @OneToMany(cascade = CascadeType.ALL, mappedBy = "owner")
    @OrderBy("name")
    private List<Pet> pets = new ArrayList<>();
    
    public Pet addPet(Pet pet) {
        if (pet != null) {
            if (!getPets().contains(pet)) {
                getPets().add(pet);
            }
            pet.setOwner(this);
        }
        return pet;
    }
}
```

**Database Table Created:**
```sql
CREATE TABLE owners (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    name VARCHAR(255),    -- inherited from NamedEntity
    address VARCHAR(255),
    city VARCHAR(255),
    telephone VARCHAR(20)
);
```

**Key Annotations:**
- `@OneToMany(cascade = CascadeType.ALL, mappedBy = "owner")`
  - **cascade = ALL** = Delete owner → Delete all their pets
  - **mappedBy = "owner"** = Pet has a field called "owner" that references Owner
- `@OrderBy("name")` = Load pets sorted by name
- `@NotBlank` = Validation — cannot be empty

### 3. Pet Entity

```java
@Entity
@Table(name = "pets")
public class Pet extends NamedEntity {
    
    @Column(name = "birth_date")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate birthDate;
    
    @ManyToOne
    @JoinColumn(name = "type_id")
    private PetType type;  // dog, cat, bird, etc
    
    // Many pets belong to one owner
    @ManyToOne
    @JoinColumn(name = "owner_id")
    private Owner owner;
    
    // One pet can have many visits
    @OneToMany(cascade = CascadeType.ALL, mappedBy = "pet")
    @OrderBy("visitDate desc")
    private Set<Visit> visits = new LinkedHashSet<>();
}
```

**Relationships:**
- Pet → Owner (Many-to-One): Many pets belong to one owner
- Pet → PetType (Many-to-One): Many pets can be the same type
- Pet → Visit (One-to-Many): One pet can have many visits

**Database Table:**
```sql
CREATE TABLE pets (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    birth_date DATE,
    type_id INTEGER,
    owner_id INTEGER,
    FOREIGN KEY (type_id) REFERENCES pet_types(id),
    FOREIGN KEY (owner_id) REFERENCES owners(id)
);
```

### 4. Visit Entity

```java
@Entity
@Table(name = "visits")
public class Visit extends BaseEntity {
    
    @Column(name = "visit_date")
    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDate visitDate;
    
    @Column(name = "description")
    private String description;
    
    // Many visits belong to one pet
    @ManyToOne
    @JoinColumn(name = "pet_id")
    private Pet pet;
}
```

### 5. Vet & Specialty Entities

```java
@Entity
@Table(name = "vets")
public class Vet extends Person {
    
    // Many-to-Many: One vet has many specialties
    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "vet_specialties",
        joinColumns = @JoinColumn(name = "vet_id"),
        inverseJoinColumns = @JoinColumn(name = "specialty_id")
    )
    private Set<Specialty> specialties = new HashSet<>();
}

@Entity
@Table(name = "specialties")
public class Specialty extends NamedEntity {
    // Just a name (dentistry, surgery, etc)
}
```

**Many-to-Many Join Table:**
```sql
CREATE TABLE vet_specialties (
    vet_id INTEGER,
    specialty_id INTEGER,
    PRIMARY KEY (vet_id, specialty_id),
    FOREIGN KEY (vet_id) REFERENCES vets(id),
    FOREIGN KEY (specialty_id) REFERENCES specialties(id)
);
```

---

## Repository Layer Deep Dive

### What is a Repository?

Pet Clinic uses **Spring Data JPA** repositories — you write an interface, Spring implements it automatically.

```java
public interface OwnerRepository extends JpaRepository<Owner, Integer> {
    // You define methods here
    // Spring writes SQL automatically!
}
```

### Inheritance: JpaRepository

```
JpaRepository<T, ID>
    ↑
    │ Extends
    ↓
PagingAndSortingRepository<T, ID>
    ↑
    │ Extends
    ↓
CrudRepository<T, ID>
```

**Methods you get for FREE:**

| Method | SQL Generated |
|--------|---|
| `save(T entity)` | INSERT or UPDATE |
| `findById(ID id)` | SELECT * WHERE id = ? |
| `findAll()` | SELECT * |
| `findAll(Pageable page)` | SELECT * LIMIT offset, size |
| `delete(T entity)` | DELETE WHERE id = ? |
| `deleteById(ID id)` | DELETE WHERE id = ? |
| `count()` | SELECT COUNT(*) |
| `exists(ID id)` | SELECT COUNT(*) > 0 |

### 1. OwnerRepository

```java
public interface OwnerRepository extends JpaRepository<Owner, Integer> {
    
    // Spring generates: SELECT * FROM owners WHERE last_name LIKE 'searchTerm%'
    Page<Owner> findByLastNameStartingWith(String lastName, Pageable pageable);
}
```

**How Spring understands this:**
- `findBy` = SELECT query
- `LastNameStartingWith` = WHERE lastName LIKE ?%
- `Page<...>, Pageable` = Add LIMIT/OFFSET for pagination

### 2. PetTypeRepository

```java
public interface PetTypeRepository extends JpaRepository<PetType, Integer> {
    // Find by exact name
    PetType findByName(String name);
}
```

### 3. PetRepository

```java
public interface PetRepository extends JpaRepository<Pet, Integer> {
    // Query derived from method name
    List<Pet> findByOwner(Owner owner);
}
```

### 4. VetRepository

```java
public interface VetRepository extends JpaRepository<Vet, Integer> {
    // Find all vets (inherited from JpaRepository)
}
```

### Custom Queries with @Query

If method name is too complex, use `@Query`:

```java
@Query("SELECT v FROM Vet v WHERE SIZE(v.specialties) = 0")
List<Vet> findAllWithoutSpecialties();
```

---

## Controller Layer Deep Dive

### Note: This Project Uses @Controller, Not @RestController

Pet Clinic is a **Web MVC app**, not a REST API:
- `@Controller` returns HTML pages
- `@RestController` returns JSON

If you see `@Controller` — it returns HTML views (like ownersList.html)

### OwnerController Structure

```java
@Controller
class OwnerController {
    
    private final OwnerRepository owners;
    
    // Dependency Injection via constructor
    public OwnerController(OwnerRepository owners) {
        this.owners = owners;
    }
    
    // ============ LIST OWNERS ============
    @GetMapping("/owners")
    public String processFindForm(Owner owner, BindingResult result, Model model, Pageable pageable) {
        // GET /owners → Show search form + results
    }
    
    // ============ OWNER DETAILS ============
    @GetMapping("/owners/{ownerId}")
    public ModelAndView showOwner(@PathVariable("ownerId") int ownerId) {
        // GET /owners/{id} → Show owner details page
    }
    
    // ============ CREATE OWNER ============
    @GetMapping("/owners/new")
    public String initCreationForm(Model model) {
        // GET /owners/new → Show create form (HTML)
    }
    
    @PostMapping("/owners/new")
    public String processCreationForm(@Valid Owner owner, BindingResult result) {
        // POST /owners/new → Process form submission
        if (result.hasErrors()) {
            return "owners/createOrUpdateOwnerForm";  // Return to form if errors
        }
        this.owners.save(owner);  // Save to database
        return "redirect:/owners/" + owner.getId();   // Redirect to details
    }
    
    // ============ UPDATE OWNER ============
    @GetMapping("/owners/{ownerId}/edit")
    public String initUpdateOwnerForm(@PathVariable("ownerId") int ownerId, Model model) {
        // GET /owners/{id}/edit → Show edit form
    }
    
    @PostMapping("/owners/{ownerId}/edit")
    public String processUpdateOwnerForm(@Valid Owner owner, 
                                         BindingResult result,
                                         @PathVariable("ownerId") int ownerId) {
        // POST /owners/{id}/edit → Save changes
        if (result.hasErrors()) {
            return "owners/createOrUpdateOwnerForm";
        }
        this.owners.save(owner);
        return "redirect:/owners/" + ownerId;
    }
}
```

### PetController

```java
@Controller
class PetController {
    
    private final PetRepository pets;
    private final OwnerRepository owners;
    private final PetTypeRepository petTypes;
    private final PetValidator petValidator;
    
    @InitBinder("owner")
    public void initOwnerBinder(WebDataBinder dataBinder) {
        dataBinder.setDisallowedFields("id");  // Don't allow changing owner ID
    }
    
    @InitBinder("pet")
    public void initPetBinder(WebDataBinder dataBinder) {
        dataBinder.addValidator(petValidator);  // Validate pet
        dataBinder.setDisallowedFields("id");
    }
    
    // ============ CREATE PET ============
    @GetMapping("/owners/{ownerId}/pets/new")
    public String initCreationForm(Owner owner, Model model) {
        // GET /owners/{id}/pets/new → Show pet creation form
        Pet pet = new Pet();
        owner.addPet(pet);
        model.addAttribute("pet", pet);
        model.addAttribute("types", this.petTypes.findAll());
        return "pets/createOrUpdatePetForm";
    }
    
    @PostMapping("/owners/{ownerId}/pets/new")
    public String processCreationForm(Owner owner, @Valid Pet pet, 
                                      BindingResult result, Model model) {
        // POST /owners/{id}/pets/new → Save new pet
        if (StringUtils.hasLength(pet.getName()) && pet.isNew() && owner.getPet(pet.getName(), true) != null) {
            result.rejectValue("name", "duplicate", "Pet name already exists");
        }
        if (result.hasErrors()) {
            model.addAttribute("types", this.petTypes.findAll());
            return "pets/createOrUpdatePetForm";
        }
        this.pets.save(pet);
        return "redirect:/owners/" + owner.getId();
    }
}
```

### VisitController

```java
@Controller
class VisitController {
    
    private static final String VIEWS_VISIT_CREATE_OR_UPDATE_FORM = "visits/createOrUpdateVisitForm";
    
    private final PetRepository pets;
    
    @InitBinder
    public void setAllowedFields(WebDataBinder dataBinder) {
        dataBinder.setDisallowedFields("id");
    }
    
    // ============ CREATE VISIT ============
    @GetMapping("/owners/*/pets/{petId}/visits/new")
    public String initNewVisitForm(@PathVariable("petId") int petId, Model model) {
        // GET /owners/*/pets/{petId}/visits/new → Show visit form
        Pet pet = this.pets.findById(petId).orElse(null);
        model.addAttribute("visit", new Visit());
        model.addAttribute("pet", pet);
        return VIEWS_VISIT_CREATE_OR_UPDATE_FORM;
    }
    
    @PostMapping("/owners/*/pets/{petId}/visits/new")
    public String processNewVisitForm(@Valid Visit visit, BindingResult result) {
        // POST /owners/*/pets/{petId}/visits/new → Save visit
        if (result.hasErrors()) {
            return VIEWS_VISIT_CREATE_OR_UPDATE_FORM;
        }
        this.pets.save(visit.getPet());  // Save pet (which cascades to visit)
        return "redirect:/owners/" + visit.getPet().getOwner().getId();
    }
}
```

### VetController (Simple)

```java
@Controller
class VetController {
    
    private final VetRepository vets;
    
    @GetMapping("/vets")
    public String showVetList(Model model) {
        // GET /vets → Show all vets
        model.addAttribute("vets", this.vets.findAll());
        return "vets/vetList";
    }
}
```

---

## Data Flow Examples

### Flow 1: Create a New Owner

**User visits:** http://localhost:8080/owners/new

1. **Browser** → GET /owners/new
2. **OwnerController.initCreationForm()** called
   - Creates empty Owner object
   - Adds to model: `model.addAttribute("owner", owner)`
   - Returns: `"owners/createOrUpdateOwnerForm"` (HTML file)
3. **Thymeleaf** renders HTML form with fields for:
   - First name, Last name, Address, City, Telephone
4. **User fills form and submits** → POST /owners/new
5. **OwnerController.processCreationForm()** called
   - Gets Owner object from form data
   - Spring validates with `@NotBlank` annotations
   - If errors: return form with error messages
   - If valid: `owners.save(owner)` → **saves to database**
   - Returns: `"redirect:/owners/{id}"` (redirect to details)
6. **Browser** → GET /owners/{id}
7. **OwnerController.showOwner()** called
   - Retrieves owner from database: `owners.findById(id)`
   - Returns: `"owners/ownerDetails"` (HTML page)

**Database changes:**
```sql
INSERT INTO owners (first_name, last_name, address, city, telephone) 
VALUES ('John', 'Doe', '123 Main St', 'Madison', '555-1234');
-- Returns: id = 1 (auto-generated)
```

---

### Flow 2: Add a Pet to Owner

**User visits:** http://localhost:8080/owners/{ownerId}/pets/new

1. **Browser** → GET /owners/1/pets/new
2. **PetController.initCreationForm()** called
   - Gets Owner with id=1: `ownerRepository.findById(1)`
   - Creates empty Pet
   - Sets pet's owner: `owner.addPet(pet)`
   - Loads all pet types (Dog, Cat, Bird):  `petTypes.findAll()`
   - Returns form HTML
3. **User selects pet type and fills name** → POST /owners/1/pets/new
4. **PetController.processCreationForm()** called
   - Validates pet (via `PetValidator`)
   - If valid: `pets.save(pet)` → **saves to database**
   - Returns: redirect to owner details
5. **Browser** → GET /owners/1
6. Owner's pets list now shows the new pet

**Database changes:**
```sql
INSERT INTO pets (name, birth_date, type_id, owner_id) 
VALUES ('Rex', '2020-01-15', 1, 1);  -- type_id=1 is Dog, owner_id=1 is John Doe
```

---

### Flow 3: Record a Visit

**User visits:** http://localhost:8080/owners/{ownerId}/pets/{petId}/visits/new

1. **Browser** → GET /owners/1/pets/2/visits/new
2. **VisitController.initNewVisitForm()** called
   - Gets Pet with id=2: `petRepository.findById(2)`
   - Creates empty Visit
   - Returns form
3. **User enters description, date** → POST /owners/1/pets/2/visits/new
4. **VisitController.processNewVisitForm()** called
   - Validates visit
   - Sets visit.setPet(pet) (already set)
   - Saves: `pets.save(visit.getPet())`
   - Why pets? Because Visit cascades from Pet
   - Returns: redirect to owner details
5. **Owner details page shows pet with new visit in list**

**Database changes:**
```sql
INSERT INTO visits (visit_date, description, pet_id) 
VALUES ('2025-09-05', 'Annual checkup', 2);
```

---

## Running the Application

### Prerequisites
- Java 17+ installed
- Maven (comes with project)

### Start the Application

```bash
# Navigate to project
cd c:\Workspace\OffLimits\spring-petclinic

# Run with Maven
./mvnw spring-boot:run

# Or Windows
mvnw.cmd spring-boot:run
```

### Access the App
- **URL:** http://localhost:8080
- **Features:** 
  - Home page → Links to owners, vets
  - Owners → Search, create, view, edit
  - Pets → Create under owners, view details
  - Visits → Record under pets
  - Vets → View all vets and specialties

### Database
- **Type:** H2 (in-memory)
- **Data:** Loads from `src/main/resources/data.sql` on startup
- **Resets:** Every time you restart (in-memory)
- **Persistence:** To use MySQL/PostgreSQL, edit `application.properties`

---

## Key Patterns & Best Practices

### 1. Dependency Injection via Constructor

```java
@Controller
class OwnerController {
    private final OwnerRepository owners;
    
    // ← Spring injects repository here
    public OwnerController(OwnerRepository owners) {
        this.owners = owners;
    }
}
```

**Why?**
- More testable (easy to pass mock)
- Immutable (final)
- Clear dependencies

### 2. Entity Inheritance

```
BaseEntity (id)
    ↓
NamedEntity (name)
    ↓
Person (firstName, lastName)
    ↓
Owner (address, city, telephone, pets)
```

**Benefit:** No code duplication

### 3. Cascade Operations

```java
@OneToMany(cascade = CascadeType.ALL, mappedBy = "owner")
private List<Pet> pets;
```

**CascadeType.ALL means:**
- Save owner → also saves all pets
- Delete owner → also deletes all pets
- Update owner → also updates pets

### 4. Data Validation

```java
@Entity
public class Owner extends Person {
    
    @NotBlank(message = "Address cannot be empty")
    private String address;
    
    @Pattern(regexp = "^\\d{3}-\\d{3}-\\d{4}$", message = "Invalid phone format")
    private String telephone;
}
```

Spring validates automatically in controller:
```java
@PostMapping("/owners/new")
public String processCreationForm(@Valid Owner owner, BindingResult result) {
    if (result.hasErrors()) {
        return "form";  // Show form with errors
    }
    // ... save owner
}
```

### 5. @InitBinder for Custom Binding

```java
@InitBinder("pet")
public void initPetBinder(WebDataBinder dataBinder) {
    dataBinder.addValidator(petValidator);     // Add validator
    dataBinder.setDisallowedFields("id");      // Don't allow changing ID
}
```

**Purpose:** 
- Customize how form data is converted to objects
- Prevent tampering with critical fields (like ID)
- Add custom validation

### 6. Many-to-Many Relationships

```java
@Entity
public class Vet {
    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
        name = "vet_specialties",
        joinColumns = @JoinColumn(name = "vet_id"),
        inverseJoinColumns = @JoinColumn(name = "specialty_id")
    )
    private Set<Specialty> specialties;
}
```

**Join Table:** 
- Bridge table connecting vets and specialties
- Avoids duplicating data (e.g., can't store "specialties" in vet row)
- Allows one vet to have multiple specialties

### 7. Derived Query Methods

```java
public interface OwnerRepository extends JpaRepository<Owner, Integer> {
    // Spring reads method name and generates SQL
    Page<Owner> findByLastNameStartingWith(String lastName, Pageable pageable);
    
    // Equivalent to:
    // SELECT * FROM owners WHERE last_name LIKE ? ORDER BY ... LIMIT offset size
}
```

**Method Name Parts:**
- `findBy` = SELECT WHERE
- `LastName` = owners.last_name column
- `StartingWith` = LIKE ?%
- `Page<..., Pageable>` = Pagination

---

## Study Checklist

### Phase 1: Understand the Domain (1-2 hours)
- [ ] Read README.md
- [ ] Understand the domain (Owners, Pets, Vets, Visits)
- [ ] Draw the entity relationship diagram
- [ ] Identify One-to-Many relationships (Owner → Pets)
- [ ] Identify Many-to-Many relationships (Vet ↔ Specialty)

### Phase 2: Explore Entity Layer (2-3 hours)
- [ ] Read [BaseEntity.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/model/BaseEntity.java)
- [ ] Read [Owner.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/Owner.java)
- [ ] Read [Pet.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/Pet.java)
- [ ] Read [Visit.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/Visit.java)
- [ ] Read [Vet.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/vet/Vet.java)
- [ ] Understand @Entity, @Table, @Column, @ManyToOne, @OneToMany, @ManyToMany
- [ ] Understand cascade operations
- [ ] Understand @MappedSuperclass vs @Entity

### Phase 3: Explore Repository Layer (1-2 hours)
- [ ] Read [OwnerRepository.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java)
- [ ] Read [PetRepository.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/PetRepository.java)
- [ ] Read [VetRepository.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/vet/VetRepository.java)
- [ ] Understand how Spring generates SQL from method names
- [ ] Test query methods: findByLastNameStartingWith, findByOwner, etc.

### Phase 4: Explore Controller Layer (2-3 hours)
- [ ] Read [OwnerController.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java)
- [ ] Read [PetController.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/PetController.java)
- [ ] Read [VisitController.java](../../spring-petclinic/src/main/java/org/springframework/samples/petclinic/owner/VisitController.java)
- [ ] Understand @Controller vs @RestController
- [ ] Understand @GetMapping, @PostMapping, @PathVariable
- [ ] Understand ModelAndView, Model, BindingResult
- [ ] Understand form binding and validation

### Phase 5: Run the Application (1 hour)
- [ ] Start the app: `./mvnw spring-boot:run`
- [ ] Visit http://localhost:8080
- [ ] Create an owner
- [ ] Add a pet to the owner
- [ ] Record a visit for the pet
- [ ] Edit owner details
- [ ] Check database changes

### Phase 6: Understand Data Flow (1 hour)
- [ ] Trace the flow: Owners list → Details → Edit → Save
- [ ] Trace the flow: Owner → Create pet → Save
- [ ] Trace the flow: Pet → Create visit → Save
- [ ] Understand how form data is converted to objects
- [ ] Understand how validation errors are displayed

### Phase 7: Advanced Concepts (2 hours)
- [ ] Understand @InitBinder and custom binding
- [ ] Understand @Transactional (if used)
- [ ] Understand lazy vs eager loading (@OneToMany(fetch=...))
- [ ] Understand how Spring manages entity relationships
- [ ] Understand open session in view pattern

### Phase 8: Practice (2-4 hours)
- [ ] Add a new feature: "Owner Notes" (text field on owner)
- [ ] Add a new feature: "Pet Weight" (track weight over visits)
- [ ] Add a new feature: "Vet Reviews" (owners review vets)
- [ ] Modify an existing feature: Sort owners by registration date

### Phase 9: Move to REST API Version (1-2 hours)
After mastering the MVC version:
- [ ] Find: `spring-petclinic-rest` repository (REST API version)
- [ ] Compare with MVC version
- [ ] Notice: Services layer, DTOs, Exception handling
- [ ] Notice: `@RestController`, `@RequestBody`, `@ResponseStatus`

---

## Next Learning Paths

### After Mastering Spring Pet Clinic:

**1. REST API Path** (3-5 hours)
- Clone `spring-petclinic-rest` repository
- Learn `@RestController` vs `@Controller`
- Learn request/response DTOs
- Learn exception handling
- Learn HTTP status codes

**2. Security Path** (4-6 hours)
- Add Spring Security to Pet Clinic
- Learn authentication (login/logout)
- Learn authorization (roles, permissions)
- Learn JWT tokens
- Recommended: `spring-petclinic-microservices` (has security examples)

**3. Microservices Path** (8-12 hours)
- Split Pet Clinic into microservices
- Learn Service-to-service communication
- Learn API Gateway
- Learn Config Server
- Repository: `spring-petclinic-microservices`

**4. Testing Path** (3-5 hours)
- Unit tests for entities
- Unit tests for repositories
- Integration tests for controllers
- Learn @WebMvcTest, @DataJpaTest
- Learn Mockito

---

## File Locations for Deep Study

| Topic | File |
|-------|------|
| Entry point | `PetClinicApplication.java` |
| Base entity | `model/BaseEntity.java` |
| Entity hierarchy | `model/Person.java` |
| Owner entity | `owner/Owner.java` |
| Pet entity | `owner/Pet.java` |
| Owner repository | `owner/OwnerRepository.java` |
| Owner controller | `owner/OwnerController.java` |
| Pet controller | `owner/PetController.java` |
| Visit controller | `owner/VisitController.java` |
| Configuration | `application.properties` |
| Initial data | `data.sql` |
| HTML templates | `resources/templates/` |

---

## Common Questions

**Q: Why use @Controller and not @RestController?**  
A: This is a web application returning HTML pages (MVC), not an API returning JSON. @Controller is correct for this use case.

**Q: Why extend Person instead of BaseEntity directly?**  
A: To reuse firstName, lastName fields. Pet Clinic shows good OOP design.

**Q: How does pagination work?**  
A: `Pageable` is passed to repository. Spring generates: `SELECT ... LIMIT offset, size`. JpaRepository returns `Page<Owner>` which has info about total pages, current page, etc.

**Q: What is @MappedSuperclass?**  
A: Used for inheritance where parent is NOT a table. All columns go to child tables. Different from `@Entity` inheritance where parent IS a table.

**Q: Can I convert this to use a REST API?**  
A: Yes! Clone `spring-petclinic-rest` which is the same domain with REST endpoints instead.

---
