# Consistent Hashing

Goal: understand why plain `hash % N` breaks when servers are added/removed, and how consistent hashing fixes it.

## The Problem (Plain Hashing)

- Simple approach: `server = hash(key) % N` (N = number of servers).
- Works fine... until N changes (server added/removed/crashes).
- Since `N` changed, almost **every key** now maps to a different server.
- Result: massive cache misses, huge data reshuffling, unhappy downstream DBs.

## The Idea: A Hash Ring

- Draw a circle representing hash values `0` → `2^32 - 1` (then it wraps back to 0).
- Hash both **servers** and **keys** onto this same ring (using the same hash function).
- Rule: a key belongs to the **first server you hit going clockwise** from the key's position.
- Adding/removing a server only affects the keys in the arc next to it — everything else stays exactly where it was.
- Rough rule of thumb: only about `K/N` keys move (K = total keys, N = servers), instead of almost all of them.

```
        server-A
       /         \
  keyX             server-B
       \         /
        server-C
```
(Key X walks clockwise until it hits the next server on the ring.)

## Virtual Nodes (important refinement)

- Problem: with only 1 point per server on the ring, the ring is unbalanced — one server might cover a huge arc, another a tiny sliver.
- Fix: hash each **physical server multiple times** with different suffixes:
  - `server-A#1`, `server-A#2`, ... `server-A#150`
- Now each physical server owns many small, scattered arcs → much more even load distribution.
- Bonus: when a server dies, its load spreads across many other servers instead of dumping it all on one neighbor.

## Why It's Better

| Plain `hash % N`                        | Consistent Hashing                     |
|------------------------------------------|-----------------------------------------|
| Adding/removing a node remaps ~all keys  | Remaps only ~`K/N` keys                 |
| Bad for caches (mass cache miss storm)   | Cache-friendly, minimal disruption      |
| Uneven load needs manual tuning          | Virtual nodes even things out automatically |

## Real-World Uses

- Distributed caches: Memcached client-side hashing
- Databases: DynamoDB, Cassandra (partitioning across nodes)
- Redis Cluster (uses a related idea: fixed hash slots, not a literal ring)
- Load balancers / CDNs: routing requests to backend nodes or edge caches consistently
- Cluster sharding in distributed systems (e.g., Akka Cluster Sharding)

## Simple Mental Walkthrough

1. You have servers A, B, C hashed onto the ring at positions 10, 50, 90.
2. Key `"user:42"` hashes to position 35 → goes clockwise → lands on server B (50).
3. Server B crashes → ring removes position 50 → key `"user:42"` now goes to C (90).
4. Only keys that were routed to B need to move. Keys pointed at A or C never notice anything changed.

## Practical Exercise

- Implement a simple consistent hash ring in Python or Java:
  1. Hash N servers (with ~100-150 virtual nodes each) onto a sorted ring (e.g., a `TreeMap`/`SortedDict` of hash → server).
  2. Implement `get_server(key)`: hash the key, find the next server clockwise (ceiling lookup, wrap around to smallest if none found).
  3. Add/remove a server and verify only a small fraction of test keys change their assigned server.
- Compare against plain `hash % N` on the same key set to see the difference in how many keys move.

## Related Notes

- [scalability-cheatsheet.md](scalability-cheatsheet.md) — broader scaling patterns (sharding, replication, caching).
