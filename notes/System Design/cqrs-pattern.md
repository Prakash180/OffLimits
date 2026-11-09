# CQRS Pattern

## The Problem: Reads and Writes Have Different Needs

A typical REST API does both:
- **Writes:** Create/update/delete (complex logic, strong consistency, slow)
- **Reads:** Query (simple, need speed, can tolerate stale data)

Forcing both through the same database is inefficient:

```
POST /users          → Complex logic, database lock, slow write ← 100ms
GET /users?city=NYC  → Simple query, needs speed ← But still waits behind writes!
```

**The conflict:**
- Writes need **strong consistency** (ACID locks)
- Reads need **speed** (eventual consistency is fine)
- One database can't be great at both

## The Solution: CQRS (Command Query Responsibility Segregation)

Separate read and write models:
- **Command (Write):** Store authoritative data in a normalized database
- **Query (Read):** Replicate to optimized read-only databases

```
Write Model (Authoritative):
  POST /users
    ↓
  User Service normalizes data
    ↓
  Writes to User DB (PostgreSQL, ACID)
    ↓
  Publishes "UserCreated" event

Read Models (Optimized):
  "UserCreated" event → Event Handler
    ↓
  Updates Read Database 1 (Elasticsearch for search)
  Updates Read Database 2 (Redis cache for profile page)
  Updates Read Database 3 (MongoDB for analytics)

Query (Read):
  GET /users?city=NYC
    ↓
  Queries Elasticsearch (super fast)
    ↓
  Returns results instantly
```

## Example: User Profile Service

### Old Way (Single Model)
```
Database (PostgreSQL):
┌──────────────────────────┐
│ users table              │
├──────────────────────────┤
│ id: 1                    │
│ name: "Alice"            │
│ email: "alice@..."       │
│ city: "NYC"              │
│ created_at: 2024-01-01   │
│ updated_at: 2024-10-10   │
│ ... 50 more fields ...   │
└──────────────────────────┘

API:
  POST /users → writes all fields, slow
  GET /users?city=NYC → filters through all 50 fields, slow
```

### CQRS Way (Separate Models)
```
Write Model (User Service):
┌──────────────────────────┐
│ PostgreSQL (Authoritative)
├──────────────────────────┤
│ users table (normalized) │
│ Complete user record     │
│ ACID protected          │
└──────────────────────────┘
        ↓ (publishes event)

Read Models (Optimized for different queries):

Model 1: Elasticsearch (City Search)
┌──────────────────────────┐
│ Indexed documents       │
├──────────────────────────┤
│ {id:1, name:"Alice", city:"NYC"} │
│ (only fields needed for search)   │
│ Super fast full-text search       │
└──────────────────────────┘

Model 2: Redis (Profile Cache)
┌──────────────────────────┐
│ key: "user:1"          │
│ value: {name, email, city} │
│ (pre-rendered JSON)    │
│ 1ms response           │
└──────────────────────────┘

Model 3: MongoDB (Analytics)
┌──────────────────────────┐
│ Denormalized user data  │
│ + activity history      │
│ + computed stats        │
└──────────────────────────┘

API:
  POST /users → writes to PostgreSQL only (100ms, ACID)
  GET /users?city=NYC → reads from Elasticsearch (5ms, eventual consistency)
  GET /users/{id}/profile → reads from Redis (1ms)
  GET /analytics/user/{id} → reads from MongoDB
```

## How CQRS Works: Step by Step

### 1. Write (Command)
```
POST /users {name: "Bob", email: "bob@..."}
  ↓
User Service (Write Model)
  ↓
Validate input
  ↓
Write to PostgreSQL (authoritative source)
  ↓
Return ID: 123 to client
  ↓
Publish Event: "UserCreated(id=123, name='Bob', email='bob@...')"
```

### 2. Event Propagation
```
Event "UserCreated" published to message broker (Kafka, RabbitMQ)
  ↓
Multiple subscribers (async):
  ├─ Elasticsearch Indexer: adds user to search index
  ├─ Cache Warmer: stores in Redis for quick profile lookup
  ├─ Analytics: stores in MongoDB for analysis
  └─ Notification: sends welcome email
```

### 3. Read (Query)
```
GET /users?city=NYC
  ↓
Query Reader (NOT the authoritative database)
  ↓
Query Elasticsearch: "Find all users with city='NYC'"
  ↓
Return: [{id:1, name:"Alice"}, {id:5, name:"Charlie"}]
  ↓
Response time: 5ms (cached, indexed, optimized)
```

## Key Characteristics

