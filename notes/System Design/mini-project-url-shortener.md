# Mini Project: URL Shortener with Analytics

A URL shortener (like bit.ly) is the perfect learning project.
It's simple enough to build solo, but naturally forces you to use every major HLD component.

---

## What it does

- User submits a long URL → gets back a short URL (e.g. `short.ly/abc123`)
- Anyone visits the short URL → gets redirected to the original
- Every click is tracked → analytics (how many clicks, from where, when)

---

## Why this project?

It maps perfectly to real system design:
- **High read traffic** → needs caching
- **Simple data model** → good for DB practice
- **Click tracking** → perfect use case for async message queues
- **Multiple services** → can be load balanced
- **Static assets** → CDN opportunity

---

## Tech Stack

| Layer | Tool |
|---|---|
| REST API | Spring Boot (Java) |
| Database | PostgreSQL |
| Cache | Redis |
| Message Queue | RabbitMQ |
| Containerization | Docker + Docker Compose |
| Load Balancer | Nginx |

---

## Architecture (HLD)

```
User
 │
 ▼
Nginx (Load Balancer)
 │
 ├──► App Instance 1 (Spring Boot :8081)
 └──► App Instance 2 (Spring Boot :8082)
          │
          ├──► Redis (Cache) ◄── check short URL first
          │       │ miss
          ├──► PostgreSQL (DB) ◄── fetch + store URLs
          │
          └──► RabbitMQ (Queue) ◄── publish click event
                    │
                    ▼
              Analytics Consumer
              (logs click data to DB)
```

---

## Build Plan — Phase by Phase

### Phase 1 — Core API + Database
**Goal:** Get the basic feature working end-to-end.

- [ ] Create a Spring Boot project
- [ ] Connect to PostgreSQL
- [ ] Table: `url_mapping (id, short_code, original_url, created_at)`
- [ ] `POST /shorten` — accepts a long URL, returns a short code
- [ ] `GET /{shortCode}` — redirects to the original URL
- [ ] Use UUID or Base62 encoding to generate short codes

**Concepts touched:** REST API, SQL DB, Spring Data JPA

---

### Phase 2 — Caching with Redis
**Goal:** Make redirects blazing fast without hitting the DB every time.

- [ ] Spin up Redis with Docker
- [ ] On `GET /{shortCode}`:
  - Check Redis first
  - If found → return immediately (cache hit)
  - If not → query DB, then store result in Redis (cache miss)
- [ ] Set a TTL (e.g. 1 hour) on cached entries

**Concepts touched:** Caching, cache-aside pattern, TTL, Redis

---

### Phase 3 — Async Click Tracking with RabbitMQ
**Goal:** Track every click without slowing down the redirect.

- [ ] Spin up RabbitMQ with Docker
- [ ] On every redirect, publish a message to a queue: `{ shortCode, timestamp, userAgent }`
- [ ] Write a consumer that reads from the queue and saves click data to a `click_events` table
- [ ] `GET /analytics/{shortCode}` — returns total click count

**Why async?** The user should be redirected instantly. Saving analytics should not slow that down.

**Concepts touched:** Message queues, producer/consumer, async processing, decoupling

---

### Phase 4 — Docker Compose + Load Balancing with Nginx
**Goal:** Run the whole system locally like a real deployment.

- [ ] Write a `docker-compose.yml` that starts:
  - 2 instances of your Spring Boot app (ports 8081, 8082)
  - PostgreSQL
  - Redis
  - RabbitMQ
  - Nginx
- [ ] Write an `nginx.conf` that round-robins requests between the two app instances
- [ ] Verify both instances share the same DB and cache

**Concepts touched:** Horizontal scaling, load balancing, containerization, Docker networking

---

## Stretch Goals (Optional)

- [ ] **Rate limiting** — limit how many URLs a single IP can shorten per minute
- [ ] **Custom short codes** — let users pick their own alias
- [ ] **Expiry** — short URLs that expire after N days
- [ ] **Dashboard** — a simple HTML page showing analytics (touches CDN/static asset serving)

---

## Learning Checkpoints

After each phase, ask yourself:
- What happens if the cache goes down? (Phase 2)
- What happens if the queue goes down? Is any data lost? (Phase 3)
- What happens if one app instance crashes? (Phase 4)
- Where is the bottleneck in the current design?

These questions are exactly what interviewers ask in system design rounds.
