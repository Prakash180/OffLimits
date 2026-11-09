# Message Queues

Goal: understand why services talk to each other *asynchronously* through a queue instead of calling each other directly, and the trade-offs that come with it.

## The Problem (Direct/Synchronous Calls)

- Service A calls Service B directly and waits for a response.
- If B is slow → A is stuck waiting (blocked threads, timeouts pile up).
- If B is down → A's request fails outright.
- If 10,000 requests hit A at once → A dumps all 10,000 onto B instantly → B falls over.
- A and B are **tightly coupled**: both must be up, both must be fast, at the same time.

## The Idea: A Buffer In Between

- Analogy: a restaurant kitchen. Waiters (producers) drop order tickets on a rail (the queue). The chef (consumer) pulls tickets off whenever free, one at a time. Customers don't wait for the chef to be free.
- **Producer** → sends a message → **Queue (Broker)** → **Consumer** pulls it whenever ready.
- Producer and consumer never need to be online/fast at the same time — that's **decoupling**.
- If consumer is briefly down, messages just wait in the queue — nothing is lost.
- If there's a burst of traffic, the queue absorbs it and the consumer drains it at its own pace (**load leveling / buffering**), instead of the consumer getting overwhelmed.

```
Producer ---> [ Queue / Broker ] ---> Consumer
   (send)                              (pull, process, ack)
```

## Point-to-Point vs Publish/Subscribe

- **Point-to-point (queue)**: one message → exactly ONE consumer processes it. E.g. "process this order" — only one worker should charge the card.
- **Pub/Sub (topic)**: one message → broadcast to ALL subscribers. E.g. "order placed" event goes to billing, inventory, and email services all at once, independently.

## Delivery Guarantees (important interview topic)

| Guarantee | Meaning | Risk |
|---|---|---|
| At-most-once | Message sent once, might get lost | Silent data loss |
| At-least-once | Message never lost, but may be delivered twice | Duplicate processing (most common default) |
| Exactly-once | Delivered & processed exactly once | Hard to guarantee in practice; usually simulated via idempotency + dedup |

- Most real systems pick **at-least-once** because it's the safest easy default — but that means consumers MUST be **idempotent** (safe to process the same message twice without bad side effects, like double-charging a card).

## Other Key Concepts

- **Broker**: the actual server that stores/routes messages (RabbitMQ, Kafka, SQS...).
- **Visibility timeout / lease**: when a consumer pulls a message, it becomes temporarily invisible to others. If the consumer crashes before acknowledging (deleting) it, the message becomes visible again and gets redelivered to another consumer. This is *how* at-least-once delivery is implemented.
- **Ordering**: some queues guarantee strict order (FIFO), others sacrifice order for throughput. Kafka guarantees order only *within a partition*, not across the whole topic.
- **Dead-letter queue (DLQ)**: messages that fail processing repeatedly get moved here instead of blocking/retrying forever, so they can be inspected/fixed separately.
- **Backpressure**: if consumers fall behind, the queue just grows instead of crashing the whole system — but you still need alerts/autoscaling so the backlog doesn't grow forever.

## Real-World Tools

| Tool | Style | Notes |
|---|---|---|
| RabbitMQ | Traditional broker | Point-to-point + pub/sub, flexible routing rules |
| Apache Kafka | Distributed log | High throughput, replayable, ordered per-partition |
| AWS SQS | Managed queue | Simple, at-least-once, great for decoupling microservices |
| AWS SNS / Google Pub/Sub | Managed pub/sub | Fan-out one event to many subscribers |
| Redis Streams | Lightweight log | Good for smaller-scale needs |

## Practical Exercise

- Build a tiny in-memory message queue:
  1. `send(message)` — producer adds message to the queue.
  2. `receive()` — consumer pulls a message; it becomes invisible for a timeout window instead of being deleted immediately.
  3. `delete(id)` / `ack(id)` — consumer confirms processing; message is removed for good.
  4. A background check: if a message's visibility timeout expires without being acked (consumer "crashed"), put it back in the queue for redelivery.
  5. Make the consumer idempotent: track processed IDs so a redelivered/duplicate message doesn't get double-processed.
- Code for this exercise lives in `SideProject/src/systemdesign/messagequeue/`:
  - [Message.java](../../SideProject/src/systemdesign/messagequeue/Message.java) — id + payload envelope.
  - [InMemoryMessageQueue.java](../../SideProject/src/systemdesign/messagequeue/InMemoryMessageQueue.java) — `send`, `receive` (with visibility timeout), `ack`, and a background reaper that redelivers expired messages.
  - [MessageQueueDemo.java](../../SideProject/src/systemdesign/messagequeue/MessageQueueDemo.java) — simulates a consumer crash on `order-1`, then shows the redelivery being handled idempotently.
- Same style as the previous topic's demo: [ConsistentHashingDemo.java](../../SideProject/src/systemdesign/consistenthashing/ConsistentHashingDemo.java).

## How to Approach "What is a message queue?" in an Interview

1. **One-liner**: "It's a buffer that lets one part of a system hand off work to another asynchronously, without both needing to be available at the same time."
2. **Analogy**: restaurant order rail / a mailbox — drop it and walk away.
3. **Problem it solves**: decoupling, absorbing traffic bursts, resilience when downstream is temporarily down.
4. **Mechanics**: producer/consumer/broker, point-to-point vs pub/sub.
5. **Depth (if pushed)**: delivery guarantees, ordering, idempotency, DLQs, visibility timeout — this is where you show seniority.
6. **Real-world tie-in**: Kafka, RabbitMQ, SQS — grounds the answer in real systems.

## Related Notes

- [scalability-cheatsheet.md](scalability-cheatsheet.md) — queueing is listed there as a scaling pattern.
- [consistent-hashing.md](consistent-hashing.md) — another infra building block, often used *inside* distributed queue/broker systems for partitioning.
