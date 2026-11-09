# SAGA Pattern

## The Problem: Distributed Transactions

You have three microservices (User, Order, Payment) that need to work together:
1. Debit user's account
2. Reserve inventory
3. Charge payment card

**Problem:** Traditional ACID transactions don't work across databases/services. If step 2 fails, how do you rollback step 1?

**Without SAGA:**
```
Begin Transaction
  ↓
Debit Account ✓
  ↓
Reserve Inventory ✗ (out of stock!)
  ↓
Charge Card ← should we still do this?
  ↓
BROKEN STATE: Account is debited, inventory not reserved, card not charged
```

## The Solution: SAGA (Distribute the Transaction)

A SAGA is a sequence of **local transactions** with **compensating transactions** (rollbacks):
```
1. Debit Account (local transaction in User Service)
   → if success, move to step 2
   → if fails, STOP

2. Reserve Inventory (local transaction in Order Service)
   → if success, move to step 3
   → if fails, ROLLBACK step 1 (credit account back)

3. Charge Card (local transaction in Payment Service)
   → if success, DONE
   → if fails, ROLLBACK steps 1 & 2
```

**Key idea:** Each step can undo itself. No central ACID guarantee, but coordinated success/failure.

## Two Flavors of SAGA

### 1. Choreography-Based SAGA
Services publish events; other services listen and react.

**How it works:**
```
1. Order Service: User creates order
   → publishes "OrderCreated" event

2. User Service: listens for "OrderCreated"
   → debits account
   → publishes "AccountDebited" event

3. Inventory Service: listens for "AccountDebited"
   → reserves stock
   → publishes "InventoryReserved" event

4. Payment Service: listens for "InventoryReserved"
   → charges card
   → publishes "PaymentCharged" event

5. Order Service: listens for "PaymentCharged"
   → marks order as confirmed
   → publishes "OrderConfirmed"

If Payment Service fails:
   Payment Service: publishes "PaymentFailed" event
   → Inventory Service: listens → releases stock → "StockReleased"
   → User Service: listens → credits account back → "AccountCredited"
   → Order Service: listens → marks order as cancelled
```

