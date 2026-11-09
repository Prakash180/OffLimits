# Why System Design?

## The core problem

When you write code for the first time, you think about:
- Does it work?
- Is the logic correct?

That's enough when 10 people use your app.

But what happens when **10 million people** use it?
- Your single server crashes under the load.
- Your database can't handle that many queries.
- One bug brings the whole system down.

**System design is about building software that survives the real world.**

---

## What system design actually is

It's the process of deciding:
- **How** to structure your application
- **What** components to use (servers, databases, caches, queues)
- **How** those components talk to each other
- **What** happens when something fails

You're not writing code. You're making architectural decisions that affect millions of users.

---

## A simple analogy

Imagine you open a small tea stall.
- 1 person working → fine for 5 customers.
- 50 customers show up → chaos. Orders get lost. People wait too long.

What do you do?
- Hire more people (horizontal scaling).
- Create a system — one takes orders, one makes tea, one serves (separation of concerns).
- Keep popular items pre-prepared (caching).
- Use a token/ticket system so no order is lost even if it takes time (message queue).

You just designed a system. The same thinking applies to software.

---

## Why it matters in the real world

### 1. Things will fail
Servers crash. Networks drop. Disks fill up. Code has bugs.
A good system design anticipates failure and handles it gracefully — the user barely notices.

### 2. Traffic is unpredictable
A normal day might have 1,000 users. Then your app goes viral and 1,000,000 show up.
Your system needs to scale — fast.

### 3. Bad design is expensive to fix later
If you built everything into one giant application (a monolith) and now need to scale just one part of it, you may have to rewrite everything.
Good design makes future changes cheaper.

### 4. Downtime costs money
For companies like Amazon, **every minute of downtime = ~$220,000 in lost revenue**.
Availability isn't just a technical goal — it's a business requirement.

---

## Why it matters for you as a developer

- You'll be asked system design questions in **every senior+ interview**.
- Understanding it helps you write better code — because you understand the system your code runs in.
- It helps you communicate with architects, DevOps, and product teams.
- Even if you never design a system from scratch, you'll need to understand the one you're working in.

---

## What "good" system design looks like

A well-designed system is:

| Property | What it means |
|---|---|
| **Scalable** | Can handle more users without rewriting everything |
| **Available** | Stays up even when parts of it fail |
| **Reliable** | Does what it's supposed to, consistently |
| **Maintainable** | Easy to change, debug, and extend |
| **Performant** | Fast enough that users don't notice the wait |

No system is perfect on all five. Design is always about **trade-offs**.

---

## The key mindset shift

As a junior dev: *"Does my code work?"*

As someone thinking about system design: *"What happens when this works at 1000x the scale, with 3 servers failing, and a sudden traffic spike at 2am?"*

That's the shift. System design is engineering for the real world.

---

## What comes next

Now that you know *why*, the next step is understanding the building blocks:
- How do databases store and retrieve data efficiently?
- What is caching and why does it matter?
- How does a load balancer decide where to send traffic?
- What happens when two servers need to share data?

Each of these is a piece of the puzzle.
