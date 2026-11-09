# System Design Learning Pipeline

This is your structured learning path. Work through topics in order, then revisit as needed.

## ✅ Completed

- [x] **Why System Design** — understand scope, trade-offs, and real-world constraints
- [x] **HLD Basics** — learn fundamental patterns (monolith vs microservices, layers, databases)
- [x] **Consistent Hashing** — load balancing and distributing requests/data across servers
- [x] **Message Queues** — async communication, decoupling, delivery guarantees, request-reply patterns

## 🟡 In Progress

- [ ] **Webhooks** — push-based notifications, callback patterns, reliability & idempotency
- [ ] **Message Queues (Deep Dive)** — topics vs queues, pub/sub patterns, Kafka vs RabbitMQ
- [ ] **CAP Theorem** — consistency vs availability trade-offs, choosing what matters for your system

## ⏳ Up Next (Pick One)

1. **Caching Strategies** — in-memory caches (Redis), cache invalidation, CDN for static assets
2. **Database Replication & Sharding** — scaling storage, master-slave patterns, shard key selection
3. **Rate Limiting & Backpressure** — protect services from overload, token bucket, sliding window
4. **Load Balancing** — round-robin, least connections, sticky sessions, health checks

## 📋 Essential Topics (Later)

- **API Gateway** — routing, authentication, rate limiting at entry point
- **Distributed Transactions** — 2-phase commit vs eventual consistency, saga pattern
- **Circuit Breaker Pattern** — prevent cascading failures, retry logic
- **Monitoring & Logging** — observability, metrics, alerting
- **Fault Tolerance & Failover** — redundancy, graceful degradation
- **Service Discovery** — how services find each other (Consul, Kubernetes DNS)
- **CORS & Security** — cross-origin, authentication, authorization
- **Time & Synchronization** — clock skew, NTP, distributed timestamps

## 📚 Mini-Projects to Revisit

- **URL Shortener** — good intro project covering hashing, caching, databases
- **Design a High-Traffic System** — combine multiple concepts

---

**Current Status:** Webhooks & Message Queue patterns (transitioning to next topic soon)
