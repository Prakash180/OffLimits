# Strangler Pattern

## The Problem: You Can't Rewrite Everything at Once

You have a massive monolith that works but is painful to maintain. You want to break it into microservices.

**Bad idea:** "Let's rewrite the whole thing as microservices" → high risk, takes months, everything breaks, expensive.

**Good idea:** "Let's incrementally migrate piece by piece" → lower risk, quick wins, parallel running, fail safely.

## The Solution: Gradually Replace the Monolith

The "Strangler Pattern" means:
1. Build a new service alongside the monolith
2. Gradually route traffic from monolith to new service
3. Old code "dies" as new service takes over (gets "strangled")
4. Eventually, monolith is completely replaced

**Visual:**
```
Before:
Client → Monolith (handles everything)

During Migration:
           ┌─ New Service (handles Users)
           │
Client → Strangler Proxy ─ Monolith (handles Orders, Payment, etc.)
           └─ Checks which service to route to

After:
Client → Microservices (User, Order, Payment all independent)
```

## How It Works: Step by Step

### Step 1: Extract One Service
Pick one small, low-risk service to extract first.

**Example:** User Service is standalone, few dependencies

```
Monolith:
├── User management (independent, stable)  ← Extract this
├── Orders (depends on users)
├── Payments (depends on orders)
└── Inventory
```

### Step 2: Create Strangler Proxy
Build a "reverse proxy" that intercepts requests and decides where to route them:
```
request comes in → Strangler checks request → routes to new User Service
                → if no User Service yet → routes to old Monolith
```

This proxy understands URL patterns:
```
if (request.path.startsWith("/api/users")) {
  routeToService("userService");  // new service
} else {
  routeToMonolith();  // old code
}
```

### Step 3: Duplicate Data (Cautiously)
New service needs its own database, but monolith still has the data.

**Option A (Sync on write):**
```
Client sends update → Monolith updates its User DB
                  → Monolith also calls User Service to update its DB
```
Risk: Monolith makes both calls; if User Service fails, whole thing fails. Bad.

**Option B (Events):**
```
Monolith: User updated → publishes "UserUpdated" event
User Service: subscribes → updates its own database
```
Better: Decoupled. If User Service is down, it catches up when it recovers.

**Option C (Mirror/Backup):**
```
Separate process: reads from Monolith's DB → writes to User Service's DB (sync every night)
```
Simple, safe, but not real-time.

### Step 4: Canary Deployment
Route small % of traffic to new service, monitor for issues:
```
90% traffic → Monolith (safe, proven)
10% traffic → User Service (testing in prod)
```

If problems, drop new service back to 0%. If all good, increase percentage:
```
90% → 80% → 50% → 20% → 0% (full cutover)
```

### Step 5: Parallel Run & Fallback
Run both monolith and new service in parallel:
```
User Service receives request
  ↓ (write goes to new DB)
  ↓ (read also goes to Monolith, compares results)
  → if mismatch, log error, use Monolith result
  → alerts team to debug discrepancy
```

This catches bugs before users see them.

### Step 6: Cutover
Once confident, point all traffic to new service:
```
100% → User Service
```

Keep monolith running in background for a while (quick rollback if needed).

### Step 7: Iterate
Repeat for next service (Orders, Payments, etc.)

**Timeline Example:**
```
Month 1: Extract User Service
Month 2: Extract Order Service
Month 3: Extract Payment Service
Month 6: Monolith only has Inventory, still stable
Month 12: Inventory extracted, monolith dead
```

## Real-World Example: Shopify

Shopify migrated from Rails monolith to microservices using strangler pattern:
- Started with extracting API layer (2012-2014)
- Each year, extracted another service
- Took many years but zero downtime, no massive rewrites
- Old code gradually "strangled" as new services took over

## Key Benefits

✅ **Low risk** — If new service fails, fall back to monolith
✅ **Incremental** — Ship value each month, don't wait for complete rewrite
✅ **Parallel teams** — Team A works on User Service while Team B maintains monolith
✅ **Rollback easy** — Keep monolith running; just redirect traffic back if needed
✅ **Test in prod** — Canary deployment lets you test with real traffic safely

## Common Pitfalls

### ❌ Mistake 1: Extracting Too Many Services at Once
**Wrong:** Try to extract User, Order, and Payment simultaneously
**Right:** Extract User first. Ship it. Then Order. Then Payment.

### ❌ Mistake 2: Cutting Over Too Quickly
**Wrong:** 100% traffic to User Service after 1 day of testing
**Right:** 10% → 25% → 50% → 100% over 2 weeks, monitoring closely

### ❌ Mistake 3: Monolith and New Service Out of Sync
**Wrong:** Monolith's User DB and User Service's DB have different data
**Right:** Use events to keep both in sync during migration period

### ❌ Mistake 4: No Fallback Plan
**Wrong:** Delete monolith code immediately after cutover
**Right:** Keep monolith running for 1 month, ready for emergency rollback

### ❌ Mistake 5: Strangler Proxy Becomes a Bottleneck
**Wrong:** Proxy is slow, adds latency, becomes single point of failure
**Right:** Keep proxy simple and fast; use CDN/load balancer to scale it

## When to Use Strangler

**Perfect for:**
- Migrating large, stable monolith to microservices
- Teams that can't afford downtime
- Want to move at sustainable pace
- Want to test incrementally

**Not the right tool:**
- Building new system from scratch (use microservices from start)
- Monolith is very tightly coupled (strangling takes forever)
- Need to move fast, can afford downtime (just rewrite)

## Interview Frame

**Q: You need to migrate a monolith to microservices. How?**
A: Use the Strangler Pattern. Build new services alongside the monolith. Use a proxy to gradually route traffic. Start with low-risk, independent services. Canary deploy, parallel run, then cutover.

**Q: What if the new service fails?**
A: Proxy immediately routes back to monolith. Zero impact to users (that's the safety).

**Q: How do you keep data in sync during migration?**
A: Use events. Monolith publishes "User Updated" event; new service subscribes and updates its database. Both stay consistent.

**Q: How long does this take?**
A: Depends on monolith size. Typically 1-3 services per year. Shopify took 5+ years but zero downtime, sustainable pace.
