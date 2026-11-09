Value DB (DynamoDB-style)

Goal: understand how a distributed key-value store (Dynamo paper / DynamoDB / Cassandra / Riak) stays fast, always on, and spread across many machines.

## What Is a Key-Value DB?

- Like a giant hash map: `put(key, value)` and `get(key)`.
- Value is opaque (a blob, JSON, etc.) — DB doesn't care what's inside.
- No joins, no complex queries → very fast and easy to scale.
- Examples: DynamoDB, Redis, Riak, Cassandra (wide-column, but same ideas), etcd (strongly consistent variant).

## The 3 Goals

| Goal | Plain meaning |
|------|---------------|
| Scalability | Add more machines → handle more data/traffic |
| Decentralization | No boss node; every node is equal (no single point of failure) |
| Eventual Consistency | Replicas may differ briefly, but they all agree **eventually** (favours availability over instant consistency — see [cap-theorem.md](cap-theorem.md)) |

## How the Goals Are Achieved

| Technique | Solves |
|-----------|--------|
| Partitioning (consistent hashing) | Scalability |
| Replication | Availability + durability |
| Get/Put with quorum | Tunable consistency |
| Data versioning (vector clocks) | Conflicting writes |
| Gossip protocol | Decentralized failure detection |
| Merkle tree | Fast replica repair |
| Hinted handoff, sloppy quorum | Temporary node failures |

---

## 1. Partitioning (Scalability)

- Data too big for one machine → split it across many.
- Use **consistent hashing** (see [consistent-hashing.md](consistent-hashing.md)):
  - Nodes and keys placed on a hash ring.
  - Key goes to the first node clockwise.
- **Virtual nodes**: each physical machine owns many small spots on the ring → even load, and bigger machines can own more vnodes.
- Adding/removing a node moves only a small slice of keys.

## 2. Replication (Availability + Durability)

- Keep **N copies** of each key (commonly N = 3).
- Coordinator node (owner of the key) copies data to the next N-1 **distinct physical** nodes clockwise on the ring.
- Those N nodes are called the key's **preference list**.
- Spread replicas across different racks / data centers so one failure doesn't kill all copies.

## 3. Get / Put with Quorum

Three knobs:
- `N` = number of replicas
- `W` = nodes that must acknowledge a **write**
- `R` = nodes that must respond to a **read**

Rule: **`R + W > N`** → read and write sets overlap → you read at least one fresh copy (strong-ish consistency).

| Config (N=3) | Behaviour |
|--------------|-----------|
| `W=1, R=1` | Fastest, but may read stale data |
| `W=2, R=2` | Balanced (the usual choice) |
| `W=3, R=1` | Fast reads, slow/fragile writes |
| `W=1, R=3` | Fast writes, slow reads |

