# CAP Theorem

Goal: understand why you can't have all three of Consistency, Availability, and Partition Tolerance — and how to choose which two matter for your system.

## The Three Properties (In Simple Terms)

### Consistency (C)
- **All servers see the same data at the same time**
- Example: You transfer $100 from Account A to Account B. Every server immediately shows the new balances.
- If Server 1 shows A = $900, Server 2 must also show A = $900 (not $1000)

### Availability (A)
- **System is always up and responds to requests**
- Even if some servers go down, the system keeps working
- You can always get an answer (though it might be stale data)

### Partition Tolerance (P)
- **System survives network failures (partitions)**
- A partition = servers can't communicate with each other
- The system keeps running even when the network is broken

**What counts as a "partition" in real life:**
- A switch or router dies between two data centers
- A cable gets cut (yes, literally — undersea cables, backhoes digging up fiber, etc.)
- High latency/packet loss makes servers *think* the other side is down, even if it technically isn't
- A cloud provider has a networking blip between availability zones/regions
- Firewall misconfig blocks traffic between nodes

**Why "tolerance" is really about what happens *during* the split:**
- The cluster splits into two (or more) groups that can each still talk to clients, but not to each other
- Each side has to decide: keep answering requests (risking different sides drifting apart = inconsistency), or stop answering until the network heals (risking downtime)
- Partition tolerance itself just means "the system doesn't fall over/crash when this happens" — it doesn't say *how* it responds. That "how" is the actual C vs A choice.

