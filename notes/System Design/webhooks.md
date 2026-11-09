# Webhooks

Goal: understand how services notify each other about events in a push-based (not pull/polling) manner — especially useful when you need a response but don't want synchronous blocking.

## The Problem (Polling)

- Service A needs a response from Service B, so it keeps checking: "Is it done? Is it done? Is it done?"
- Wastes resources constantly polling the queue or database
- Adds unnecessary latency and overhead

## The Idea: Push Notification

- Instead of Service A pulling for updates, Service B **pushes** the result to Service A
- Service B sends an HTTP request to a callback URL on Service A with the result
- Service A is notified immediately when the work is done

```
Service A → Queue → (returns, continues)
                ↓
           Service B processes
           POST to Service A's callback URL
                ↓
           Service A gets result, continues
```

## Webhook Flow

1. Service A registers a webhook URL: "When done, POST to https://serviceA.com/callback/order123"
2. Service A sends a message to the queue and returns immediately
3. Service B picks up the message, processes it
4. Service B makes an HTTP POST request to Service A's webhook URL with the result
5. Service A receives and processes the callback

## Key Considerations

- **Delivery reliability**: webhooks might fail (network issue, Service A down). Need retry logic on sender side.
- **Idempotency**: Service A must handle duplicate webhook calls (same result sent twice) gracefully.
- **Security**: verify webhook signatures, authenticate callback requests, use HTTPS.
- **Ordering**: webhooks might arrive out of order if retries happen. Include timestamp/sequence in payload.
- **Timeouts**: webhook handlers must respond quickly (don't do heavy work in the callback itself).

## When to Use

- Service A needs to react to Service B's completion but doesn't want to wait synchronously
- Integrations with third-party services (Stripe → tells your app when payment succeeded)
- Real-time notifications (don't poll for status updates)

## Trade-offs vs Message Queues

| Aspect | Webhooks | Message Queue |
|--------|----------|---------------|
| Latency | Low (pushed immediately) | Can have delay (consumer pulls when ready) |
| Reliability | More complex (need retry/signature logic) | Built-in reliability guarantees |
| Coupling | Slightly tighter (A must know B's callback URL) | Loosely coupled |
| Debugging | Harder (async network calls) | Easier (messages in queue are visible) |

## Real-World Examples

- Stripe webhooks: tells your app when a charge succeeded
- GitHub webhooks: notifies your CI/CD when code is pushed
- Slack incoming webhooks: send messages to Slack from your app