**Pros:**
- ✅ Loosely coupled (services don't know about each other)
- ✅ No central orchestrator to maintain

**Cons:**
- ❌ Hard to follow the flow (distributed across many services)
- ❌ Hard to test (too many async paths)
- ❌ Circular dependencies possible (Order → User → Order)

### 2. Orchestration-Based SAGA
Central orchestrator tells each service what to do.

**How it works:**
```
Central Orchestrator (OrderSaga)
  ↓
  ├─ Command to User Service: "Debit $50"
  │  User Service responds: OK
  │  ↓
  ├─ Command to Inventory Service: "Reserve 2 units"
  │  Inventory Service responds: OK
  │  ↓
  ├─ Command to Payment Service: "Charge $100"
  │  Payment Service responds: FAIL (card declined)
  │  ↓
  ├─ Compensate Inventory Service: "Release 2 units" ✓
  ├─ Compensate User Service: "Credit $50 back" ✓
  ↓
SAGA failed, order cancelled
```

**Pros:**
- ✅ Easy to see the flow (all in one place)
- ✅ Easy to test (orchestrator is a state machine)
- ✅ No circular dependencies

**Cons:**
- ❌ Tightly coupled (orchestrator knows about all services)
- ❌ Orchestrator is single point of failure (needs redundancy)

## Detailed Example: E-Commerce Order

### Choreography Example
```
Customer clicks "Buy Now"
  ↓
1. Order Service:
   - Creates order in database
   - Publishes "OrderCreated" event
   - Moves to PENDING_PAYMENT

2. User Service (subscribes to "OrderCreated"):
   - Loads user's wallet
   - Debits $100
   - Publishes "AccountDebited" event
   (if fails: publishes "AccountDebitFailed" event)

3. Inventory Service (subscribes to "AccountDebited"):
   - Checks stock: 5 units available
   - Reserves 2 units
   - Publishes "StockReserved" event
   (if fails: publishes "StockReservationFailed")

4. Payment Service (subscribes to "StockReserved"):
   - Charges customer's credit card
   - Publishes "PaymentCharged" event
   (if fails: publishes "PaymentFailed" event)

5. Order Service (subscribes to "PaymentCharged"):
   - Updates order status to CONFIRMED
   - Publishes "OrderConfirmed"
   - Customer sees "Order Confirmed!"

If at step 4, payment fails:
   - Payment Service publishes "PaymentFailed"
   - Inventory Service (subscribes) releases reserved stock
   - Inventory publishes "StockReleased"
   - User Service (subscribes) credits account back
   - User publishes "AccountCredited"
   - Order Service (subscribes) marks order as FAILED
   - Customer gets refund
```

### Orchestration Example
```
OrderSagaOrchestrator
  ├─ Call User Service API: POST /debit
  │  └─ User Service deducts $100 ✓
  ├─ Call Inventory Service API: POST /reserve
  │  └─ Inventory Service reserves 2 units ✓
  ├─ Call Payment Service API: POST /charge
  │  └─ Payment Service charges card ✗ (declined)
  ├─ Call Inventory Service API: POST /release (compensate)
  │  └─ Inventory releases 2 units ✓
  ├─ Call User Service API: POST /credit (compensate)
  │  └─ User Service credits $100 back ✓
  └─ Update Order Status: FAILED
```

## Handling Failures & Edge Cases

### Problem: A Compensation Fails
**Scenario:** Payment fails. You try to release inventory, but release fails too.

**Solutions:**
1. **Retry with backoff:** Try again after waiting
2. **Dead letter queue:** Put failed compensations in a queue for manual review
3. **Alert & Manual:** Page on-call engineer to fix manually
4. **Idempotent operations:** Make compensation safe to retry (don't double-release)

### Problem: Timeout (Service Takes Too Long)
**Scenario:** Payment Service takes 5 minutes to respond

**Solutions:**
1. **Long timeout:** Wait 5 minutes (but ties up resources)
2. **Eventual callback:** Payment Service calls back when done (async)
3. **Timeout as failure:** Assume it failed after 30s, start compensation (risky)

**Best:** Assume it failed, start compensation, but handle the race condition if Payment Service eventually succeeds:
```
Payment Service later: "Payment succeeded!"
Orchestrator: "Oops, we already refunded. Let me re-debit you."
(Messy, but safe)
```

### Problem: Idempotency
If a service crashes and restarts, it might replay a compensation twice:
```
1. Inventory released (compensation)
2. Service crashes
3. Service restarts, replays compensation
4. Inventory released AGAIN (double release!)
```

**Solution:** Make all operations idempotent (safe to run twice):
```
Inventory Service: "Release X units"
  → Check if already released
  → If yes, return success anyway
  → If no, actually release
```

Use unique `compensationId` to track what's been done.

## When to Use Choreography vs Orchestration

| Factor | Choreography | Orchestration |
|--------|---|---|
| **Coupling** | Loose | Tight |
| **Visibility** | Hard to see flow | Easy to see flow |
| **Testing** | Hard (async, distributed) | Easy (state machine) |
| **Scale** | Good (no bottleneck) | Need to scale orchestrator |
| **Simple flows** | OK | Better |
| **Complex flows** | Messy | Better |

**Rule of thumb:**
- **Few services, simple flow?** → Choreography is fine
- **Many services, complex flow?** → Orchestration is clearer
- **Unsure?** → Start with orchestration, refactor to choreography later if needed

## Common SAGA Pitfalls

### ❌ Mistake 1: SAGA as a Real Transaction
SAGA is NOT ACID. After a failure and compensation, you might have inconsistencies for a while.

**Right mindset:** SAGA gives you **eventual consistency**, not strong consistency.

### ❌ Mistake 2: Compensation that Fails Silently
If compensation fails, you don't notice. Account gets debited, inventory reserved, payment fails, compensation fails → stuck in broken state.

**Right:** Log, alert, and track all SAGA executions. Monitor for stuck SAGAs.

### ❌ Mistake 3: Over-Complicating Simple Cases
If it's just 2 services, 1 simple flow, don't use SAGA. Use a synchronous API call with retry + timeout.

**Right:** Use SAGA for complex multi-step flows only.

### ❌ Mistake 4: Not Idempotent
If a step is run twice by accident (timeout + retry), it might double-charge or double-reserve.

**Right:** All SAGA steps must be idempotent. Use unique IDs to prevent duplicates.

## Interview Frame

**Q: Design a checkout flow across User, Order, and Payment services.**
A: Use SAGA. Either choreography (services publish events) or orchestration (central coordinator). Handle failures with compensating transactions. Make operations idempotent.

**Q: What if a compensation fails?**
A: Log it, alert the team, put it in a dead letter queue. Don't silently fail.

**Q: Orchestration vs choreography?**
A: Choreography is looser (good for independent teams), orchestration is clearer (good for complex flows). Start with orchestration unless you need high decoupling.

**Q: Is SAGA an ACID transaction?**
A: No. It's eventual consistency. After compensation, there might be a brief inconsistency, but system resolves to a consistent state.
