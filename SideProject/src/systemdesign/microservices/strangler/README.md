# Strangler Pattern: Routing Facade Implementation

This directory contains a complete Java/Spring Boot implementation of the **Strangler Pattern** for gradually migrating from a monolith to microservices.

## Overview

The Strangler Pattern allows you to incrementally replace a monolith with microservices without downtime:

```
Phase 1: All traffic to monolith
         ↓
Phase 2: Canary test (10% to new service)
         ↓
Phase 3: Gradual rollout (50% to new service)
         ↓
Phase 4: Full migration (100% to new service)
         ↓
Phase 5: Decommission monolith
```

## Architecture

### StranglerFacade.java
The main routing controller that:
- Receives all client requests
- Routes to new microservices OR legacy monolith based on configuration
- Handles fallback if new service is down
- Implements dual-write for writes during migration

**Key routing logic:**
```java
if (routingConfig.isServiceEnabled("USER_SERVICE")) {
    return routeToNewService(...);  // Route to new service
} else {
    return routeToMonolith(...);    // Fall back to monolith
}
```

### RoutingConfig.java
Configuration service that manages:
- Which services are enabled (feature flags)
- Traffic percentage allocation (for canary deployment)
- Methods to enable/disable services at runtime

**Example:**
```
USER_SERVICE_ENABLED=true       # Service is available
USER_SERVICE_TRAFFIC=30         # Send 30% traffic to it, 70% to monolith
```

### StranglerConfig.java
Spring Boot configuration that:
- Creates RestTemplate for HTTP routing
- Configures timeouts (connection + read)

### Model Classes
- `UserRequest.java` — DTO for user operations
- `OrderRequest.java` — DTO for order operations

## Migration Phases

### Phase 1: All to Monolith (Safe baseline)
```
Environment variables:
  USER_SERVICE_ENABLED=false
  ORDER_SERVICE_ENABLED=false

Result: 100% of traffic goes to monolith
```

### Phase 2: Canary Test (10% traffic to new service)
```
Environment variables:
  USER_SERVICE_ENABLED=true
  USER_SERVICE_TRAFFIC=10

Result: 10% random requests go to User Service, 90% to monolith
Monitoring: Compare response times, error rates, behavior
```

### Phase 3: Gradual Rollout (Increase to 50%)
```
Environment variables:
  USER_SERVICE_ENABLED=true
  USER_SERVICE_TRAFFIC=50

Result: 50% to User Service, 50% to monolith
Action: Monitor metrics, logs, user feedback
```

### Phase 4: Full Migration (100% to new service)
```
Environment variables:
  USER_SERVICE_ENABLED=true
  USER_SERVICE_TRAFFIC=100

Result: All traffic goes to User Service
Safety: Monolith still running as backup
Action: Keep monolith live for 1+ month, ready for emergency rollback
```

### Phase 5: Decommission (Remove monolith endpoint)
```
Action: Monitor new service for 1 month
Action: Once confident, remove monolith code
Action: Delete legacy database if safe
```

## Write Strategy During Migration

### For Reads
```
GET /api/users/{id}
  ├─ If USER_SERVICE enabled → query new service
  ├─ If that fails → fallback to monolith
  └─ If not enabled → query monolith
```

### For Writes
```
POST /api/users
  ├─ ALWAYS write to monolith first (authoritative)
  ├─ If monolith succeeds AND new service enabled
  │   └─ Async write to new service (fire and forget)
  └─ Return monolith response to client
```

**Why dual-write?**
- Monolith is the source of truth during migration
- New service gets a copy for redundancy
- If new service write fails, we don't break the transaction
- New service can catch up via background sync/events

## Deployment

### Prerequisites
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

### Configuration
Set environment variables before running:
```bash
# Enable User Service canary
export USER_SERVICE_ENABLED=true
export USER_SERVICE_TRAFFIC=10

# Order Service still goes to monolith
export ORDER_SERVICE_ENABLED=false

java -jar application.jar
```

### Runtime Control
You can update routing config at runtime via REST API (extend RoutingConfig):
```bash
# Enable User Service
POST /admin/routing/USER_SERVICE/enable

# Set traffic to 50%
POST /admin/routing/USER_SERVICE/traffic?percentage=50

# Rollback to monolith
POST /admin/routing/USER_SERVICE/disable
```

## Monitoring & Logging

The facade logs all routing decisions:
```
✓ Async update to new service succeeded: http://user-service:8001/users
✗ Async update to new service failed: http://user-service:8001/users - Connection refused
User Service failed, falling back to monolith
✓ ENABLED routing to USER_SERVICE
→ USER_SERVICE traffic set to 50%
```

### Key Metrics to Monitor
1. **Error Rate:** Compare monolith vs new service errors
2. **Latency:** Is new service faster/slower than monolith?
3. **Traffic Split:** Verify traffic is actually going where we expect
4. **Data Consistency:** Do both services return same data?

### Example Monitoring Query (Prometheus)
```
// Error rate for User Service vs Monolith
rate(http_requests_total{status=~"5.."}[5m])

// Latency comparison
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Example: Migrating User Service

### Day 1: Deploy new User Service
- Service running, but traffic disabled
- Monolith handles all requests
- Verify service is healthy in background

### Day 2: Canary (10% traffic)
```bash
export USER_SERVICE_ENABLED=true
export USER_SERVICE_TRAFFIC=10
# Restart facade
```
- Monitor errors, latency, response behavior
- If issues, disable: `USER_SERVICE_ENABLED=false`

### Day 3-4: Increase to 50%
```bash
export USER_SERVICE_TRAFFIC=50
```
- More confidence data
- Ready for full rollout?

### Day 5: Full migration (100%)
```bash
export USER_SERVICE_TRAFFIC=100
```
- All traffic to new service
- Monolith still running as backup

### Day 5-35: Monitor and stabilize
- Keep monolith running for emergency rollback
- Collect 30 days of production data
- If any issues, we can quickly `USER_SERVICE_ENABLED=false` → back to monolith

### Day 35+: Decommission monolith
- Once fully confident, shut down monolith User endpoints
- Archive legacy code

## Handling Failures

### New Service Crashes
```
User requests → Facade detects connection refused
             → Falls back to monolith
             → Client gets response without knowing what happened
```

### Fallback Logic
```java
try {
    return routeToNewService(...);
} catch (RestClientException e) {
    System.out.println("New service failed, falling back to monolith");
    return routeToMonolith(...);
}
```

### Async Write Fails
```java
// Write to monolith succeeds
// Async write to new service fails
// Facade logs error, continues
// Operation: Later background sync picks it up via events
```

## Future Enhancements

1. **Circuit Breaker:** Add Netflix Hystrix to gracefully degrade
2. **Rate Limiting:** Throttle new service if it's slow
3. **A/B Testing:** Route by user segment instead of percentage
4. **Metrics Export:** Expose routing stats to Prometheus/Grafana
5. **Admin Dashboard:** UI to manage routing in real-time
6. **Event Replay:** Automatic catch-up for missed writes

## Comparison: Choreography vs Orchestration

This implementation uses **Orchestration**:
- Central routing (Strangler Facade) controls flow
- Clear, visible routing logic
- Easy to debug and monitor
- Single point of control

For comparison, **Choreography** would use:
- Events published to message queue (Kafka)
- New service subscribes independently
- Looser coupling but harder to track

## References

- [Microservices Patterns: Strangler Pattern](../strangler-pattern.md)
- [System Design Notes: Proxy and Reverse Proxy](../proxy-and-reverse-proxy.md)
- [Spring Boot RestTemplate Documentation](https://spring.io/projects/spring-framework)
