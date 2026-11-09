# HLD — High-Level Design

## What is HLD?

HLD is the **big picture** of how a system works.

- You define **what components** exist and **how they talk to each other**.
- You don't go into code details — just boxes and arrows.
- Think of it as a blueprint before you start building.

---

## Why is HLD important?

- Helps everyone (devs, managers, stakeholders) understand the system at a glance.
- Catches major design problems early — before writing a single line of code.
- Used in system design interviews to show you can think at scale.

---

## What does a typical HLD include?

| Component | What it means |
|---|---|
| **Client** | The user's browser/app that sends requests |
| **Load Balancer** | Distributes traffic across servers evenly |
| **Web/App Servers** | Handle business logic |
| **Database** | Stores data (SQL or NoSQL) |
| **Cache** | Stores frequently-used data in memory for speed |
| **Message Queue** | Decouples services; lets them talk asynchronously |
| **CDN** | Serves static files (images, JS) from locations near the user |
| **Storage** | Stores files/blobs (e.g., S3 for images/videos) |

---

## How to approach an HLD in an interview

1. **Clarify requirements** — What are we building? Who uses it? How much traffic?
2. **Define scope** — Which features are in/out?
3. **Estimate scale** — Users, requests per second, data size.
4. **Draw the high-level diagram** — Client → Load Balancer → Servers → DB
5. **Pick the right components** — SQL vs NoSQL, cache strategy, sync vs async.
6. **Identify bottlenecks** — Where will the system break under load?
7. **Suggest improvements** — Sharding, replication, CDN, etc.

---

## Key concepts to know for HLD

### Scalability
- **Vertical scaling** — Give the same machine more CPU/RAM. Has limits.
- **Horizontal scaling** — Add more machines. Preferred for large systems.

### Availability vs Consistency (CAP Theorem)
- A distributed system can only guarantee **two** of three: Consistency, Availability, Partition Tolerance.
- In practice, partition tolerance is a must → you choose between **C** and **A**.
- Example: Banking apps need **Consistency**. Social media feeds prefer **Availability**.

### SQL vs NoSQL
| | SQL | NoSQL |
|---|---|---|
| Structure | Tables with fixed schema | Flexible (JSON, key-value, etc.) |
| Best for | Relational data, transactions | Large scale, unstructured data |
| Example | PostgreSQL, MySQL | MongoDB, Cassandra, Redis |

### Caching
- Store results of expensive operations in fast memory (RAM).
- Tools: **Redis**, **Memcached**
- Strategy: Cache frequently read, rarely changed data.

### Load Balancing
- Distributes incoming requests across multiple servers.
- Prevents one server from being overwhelmed.
- Algorithms: Round Robin, Least Connections, IP Hash.

### Message Queues
- Let services communicate without waiting for each other (async).
- Tools: **Kafka**, **RabbitMQ**, **SQS**
- Use case: Sending emails, processing orders in the background.

### CDN (Content Delivery Network)
- Copies static content (images, videos, JS) to servers around the world.
- Users get files from the nearest server → faster load times.
- Example: Cloudflare, AWS CloudFront.

---

## Simple example: Design a URL Shortener (like bit.ly)

```
User → Load Balancer → App Server → Cache (check short URL)
                                   ↓ (miss)
                                  DB (lookup/store URL mapping)
```

- Short URL created → stored in DB + cached in Redis.
- Next time same short URL is hit → served from cache, skips DB.

---

## HLD vs LLD

| | HLD | LLD |
|---|---|---|
| Focus | System architecture | Code-level design |
| Shows | Components and their interactions | Classes, methods, DB schema |
| Audience | Everyone | Developers |
| Detail | Low | High |
