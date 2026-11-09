# REST API Basics

## What is REST?

- **REST** = Representational State Transfer
- A set of rules/conventions for building APIs over HTTP
- Not a protocol — just a style (architectural style)
- An API that follows these rules is called a **RESTful API**

---

## Core Concepts

### Resource
- Everything in REST is a **resource** (e.g., a user, an order, a product)
- Each resource has a **URL** (called a URI) that identifies it
  - `/users` → all users
  - `/users/42` → user with ID 42

### HTTP Methods (Verbs)
| Method   | What it does             | Example              |
|----------|--------------------------|----------------------|
| GET      | Read / fetch data        | `GET /users/42`      |
| POST     | Create a new resource    | `POST /users`        |
| PUT      | Replace a resource fully | `PUT /users/42`      |
| PATCH    | Update part of a resource| `PATCH /users/42`    |
| DELETE   | Delete a resource        | `DELETE /users/42`   |

### HTTP Status Codes
| Code | Meaning                        |
|------|--------------------------------|
| 200  | OK — success                   |
| 201  | Created — new resource made    |
| 204  | No Content — success, no body  |
| 400  | Bad Request — your input is wrong |
| 401  | Unauthorized — not logged in   |
| 403  | Forbidden — logged in but no permission |
| 404  | Not Found — resource doesn't exist |
| 500  | Internal Server Error          |

---

## REST Constraints (Rules)

1. **Client-Server** — Frontend and backend are separate; they talk only via API
2. **Stateless** — Each request is independent; server doesn't remember previous requests
   - Any session state must be sent by the client (e.g., token in header)
3. **Uniform Interface** — Consistent URL structure and use of HTTP methods
4. **Cacheable** — Responses can be cached to improve performance
5. **Layered System** — Client doesn't know if it's talking to the real server or a proxy/load balancer

---

## Request Structure

```
GET /users/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer <token>
Accept: application/json
```

- **Headers** — metadata (auth token, content type, etc.)
- **Body** — data sent with POST/PUT/PATCH (usually JSON)
- **Query Params** — filters/options in the URL: `/users?role=admin&page=2`
- **Path Params** — part of the URL: `/users/{id}`

---

## Response Structure

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 42,
  "name": "Alice",
  "email": "alice@example.com"
}
```

---

## Idempotency

- **Idempotent** = calling it multiple times gives the same result
- GET, PUT, DELETE → idempotent
- POST → NOT idempotent (creates a new resource each time)
- PATCH → depends on implementation

---

## REST vs SOAP

| Feature    | REST             | SOAP                    |
|------------|------------------|-------------------------|
| Format     | JSON / XML       | Only XML                |
| Speed      | Faster, lighter  | Heavier                 |
| Flexibility| High             | Strict standards        |
| Usage      | Web/mobile APIs  | Enterprise / banking    |

---

## Common Design Conventions

- Use **nouns** in URLs, not verbs: `/users` not `/getUsers`
- Use **plural** for collections: `/orders` not `/order`
- Nest resources to show relationships: `/users/42/orders`
- Avoid deep nesting (max 2 levels is a good rule of thumb)
- Return consistent JSON structure in responses

---

## Versioning

- APIs change over time — versioning prevents breaking old clients
- Common approach: put version in URL → `/api/v1/users`
- Other approaches: version in header (less common)

---

## Authentication in REST

- REST is stateless, so auth info is sent with **every request**
- Common methods:
  - **API Key** — a secret key passed in header or query param
  - **Bearer Token (JWT)** — signed token in `Authorization` header
  - **OAuth 2.0** — delegated access (see `oauth2.md`)

---

## Quick Summary

> REST is a style of building APIs where resources are accessed via URLs, actions are expressed using HTTP methods, and every request is self-contained (stateless). It's the most common way web services communicate today.