### Write Model
- **Authoritative:** Source of truth
- **Normalized:** No redundancy (3NF database design)
- **ACID compliant:** Strong consistency
- **Smaller:** Only core data
- **Slow:** But safe

### Read Models
- **Denormalized:** Optimized for queries
- **Eventual consistency:** Might be 1-5 seconds behind
- **Specialized:** Each model for different access pattern
- **Fast:** Milliseconds
- **Redundant:** OK to duplicate data

## Real-World Examples

### Example 1: E-Commerce (Product Catalog)

**Write Model:**
```
PostgreSQL: products table
- id, name, price, inventory_count, description, ...
```

**Read Models:**
```
Elasticsearch: product search index
  ├─ id, name, price (for searching)
  ├─ Full-text indexed
  └─ Updated async

Redis: hot products cache
  ├─ top 100 bestsellers
  ├─ Updated nightly
  └─ 1ms response

MySQL data warehouse: analytics
  ├─ product sales over time
  ├─ customer demographics
  └─ trends
```

### Example 2: Social Media (Feed)

**Write Model:**
```
PostgreSQL: posts table
- id, user_id, content, created_at, ...
```

**Read Models:**
```
Elasticsearch: post search
  └─ full-text search across all posts

Redis: user timelines
  ├─ cached feed for "Alice's timeline" = [post1, post2, ...]
  ├─ updated when Alice posts or new posts from followers

DynamoDB: sorted by recency
  └─ fast lookup of "posts from last 24 hours"
```

## Benefits

✅ **Read Performance:** Queries can be super fast (no joins, indexed, cached)
✅ **Write Safety:** Authoritative model stays ACID
✅ **Scalability:** Scale reads and writes independently
✅ **Flexibility:** Add new read models without changing writes
✅ **Tech Stack:** Writes in PostgreSQL, reads in Elasticsearch + Redis + MongoDB

## Challenges

❌ **Eventual Consistency:** Read models lag behind writes (usually fine, 1-5 sec delay)
❌ **Complexity:** More databases to operate, more code
❌ **Sync Issues:** If event handling fails, read model goes stale (need monitoring)
❌ **Debugging:** Bug in Elasticsearch indexer → "Why is this user not in search?"
❌ **Deployment:** Updating read models is risky (can't just revert database schema)

## When to Use CQRS

**Good fit:**
- Read-heavy systems (search engines, dashboards, feeds)
- Complex queries (aggregations, filtering, sorting)
- Different teams own reads vs writes
- Reads need to be super fast
- Need to scale reads and writes independently

**Overkill:**
- Simple CRUD app (blog with 100 posts)
- Writes = reads (ledger/audit log)
- Team is small (don't need to separate teams)
- Consistency more important than speed (financial transactions)

**Start simple, add CQRS only if needed:** Most apps start as monolith, add CQRS later when they have read performance problems.

## Example Implementation (Node.js)

```javascript
// WRITE: Command handler
app.post('/users', async (req, res) => {
  const user = { id: uuid(), ...req.body };
  
  // Write to authoritative database
  await postgres.query('INSERT INTO users VALUES (?)', [user]);
  
  // Publish event
  await messageQueue.publish('user.created', user);
  
  res.json(user);
});

// READ: Query handler
app.get('/users', async (req, res) => {
  // Read from optimized database
  const users = await elasticsearch.search({
    index: 'users',
    query: { match: { city: req.query.city } }
  });
  
  res.json(users);
});

// EVENT HANDLER: Update read model
messageQueue.subscribe('user.created', async (user) => {
  // Update Elasticsearch
  await elasticsearch.index({
    index: 'users',
    id: user.id,
    body: { id: user.id, name: user.name, city: user.city }
  });
  
  // Update Redis
  await redis.set(`user:${user.id}`, JSON.stringify(user));
});
```

## Interview Frame

**Q: Why would you use CQRS?**
A: To separate read and write optimization. Writes use ACID (slow but safe), reads use denormalized data structures (fast but eventually consistent).

**Q: What if a read model gets out of sync?**
A: Publish a "rebuild" event that replays all events through that read model. Or rebuild it from the authoritative database at midnight.

**Q: Isn't this just denormalization?**
A: Yes, but intentional and structured. CQRS makes denormalization explicit and manages it via events.

**Q: When should I NOT use CQRS?**
A: Simple systems where consistency matters more than speed. Also, small teams where the overhead isn't justified.

**Q: Choreography vs Orchestration for syncing read models?**
A: Choreography works (event → Elasticsearch indexer, Elasticsearch indexer updates index). No orchestration needed; let each read model subscriber decide how to react.