Flow:
- **Put**: client → coordinator → writes to N replicas → returns success once `W` ack.
- **Get**: client → coordinator → asks N replicas → waits for `R` replies → returns the newest value (or all conflicting versions if they can't be reconciled).

## 4. Data Versioning (Conflict Handling)

- Because replicas can accept writes independently, two nodes may update the same key at the same time → **conflict**.
- **Vector clock**: a list of `(node, counter)` pairs attached to each value.
  - Example: `[(A,2), (B,1)]`
- Comparing clocks:
  - Every counter in X ≤ Y → X is an **ancestor** of Y → safe to discard X.
  - Neither dominates → **conflict** → keep both versions and reconcile.
- Reconcile by:
  - Client merges (e.g., shopping cart = union of items — Dynamo's classic example).
  - **Last Write Wins (LWW)** using timestamps: simple but may silently lose data.
- Downside: vector clocks can grow big → truncate oldest entries.

## 5. Gossip Protocol (Decentralized Membership & Failure Detection)

- No central server tracking who is alive.
- Every second or so, each node picks a few random peers and shares what it knows: "who's alive, who's dead, heartbeat counters."
- Information spreads like a rumour → whole cluster knows within a few rounds (`~log N`).
- Each node keeps a table: `node → heartbeat counter, last updated`.
- If a node's heartbeat hasn't increased for a while → marked **down**.
- Pros: no single point of failure, scales well. Cons: info is slightly delayed.

## 6. Merkle Tree (Anti-Entropy / Replica Repair)

- Problem: replicas drift apart. Comparing every key between two nodes is too expensive.
- A **Merkle tree** = tree of hashes:
  - Leaves = hash of a small group of keys.
  - Parent = hash of its children's hashes.
  - Root = fingerprint of the entire dataset.
- Compare two replicas:
  1. Compare root hashes. Same → done.
  2. Different → compare children, go down only the mismatching branch.
  3. Sync only the few differing key ranges.
- Cost: tiny data transfer, and a replica needs to compare only `O(log n)` hashes to find the difference.
- Each node builds a tree per key range it owns.

```
          Root(H12 + H34)
          /            \
     H12(H1+H2)      H34(H3+H4)
      /     \          /     \
    H1      H2       H3      H4   <- hashes of key groups
```

---

## Topics You Might Have Missed

### Handling Failures
- **Sloppy quorum**: if a preference-list node is down, use the next healthy node on the ring instead of failing the write → keeps the DB always writable.
- **Hinted handoff**: the stand-in node stores the data with a "hint" (intended owner). When the real node returns, the data is handed back.
- **Anti-entropy** (via Merkle trees): background repair for permanent failures.
- **Read repair**: during a `get`, if a replica returns stale data, the coordinator quietly updates it.
- **Permanent vs temporary failure**: temporary → hinted handoff; permanent → Merkle tree sync + replace node.

### Write Path (LSM-tree based stores, e.g., Cassandra)
1. Write to **commit log** (disk, append-only) → durability.
2. Write to **memtable** (in-memory sorted map).
3. When memtable is full → flush to an immutable **SSTable** on disk.
4. Background **compaction** merges SSTables, drops old versions and deleted keys.

### Read Path
1. Check memtable.
2. Check **Bloom filter** per SSTable ("is the key definitely NOT here?") → skips most disk reads.
3. Read matching SSTables, merge results, return the newest version.

### Deletes
- Can't just erase: other replicas might bring the key back.
- Use a **tombstone** (a "deleted" marker) kept for a while, then removed during compaction.

### Other Useful Concepts
- **Coordinator node**: any node can receive the request; it routes to the right replicas (client-side routing is also possible).
- **TTL (time-to-live)**: key auto-expires after N seconds (used for caches, sessions).
- **Secondary indexes**: key-value DBs only look up by key; DynamoDB adds **GSI/LSI** to query by other attributes.
- **Partition key vs sort key** (DynamoDB): partition key picks the node; sort key orders items inside that partition.
- **Hot partition**: one key gets too much traffic → pick high-cardinality partition keys.
- **Conditional writes / compare-and-set**: write only if the version still matches → prevents lost updates.
- **Consistency options** (DynamoDB): eventually consistent read (default, cheaper) vs strongly consistent read.
- **Idempotency**: retrying a `put` should be safe.
- **Rebalancing**: moving partitions when nodes join/leave.
- **Multi-region replication** (DynamoDB Global Tables): conflicts resolved by LWW.
- **CAP / PACELC**: Dynamo = AP (stays available, eventually consistent). PACELC adds: even with no partition, you trade **L**atency vs **C**onsistency.
- **Caching layer**: DAX / Redis in front of the DB for microsecond reads.
- **Security & Ops**: encryption at rest/in transit, backups, point-in-time recovery, monitoring.

## Quick Comparison: Dynamo-style vs Others

| Store | Style | Consistency |
|-------|-------|-------------|
| Dynamo / Cassandra / Riak | Leaderless, ring | Eventual (tunable) |
| Redis (single) | In-memory, leader-follower | Strong on leader |
| etcd / Zookeeper | Consensus (Raft/Paxos) | Strong |

## One-Minute Revision

1. **Partition** with consistent hashing + vnodes → scale.
2. **Replicate** to N nodes → survive failures.
3. **Quorum** `R + W > N` → tune consistency vs speed.
4. **Vector clocks** → detect conflicting writes.
5. **Gossip** → know who is alive without a master.
6. **Hinted handoff + sloppy quorum** → survive temporary failures.
7. **Merkle trees + read repair** → fix drifted replicas.
8. **Commit log → memtable → SSTable (+ Bloom filter, tombstones, compaction)** → storage engine.

## Practical Exercise

- Build a tiny in-memory ring in `SideProject`: 3 nodes, N=3 replication, `put`/`get` with W=2/R=2, and simulate one node being down.