**Why P isn't really optional:**
- Networks are unreliable by nature — cables fail, packets drop, DNS hiccups happen, cloud regions lose connectivity
- A system that isn't partition tolerant just stops working entirely the moment any network blip occurs — not acceptable for anything distributed across multiple machines
- So in practice: if your system has more than one node, you *will* face partitions eventually, and you must have a defined behavior for it (that's where CP vs AP comes in)

**Detecting a partition is itself hard:**
- A node can't always tell the difference between "the other node is down" and "the network link to it is down" — from its point of view, both look like "no response"
- This ambiguity is why distributed systems use things like heartbeats, timeouts, and quorum/consensus (e.g., Raft, Paxos) to make a best-guess decision about what's actually happening

## What Architects Actually Do to Handle Partitions

### 1. **Replicate Data Across Network Boundaries**
- Don't put all copies of data on the same network segment
- Spread replicas across data centers, regions, or at least different network switches
- **Why:** If a partition splits the network, at least one side has a copy of the data to continue serving from
- **Trade-off:** More replicas = higher latency for writes (have to sync to multiple places)

### 2. **Quorum-Based Decisions**
- When a partition happens, nodes vote/agree on what to do
- **Write quorum:** Only accept a write if *majority* of replicas acknowledge it
- **Read quorum:** Only read from replicas that have the latest version (determined by version numbers or timestamps)
- **Why:** Majority guarantees only one partition can claim to be "the real system" at a time
- **Example:** 5-node cluster splits 3-2. The 3-node side continues serving (has quorum). The 2-node side refuses writes (doesn't have quorum) → prevents two groups from diverging
- **Cost:** If network split is exactly even (2-2 in a 4-node cluster), neither side can get quorum → system becomes unavailable (depends on your timeout/leader logic)

### 3. **Asynchronous Replication (for AP systems)**
- Replicate writes to *other* copies in the background, not synchronously
- Client gets "write accepted" immediately, actual replication happens later
- **Why:** If a partition hits right after you write, your local copy has the data even if others don't
- **Cost:** If that node crashes before replicating, that data is lost
- **How inconsistency forms:** Different partitions may have different versions of the same key

### 4. **Consistent Hashing + Ring-Based Storage**
- Spread key-space around a "ring" of nodes (e.g., DynamoDB, Cassandra)
- Each key "lives" on several consecutive nodes (N replicas)
- When a partition happens, each node still "knows" which keys it owns and serves them
- **Why:** No central coordination needed — each partition can independently decide which keys to serve
- **Cost:** After healing, replicas might have diverged; need to sync/reconcile

### 5. **Conflict-Free Replicated Data Types (CRDTs)**
- Use data structures (sets, counters, maps) designed so that any two versions can be merged without a "master"
- Example: Counter incremented by both sides of a partition → merge by taking the max value
- **Why:** When partition heals, conflicting updates can auto-merge without choosing one side as "right"
- **Cost:** Only works for specific data types, not general key-value stores; complex to get right

### 6. **Vector Clocks / Version Vectors**
- Tag each write with metadata showing which nodes have seen it
- After partition heals, use this to detect conflicting writes and decide how to merge
- **Why:** Lets system identify "which write came first" vs "these are actually conflicting and from different sides of the split"
- **Cost:** Adds metadata overhead; requires custom merge logic

### 7. **Hinted Handoff (temporary buffering)**
- When a node can't reach another node, buffer the update locally
- Once network heals, "hand off" buffered updates
- **Why:** Reduces data loss during partitions
- **Example:** DynamoDB uses this — node A writes data for node B's key range, buffers it, sends it when B comes back
- **Cost:** Can temporarily increase local disk usage during large partitions

### 8. **Timeouts and Failure Detection**
- Use heartbeats: "Are you alive? Respond every 100ms"
- If no heartbeat for 3 seconds, assume partition (don't wait forever)
- **Why:** Without this, system hangs indefinitely waiting for a node that's actually cut off
- **Cost:** Tuning is hard — too aggressive and temporary network jitter causes false failures; too lenient and real failures take too long to detect

### 9. **Graceful Degradation / Circuit Breaker**
- If you can't reach other partitions, still answer requests with *what you have*
- Don't error out immediately; instead serve stale data or limited functionality
- **Why:** Maintains availability even during partition
- **Example:** Social media feed serves cached posts if fresh data can't be fetched
- **Cost:** Users might see inconsistent/old data

### 10. **Leader Election via Consensus (Raft, Paxos)**
- Use an algorithm where one "leader" makes decisions for a partition
- Only the partition with the majority of nodes elects a leader
- Minority partitions refuse to serve (or serve read-only)
- **Why:** Prevents two sides from both thinking they're in charge and making conflicting decisions
- **Cost:** Complex to implement, adds latency to decision-making

## Real Example: How MongoDB Handles a Partition
1. **Replica set** of 3 nodes (A, B, C) across two data centers
2. A and B are in DC1, C is in DC2
3. Network link between DC1 and DC2 fails
4. A and B still talk to each other → they have quorum (2 out of 3) → **DC1 side keeps serving and accepting writes**
5. C is alone → no quorum → **DC2 side becomes read-only** (won't accept new writes)
6. Client writes go to DC1 side only
7. Network heals
8. C catches up by replaying writes from A/B → **eventual consistency achieved**
9. No data loss because writes only went to the side with quorum

## The Trade-off: Pick Two (Usually)

**You MUST have P** (partition tolerance). In real distributed systems, network failures happen — you can't avoid them.

So really, you choose between **C** and **A** when a partition happens:

| Choice | When Network Breaks | Example |
|--------|---|---|
| **CP** (Consistency + Partition) | Refuse requests to stay consistent | Traditional SQL databases with strong consistency; stops serving to avoid giving stale data |
| **AP** (Availability + Partition) | Keep serving, accept stale data | NoSQL like DynamoDB; always responds even if data is outdated |

## Interview Frame: "When Partition Happens"

Interviewer: *"Database A and Database B lose network connection. What happens?"*

**If you picked CP:**
- System says "I don't know if my copy is the latest" → refuses requests or blocks
- Users see "Service Unavailable" error
- **Pro:** No inconsistent data. **Con:** Users can't use the app.

**If you picked AP:**
- System says "Here's what I have" (might be stale)
- Users can still use the app
- **Pro:** App keeps working. **Con:** Data might be old or inconsistent temporarily.

## Real-World Examples

### CP Systems (Consistency matters more)
- **Banking transactions** — can't risk showing wrong balance
- **Ticketing systems** — can't oversell tickets (must refuse if unsure)
- **SQL databases** (PostgreSQL, MySQL with primary-replica setup)

### AP Systems (Availability matters more)
- **Social media feeds** — if you see an old post, not the end of the world
- **Stock price quotes** — 1-minute-old data is fine
- **NoSQL** (DynamoDB, Cassandra, MongoDB)
- **DNS** — always responds, might be outdated

## How They Resolve Inconsistency

After the network is fixed, inconsistent data is resolved through:
- **Read repair** — when you query, fix stale copies
- **Hinted handoff** — temporary backup servers pass data back
- **Anti-entropy** — background process syncs all copies
- **Eventual consistency** — system guarantees data will eventually match

## Interview Questions You Might Get

1. *"Design a banking system. Which do you pick?"* → **CP** (consistency critical, small downtime acceptable)
2. *"Design a social media feed?"* → **AP** (always need to show something, eventual consistency is fine)
3. *"A network partition happens. What does your system do?"* → Depends on CP vs AP choice
4. *"How do you handle stale data?"* → Explain eventual consistency, read repair, etc.

## Key Takeaway

- **P is non-negotiable** — partitions happen in real systems
- **C vs A is a business decision** — what hurts more: downtime or wrong data?
- **Most modern systems are AP** — because users hate "Service Unavailable" more than slightly stale data
- **But some systems MUST be CP** — financial, critical operations where wrongness is unacceptable
