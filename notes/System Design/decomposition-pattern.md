# Decomposition Pattern

## The Problem: Monolith is Too Big

You have one giant application:
- Hard to understand (too much code in one place)
- Hard to scale (if User feature is popular, you scale the entire app, wasting resources on Order processing)
- Hard to change (small change to User Service requires testing entire app)
- Hard to deploy (deploy Order feature = restart everything, risk breaking User Service)
- One team can't own it all (multiple teams stepping on each other)

**Question:** How do you break a monolith into microservices?

## The Solution: Decompose by Responsibility

Identify service boundaries by looking at:
1. **Subdomain / Business Domain** — What business capabilities exist?
2. **Data / Database** — What data does this domain own?
3. **API / External Contracts** — What does the outside world call this service for?

**Example: E-Commerce Monolith**

**Before (Monolith):**
```
┌─────────────────────────────────────────────────┐
│         E-Commerce App                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Users     │  │   Orders    │  │ Payment │ │
│  │             │  │             │  │         │ │
│  │ - Signin    │  │ - Create    │  │- Charge │ │
│  │ - Profile   │  │ - List      │  │- Refund │ │
│  │ - Checkout  │  │ - Cancel    │  │         │ │
│  │             │  │ - Inventory │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
│              (All in one codebase)              │
└─────────────────────────────────────────────────┘
```

**After (Decomposed):**
```
User Service           Order Service          Payment Service
├── Signin             ├── Create Order       ├── Charge Card
├── Profile            ├── List Orders        ├── Refund
└── Auth               ├── Cancel             └── Webhook Handlers
│                      │
│ (own database)       │ (own database)       (own database)
│                      │
└─ Inventory Service
   ├── Check Stock
   ├── Reserve
   └── Release
   (own database)
```

## How to Decompose: Step by Step

### 1. **Identify Business Domains (Domain-Driven Design)**
Look at your business, not the code:
- **User Domain:** Everything about managing users (auth, profiles)
- **Order Domain:** Everything about creating/managing orders
- **Payment Domain:** Everything about charging money
- **Inventory Domain:** Everything about stock levels

**Question to ask:** "Could I build this domain independently if I had a separate team?"

### 2. **Identify Data Ownership**
Each service should own its data:
- User Service owns: users table, profiles, credentials
- Order Service owns: orders table, order items
- Payment Service owns: transactions, refunds
- Inventory Service owns: stock levels, reservations

**No sharing a database!** If Order Service needs user email, it gets a copy (eventual consistency).

### 3. **Define Service Boundaries**
Each service exposes:
- **Public API:** REST endpoints other services call
- **Events:** Things this service publishes (User signed up → publish event)
- **Database:** Only this service writes to it

**Example APIs:**
```
User Service:
  GET /users/{id}
  POST /users
  POST /users/{id}/auth

Order Service:
  POST /orders
  GET /orders/{id}
  PATCH /orders/{id}/cancel

Payment Service:
  POST /payments/charge
  POST /payments/{id}/refund
```

### 4. **Handle Cross-Service Dependencies**
**Scenario:** Order Service needs user's email to send confirmation

**Wrong (tightly coupled):**
```javascript
// Order Service calls User Service synchronously
const user = await userService.getUser(userId);
order.notify(user.email);  // Blocks if User Service is down
```

**Right (loosely coupled):**
- **Option A (Sync with timeout):** Order Service calls User Service, but if it times out, use cached/stale data
- **Option B (Async):** User Service publishes "User Updated" event → Order Service subscribes and caches email
- **Option C (Denormalization):** Order Service keeps its own copy of user email (sync via events)

### 5. **Data Consistency Strategy**
Since services have separate databases, decide:
- **Synchronous:** Order Service queries User Service for current data (latency, tight coupling)
- **Asynchronous:** Services publish events; others listen and cache (loose coupling, eventual consistency)
- **Replication:** Order Service keeps a copy of user data, synced via events (best for performance)

**Example:**
```
1. User Service: User email changed
2. User Service: publishes "UserEmailChanged" event
3. Order Service: subscribes, updates cached email
4. Order Service: next time it needs email, it's already there
```

## Common Decomposition Mistakes

### ❌ Mistake 1: Decomposing by Technology Layer
**Wrong:**
```
Service A: "UserController, UserService, UserRepository"
Service B: "OrderController, OrderService, OrderRepository"
```
This just splits a monolith vertically, doesn't solve the problem.

**Right:**
```
User Service: Everything related to users (controller, logic, database)
Order Service: Everything related to orders
```

### ❌ Mistake 2: Services Too Small
**Wrong:**
```
GetUserService, SaveUserService, DeleteUserService
```
You'll end up calling many services per request = network overhead.

**Right:**
```
User Service: handles all user operations
```

### ❌ Mistake 3: Services Too Big
**Wrong:**
```
Everything-But-Payment Service
```
Defeats the purpose (still hard to understand/scale).

**Right:**
Use domain-driven design; if it's a distinct capability, it's a service.

### ❌ Mistake 4: Sharing a Database
**Wrong:**
```
User Service and Order Service both write to shared database
```
No longer microservices; you lose independence, scaling, deployment benefits.

**Right:**
Each service has its own database.

## When to Decompose

**Good time:**
- Monolith is large (10K+ lines or growing team)
- Teams stepping on each other's code
- Different parts scale differently
- Want independent deployment

**Not ready yet:**
- Monolith is small and maintainable
- Team is tiny (< 10 people)
- Don't need independent scaling

**Pro tip:** Start as monolith, decompose when you feel the pain. Don't over-architect upfront.

## Interview Frame

**Q: How would you decompose this monolith?**
A: Identify business domains using Domain-Driven Design. Each domain becomes a service. Each service owns its data. Define APIs and async events for communication. Ensure no shared database.

**Q: How do you decide if something should be a separate service?**
A: Ask: "Can a team own this independently? Does it have distinct data? Can it scale separately?" If yes to most, make it a service.

**Q: What about data consistency across services?**
A: Use eventual consistency. Services publish events; others listen and cache data. Sync via message queues, not direct database access.
