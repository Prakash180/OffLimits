—# API Basics & Types

## What is an API?

- **API** = Application Programming Interface
- A contract that lets two systems talk to each other
- You ask for something → it gives you something back
- You don't need to know *how* it works internally — just *how to ask*

> Think of it like a waiter in a restaurant. You don't go into the kitchen yourself. You tell the waiter what you want, and they bring it back.

---

## Types of APIs

### 1. REST (Representational State Transfer)
- Uses HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Data format: usually **JSON**
- Stateless — every request is independent
- Most widely used API style today
- Best for: web apps, mobile apps, public APIs
- See: `rest-api-basics.md`

---

### 2. SOAP (Simple Object Access Protocol)
- Older, stricter protocol
- Data format: only **XML**
- Has a formal contract called a **WSDL** (Web Services Description Language)
- Heavier and more complex than REST
- Built-in error handling and security standards
- Best for: banking, enterprise systems, legacy integrations

---

### 3. gRPC (Google Remote Procedure Call)
- Made by Google, built on **HTTP/2**
- Data format: **Protocol Buffers (Protobuf)** — binary, not human-readable
- Much faster and lighter than REST/SOAP
- You define a `.proto` file as a contract, and code is auto-generated
- Supports **streaming** (client, server, or both ways)
- Best for: microservices, internal service-to-service communication

---

### 4. GraphQL
- Made by Facebook
- One endpoint (`/graphql`) for everything — unlike REST's multiple URLs
- **Client decides exactly what data it wants** — no over-fetching or under-fetching
- Uses a **query language** (similar to JSON) to describe what you need
- Best for: complex UIs, mobile apps where bandwidth matters

> REST gives you the whole menu. GraphQL lets you order exactly what you want.

---

### 5. WebSockets
- A **persistent, two-way connection** between client and server
- Unlike HTTP, the connection stays open — both sides can send messages anytime
- Real-time communication
- Best for: chat apps, live scores, multiplayer games, stock tickers

---

### 6. Webhooks
- Reverse of a typical API call — **server calls YOU** when something happens
- You register a URL; the server sends a POST request to it when an event occurs
- No polling needed — push-based
- Best for: payment notifications, GitHub events, CI/CD triggers

> Normal API: "Hey, did anything happen?" (you ask repeatedly)
> Webhook: "I'll let you know when something happens." (server tells you)

---

### 7. SSE (Server-Sent Events)
- Server pushes updates to the client over a **one-way, persistent HTTP connection**
- Unlike WebSockets, only the **server can send** — client just listens
- Simpler than WebSockets; works over regular HTTP
- Best for: live feeds, notifications, dashboards, real-time logs

---

## Quick Comparison

| Type       | Direction      | Protocol   | Format       | Real-time? | Best For                        |
|------------|----------------|------------|--------------|------------|---------------------------------|
| REST       | Request/Response | HTTP     | JSON         | No         | General web APIs                |
| SOAP       | Request/Response | HTTP     | XML          | No         | Enterprise, banking             |
| gRPC       | Request/Response + Streaming | HTTP/2 | Protobuf | Yes (streaming) | Microservices          |
| GraphQL    | Request/Response | HTTP     | JSON         | No (mostly)| Flexible data fetching          |
| WebSockets | Two-way        | WS / WSS   | Any          | Yes        | Chat, games, live data          |
| Webhooks   | Server → Client | HTTP     | JSON/XML     | Event-driven | Notifications, triggers       |
| SSE        | Server → Client | HTTP     | Text/JSON    | Yes        | Live feeds, dashboards          |

---

## How to Choose?

- Need a simple CRUD API? → **REST**
- Need speed between internal services? → **gRPC**
- Frontend needs flexible/custom data? → **GraphQL**
- Need real-time two-way chat? → **WebSockets**
- Need one-way live updates (news feed, logs)? → **SSE**
- Need to be notified when an event happens? → **Webhooks**
- Working with legacy enterprise systems? → **SOAP**
