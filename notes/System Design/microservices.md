 ok # Microservices

## What's a Microservice?
Instead of one big app (monolith), break it into many small, independent services:
- Each service does **one thing well** (single responsibility)
- Each has its own database (no shared DB)
- Services talk to each other via APIs (REST, gRPC, messages)
- Deploy/scale independently

**Monolith Example:**
```
One big app (User Service + Order Service + Payment Service all in one)
├── User DB
├── Order DB
└── Payment DB
```

**Microservices Example:**
```
User Service        Order Service       Payment Service
├── User DB         ├── Order DB        └── Payment DB
└── REST API        └── REST API
     ↓                  ↓                      ↑
     └──────────────────────────────────────→
         (Services call each other)
```

## Why Microservices? (Trade-offs)

| Benefit | Cost |
|---------|------|
| Scale services independently | More complex networking/debugging |
| Deploy service without stopping others | Need sophisticated deployment/monitoring |
| Different tech stacks per service | More moving parts, more things to break |
| Easier to understand (small codebase) | Must coordinate across services |
| Different databases per service | Distributed transactions are hard |

**Bottom line:** Microservices add complexity but give you **flexibility and scalability**. Use them when you need it, not by default.

## When to Use Microservices

**Good fit:**
- Large team (split work by service)
- Different services scale independently
- Different tech stacks per service
- Need rapid deployment cycles

**Bad fit:**
- Small team / simple app
- Strong need for ACID transactions across data
- All services scale together anyway

---

## Design Patterns (See Separate Files)

Key patterns for building microservices architectures:
- [Decomposition Pattern](decomposition-pattern.md) — How to break a monolith into services
- [Strangler Pattern](strangler-pattern.md) — Incrementally migrate to microservices
- [SAGA Pattern](saga-pattern.md) — Distributed transactions across services
- [CQRS](cqrs-pattern.md) — Separate read and write models

