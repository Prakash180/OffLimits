# SQL vs NoSQL

Goal: know the difference, and pick the right database for a given problem.

## Quick Definitions

- **SQL (relational)**: data lives in **tables** (rows + columns) with a fixed **schema**. Tables are linked via keys. You query using SQL.
  - Examples: PostgreSQL, MySQL, Oracle, SQL Server.
- **NoSQL ("not only SQL")**: a family of databases that store data in **non-tabular** shapes, usually with a flexible schema and built to scale across many machines.
  - Examples: MongoDB, DynamoDB, Cassandra, Redis, Neo4j.

## Core Differences

| Aspect | SQL | NoSQL |
|--------|-----|-------|
| Data model | Tables, rows, columns | Documents / key-value / wide-column / graph |
| Schema | Fixed, defined upfront | Flexible, can change per record |
| Relationships | Joins across tables | Usually embed data or handle in app code |
| Query language | Standard SQL | Varies per database (own API/query) |
| Transactions | Full **ACID** | Often limited; many are **BASE** (eventual consistency) |
| Scaling | Mainly **vertical** (bigger machine); horizontal is harder | Built for **horizontal** (add more machines) |
| Consistency | Strong | Tunable, often eventual (see [cap-theorem.md](cap-theorem.md)) |
| Best at | Complex queries, data integrity | Huge scale, speed, flexible data |

## ACID vs BASE

**ACID** (SQL):
- **A**tomicity: all steps of a transaction succeed, or none do.
- **C**onsistency: data always follows the rules (constraints, keys).
- **I**solation: parallel transactions don't mess each other up.
- **D**urability: once committed, it survives a crash.

**BASE** (many NoSQL):
- **B**asically **A**vailable: system keeps answering, even during failures.
- **S**oft state: data may change over time as replicas sync.
- **E**ventual consistency: replicas agree *eventually*, not instantly.

## The 4 Types of NoSQL

| Type | How data looks | Examples | Good for |
|------|----------------|----------|----------|
| Key-Value | `key -> blob` | Redis, DynamoDB, Riak | Caching, sessions, carts (see [key-value-db-dynamo.md](key-value-db-dynamo.md)) |
| Document | JSON-like documents | MongoDB, Couchbase | Catalogs, user profiles, CMS |
| Wide-Column | Rows with dynamic columns, grouped in families | Cassandra, HBase | Time series, logs, huge write volume |
| Graph | Nodes + edges | Neo4j, Amazon Neptune | Social networks, recommendations, fraud detection |

## Same Data, Two Ways

An order with items.

**SQL** - split into tables, linked by keys:

```sql
orders(id, user_id, total)
order_items(id, order_id, product, qty)

SELECT o.id, i.product, i.qty
FROM orders o JOIN order_items i ON i.order_id = o.id
WHERE o.id = 42;
```

**NoSQL (document)** - one self-contained document:

```json
{
  "_id": 42,
  "userId": 7,
  "total": 59.98,
  "items": [
    { "product": "Pen", "qty": 2 },
    { "product": "Book", "qty": 1 }
  ]
}
```

- SQL: avoids duplicated data, easy to query any angle.
- NoSQL: one read gets everything, but data may be duplicated.

## When to Use SQL

- Data is **structured** and relationships matter (users -> orders -> payments).
- You need **strong consistency and transactions** (money, inventory, bookings).
- You need **complex queries**: joins, aggregations, reports, ad-hoc analytics.
- Schema is **stable** and well understood.
- Data integrity is critical (foreign keys, constraints, unique rules).
- Scale is moderate, or a single (or primary + read replicas) setup is enough.

Typical use cases: banking, e-commerce orders, ERP/CRM, booking systems, HR/payroll, anything with accounting.

## When to Use NoSQL

- You need **massive scale** and high write throughput (millions of ops/sec).
- You need **horizontal scaling** and high availability across regions.
- Data is **unstructured / semi-structured** or changes shape often.
- Access is mostly **by key** or by a few known patterns (no heavy joins).
- **Low latency** matters more than instant consistency.
- Data is naturally a graph, time series, or a cache.

Typical use cases: session stores, shopping carts, product catalogs, IoT/sensor data, activity feeds, chat messages, leaderboards, recommendation graphs, caching.

## Quick Decision Guide

| Question | Lean towards |
|----------|--------------|
| Need multi-row transactions (e.g., transfer money)? | SQL |
| Lots of joins and reporting? | SQL |
| Schema changes constantly? | NoSQL (document) |
| Need to handle huge traffic and spread over many nodes? | NoSQL |
| Only look up by ID / key, need very low latency? | NoSQL (key-value) |
| Data is highly connected (friends of friends)? | NoSQL (graph) |
| Write-heavy time series / logs? | NoSQL (wide-column) |
| Not sure, small/medium app? | **SQL** (safe default) |

## Pros and Cons

**SQL**
- Pros: mature, standard language, strong integrity, great for complex queries, huge tooling ecosystem.
- Cons: rigid schema, schema migrations can be painful, harder to scale writes horizontally.

**NoSQL**
- Pros: flexible schema, easy horizontal scale, high availability, very fast for known access patterns.
- Cons: weaker joins and transactions, eventual consistency surprises, data duplication, query patterns must be designed upfront.

## Scaling Differences

- **SQL**: scale up (bigger server), add **read replicas**, then **shard** manually (hard, loses easy joins).
- **NoSQL**: scale out by default using partitioning (see [consistent-hashing.md](consistent-hashing.md)) and replication.

## Common Myths

- "NoSQL is always faster" - only for the access patterns it was designed for.
- "SQL can't scale" - it can (Postgres/MySQL with replicas, sharding, or NewSQL like CockroachDB, Spanner), just with more effort.
- "NoSQL has no schema" - the schema just moves into your application code.
- "NoSQL has no transactions" - many now do (MongoDB, DynamoDB transactions), but with limits.

## Polyglot Persistence (Use Both)

Real systems often mix databases, each for what it's best at:

- **SQL** -> orders, payments, user accounts (source of truth).
- **Redis** -> cache, sessions, rate limiting.
- **Elasticsearch** -> full-text search.
- **Cassandra / DynamoDB** -> high-volume events or feeds.
- **Neo4j** -> recommendations / relationships.

This fits well with microservices: each service picks the database that suits it (see [microservices.md](microservices.md)).

## Interview Cheat Line

> "Start with SQL for structured, relational, transactional data. Pick NoSQL when I need huge scale, flexible schema, or very low latency on simple access patterns. Often use both."

## One-Minute Revision

1. **SQL** = tables, fixed schema, joins, **ACID**, strong consistency, scales up first.
2. **NoSQL** = flexible models (key-value, document, wide-column, graph), **BASE**, scales out easily.
3. Need **transactions + complex queries** -> SQL.
4. Need **massive scale + simple access by key + flexibility** -> NoSQL.
5. Unsure? Default to **SQL**.
6. Big systems use **both** (polyglot persistence).

## Practical Exercise

- In `SideProject`, model a "user + orders" example twice: once as two related tables (plain Java classes mimicking SQL rows with an ID link), and once as a single nested object (document style). Compare how you fetch "all orders of user 7" in each.
