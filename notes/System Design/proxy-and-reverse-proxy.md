# Proxy and Reverse Proxy

## What's a Proxy? (Forward Proxy)

A **proxy** (forward proxy) is an intermediary that sits between a **client** and the **internet**:

```
Client → Proxy → Internet/Server
```

**Analogy:** You want to send a letter to someone but don't want them to know it came from you. So you ask a friend to mail it on your behalf. The friend is the proxy.

### How a Forward Proxy Works

```
Your Computer (10.0.0.1)
    ↓ (request)
Corporate Proxy (proxy.company.com)
    ↓ (makes request on your behalf)
External Server (google.com)
    ↓ (response)
Corporate Proxy
    ↓ (sends back to you)
Your Computer
```

**What the server sees:**
- Request coming from proxy's IP address, not your computer's IP
- Server doesn't know your real IP

### Why Use a Forward Proxy?

1. **Anonymity:** Hide your real IP address
   ```
   Your IP: 192.168.1.100
   Server sees: Proxy IP 203.0.113.45
   ```

2. **Access Control:** Company proxy blocks certain websites
   ```
   Employee tries to access facebook.com
   → Proxy blocks it
   → "This site is not allowed"
   ```

3. **Caching:** Proxy caches responses; next person gets it faster
   ```
   User A requests google.com → Proxy fetches it, caches response
   User B requests google.com → Proxy returns cached version (instant)
   ```

4. **Logging & Monitoring:** Track what employees access
   ```
   Proxy logs: "10.0.0.50 accessed youtube.com at 2pm"
   ```

5. **Content Filtering:** Block malware/ads
   ```
   Proxy intercepts request
   → "This file is malware, blocking"
   ```

### Real-World Example: Corporate Network

```
Company Intranet:
  Employee 1 (10.0.0.1) \
  Employee 2 (10.0.0.2)  ─→ Corporate Proxy (203.0.113.1) → Internet
  Employee 3 (10.0.0.3) /

Google sees: requests from 203.0.113.1 (not individual employees)
IT admin sees: "Employee 2 visited CNN at 3pm"
```

---

## What's a Reverse Proxy?

A **reverse proxy** is an intermediary that sits between **clients** and a **server** (or servers):

```
Client → Reverse Proxy → Servers
```

**Key difference:** Forward proxy hides the client. Reverse proxy hides the servers.

**Analogy:** You call a restaurant, but the restaurant has a receptionist who answers the phone. You don't know if there are 5 chefs or 20 chefs in the back. The receptionist is the reverse proxy.

### How a Reverse Proxy Works

```
Client (203.0.113.100)
    ↓ (request to "example.com")
Reverse Proxy (example.com, 203.0.113.50)
    ↓ (forwards to one of many servers)
Server 1 (10.0.0.1) ─┐
Server 2 (10.0.0.2) ─┼─ Client doesn't know these exist
Server 3 (10.0.0.3) ─┘
    ↓ (response goes back through proxy)
Reverse Proxy
    ↓ (client gets response)
Client
```

**What the client sees:**
- Only one server: `example.com`
- Doesn't know there are multiple servers behind it

**What the servers see:**
- Requests appear to come from the reverse proxy
- Can't see the original client's IP (unless proxy adds a header)

### Why Use a Reverse Proxy?

1. **Load Balancing:** Distribute traffic across multiple servers
   ```
   Request 1 → Server 1
   Request 2 → Server 2
   Request 3 → Server 1 (Server 3 is busy)
   Request 4 → Server 2
   ```

2. **Hiding Backend Architecture:** Client sees one "example.com", doesn't know there are 50 servers
   ```
   Client thinks: "I'm talking to example.com"
   Reality: Reverse proxy routes to one of 50 servers
   ```

3. **SSL/TLS Termination:** Encrypt/decrypt traffic once at proxy (not on each backend server)
   ```
   Client (encrypted) → Reverse Proxy (decrypt, re-encrypt if needed)
                     → Backend Servers (unencrypted, fast)
   ```

4. **Compression:** Proxy compresses responses before sending to client
   ```
   Server: 1MB response
   Proxy: compresses to 100KB
   Client: receives 100KB (faster network)
   ```

5. **Caching:** Proxy caches responses; frequent requests don't hit backend
   ```
   Request 1 for "/api/users" → Backend processes, returns data
   Request 2 for "/api/users" → Proxy returns cached data (instant)
   ```

6. **API Gateway:** Route different paths to different services
   ```
   /api/users → User Service
   /api/orders → Order Service
   /api/payments → Payment Service
   ```

7. **Rate Limiting & Security:** Block bad clients at proxy level
   ```
   Client making 1000 requests/sec → Proxy blocks it
   ```

