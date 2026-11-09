# Scalability Cheat Sheet

Goal: understand practical patterns to scale systems horizontally and vertically, and practice designing scalable services.

## Key Concepts

- Vertical scaling: increase resources (CPU/RAM) on a single machine. Easy but limited and single point of failure.
- Horizontal scaling: add more machines (stateless services scale naturally behind a load balancer).
- Load Balancer: distributes requests; supports health checks and session affinity if needed.
- Stateless vs Stateful:
  - Stateless services are easiest to scale (no per-server state).
  - Stateful services require sticky sessions, session stores, or sharding.
- Sharding (partitioning): split data across multiple nodes by key (range, hash, directory).
- Replication: copy data across nodes for availability and read scaling (master-slave, leader-follower).
- CAP trade-offs: consistency, availability, partition tolerance — choose based on requirements.
- Consistent hashing: useful for distributing keys across nodes with minimal reshuffling.
- Autoscaling: add/remove instances based on metrics (CPU, latency, request rate).
- Bottleneck identification: profiling, logs, and metrics (use A/B tests or canary deploys for changes).

## Patterns & Techniques

- Caching: CDN for static assets; in-memory caches (Redis, Memcached) for DB query results.
- Read replicas: separate read and write paths to scale reads.
- Queueing: decouple work with message queues to smooth spikes and perform background processing.
- Bulk/batch processing: group operations to reduce overhead.
- Backpressure & rate limiting: protect downstream systems under load.
- Database partitioning: horizontal (sharding) and vertical (separate tables by function).
- Circuit breakers & retries: protect services from cascading failures.

## Practical Exercises (1-hour each)

1. Design a scalable URL shortener: identify components, DB schema, sharding strategy, and caches.
2. Convert a single-node key-value store into a sharded design using consistent hashing.
3. Add caching and read replicas to a simple blog API and reason about cache invalidation.

## Quick Reading (30–60 mins each)

- “Designing Data-Intensive Applications” (Chapters on partitioning and consensus) — pick relevant excerpts.
- Articles on Consistent Hashing and Load Balancers (NGINX/HAProxy docs).
- Cloud provider docs on autoscaling groups (AWS Auto Scaling, Azure VM Scale Sets, GCP Instance Groups).

## Checklist for a Design Interview

- State your assumptions (traffic, data size, SLOs).
- Identify bottlenecks and single points of failure.
- Choose stateless vs stateful components and justify them.
- Propose sharding/replication strategies and discuss trade-offs.
- Explain caching layers and cache invalidation.
- Discuss monitoring, alerting, and scaling triggers.

---

If you want, I can:
- Expand any exercise into a step-by-step solution.
- Add diagrams (mermaid) for common architectures.
- Create flashcards for interview practice.