### Real-World Example: Netflix Architecture

```
Users worldwide
    ↓ (request to netflix.com)
Reverse Proxy (Nginx)
    ├─ /video → Video Service (Server 1, 2, 3, ...)
    ├─ /search → Search Service (Elasticsearch)
    ├─ /billing → Billing Service (Server A, B, C, ...)
    └─ /recommendations → ML Service (GPU Servers)

Users see: single "netflix.com" endpoint
Reality: Requests routed to right service, then load-balanced across replicas
```

---

## Forward Proxy vs Reverse Proxy: Side-by-Side

| Aspect | Forward Proxy | Reverse Proxy |
|--------|---|---|
| **Position** | Between client & internet | Between clients & servers |
| **Hides** | Client IP | Server identity |
| **Client knows** | It's talking to a proxy | It's talking to `example.com` |
| **Server knows** | Proxy's IP, not client's | Proxy's IP, not real client's |
| **Who uses it** | Employees (company proxy) | Companies (load balancing) |
| **Main benefit** | Anonymity, caching, filtering | Load balancing, hiding architecture |
| **Example tools** | Squid, Tinyproxy | Nginx, HAProxy, Apache |

---

## Reverse Proxy in Microservices: API Gateway

In microservices, the reverse proxy is often called an **API Gateway**:

```
Client requests
    ↓
API Gateway (Reverse Proxy)
    ├─ Authentication: Is this request valid?
    ├─ Rate limiting: Is client going too fast?
    ├─ Routing: Which service should handle this?
    │   ├─ POST /users → User Service
    │   ├─ POST /orders → Order Service
    │   └─ POST /payments → Payment Service
    ├─ Load balancing: Which replica of the service?
    ├─ Response compression: Compress response
    └─ Caching: Cache common responses
    ↓
Multiple backend microservices
    ↓ (response goes back through gateway)
API Gateway
    ↓
Client gets response
```

**Example Nginx config (API Gateway):**
```nginx
server {
  listen 80;
  server_name api.example.com;

  # Route /users to User Service
  location /users {
    proxy_pass http://user-service:3000;
  }

  # Route /orders to Order Service
  location /orders {
    proxy_pass http://order-service:3000;
  }

  # Route /payments to Payment Service
  location /payments {
    proxy_pass http://payment-service:3000;
  }
}
```

When client requests `api.example.com/users`, Nginx:
1. Recognizes path `/users`
2. Forwards to `user-service:3000`
3. Gets response
4. Sends back to client

---

## Common Reverse Proxy Tools

1. **Nginx** — Fast, lightweight, widely used
2. **Apache HTTP Server** — Full-featured
3. **HAProxy** — Specialized for load balancing
4. **Traefik** — Modern, Kubernetes-friendly
5. **Envoy** — Service mesh sidecar proxy
6. **AWS ALB/NLB** — Cloud load balancers

---

## Real Example: Strangler Pattern Uses Reverse Proxy

Remember the **Strangler Pattern** from microservices? The "Strangler Proxy" is a reverse proxy:

```
During migration:
Client requests
    ↓
Strangler Proxy (Reverse Proxy)
    ├─ If request is /api/users → New User Service
    ├─ If request is /api/orders → Old Monolith
    └─ If request is /api/payments → Old Monolith

After migration:
Client requests
    ↓
Strangler Proxy
    ├─ All requests go to microservices
    └─ Monolith is dead
```

---

## Quick Reference

### Forward Proxy
- **Use when:** Want to hide client's identity or filter client traffic
- **Setup:** Client → Proxy → Server
- **Example:** Corporate proxy blocking facebook.com

### Reverse Proxy
- **Use when:** Want to hide server identity or distribute load
- **Setup:** Client → Proxy → Servers
- **Example:** Nginx routing /users to User Service, /orders to Order Service

---

## Interview Frame

**Q: What's the difference between a proxy and a reverse proxy?**
A: Forward proxy hides the client (sits between client & internet). Reverse proxy hides the servers (sits between clients & servers).

**Q: Why would you use a reverse proxy in microservices?**
A: Act as an API Gateway. Route /users to User Service, /orders to Order Service. Load balance across replicas. Rate limit. Handle SSL/TLS.

**Q: How does a reverse proxy help with the Strangler Pattern?**
A: Route new traffic to new services, old traffic to monolith. Gradually shift traffic as new services come online.

**Q: Can a reverse proxy cache responses?**
A: Yes. Nginx can cache GET requests, return them on next hit without hitting backend.

**Q: What if a backend server goes down?**
A: Good reverse proxies detect this and route to healthy servers. Health checks every few seconds; if server doesn't respond, skip it.
