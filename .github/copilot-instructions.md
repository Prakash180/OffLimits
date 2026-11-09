# Copilot Instructions

The `OffLimits` workspace is for **study purposes only**. It is a personal learning sandbox, not a production codebase.

## Purpose

- Reverse engineer and understand how the `panel-aggregationengine` project works.
- Practice Java / DSA / LLD / system design in small side projects.
- Learn Spring Boot, security (OAuth2/JWT), and cryptography hands-on.
- Build and revise notes in the `notes/` folder.

## Workspace Map

| Folder | What it is | Stack |
|---|---|---|
| `panel-aggregationengine/` | Study **copy** of a work repo (Nielsen Panel Aggregation Engine). Studied to understand dimensions, models, and data flow. | Java, Spring Boot, Gradle (`src/main`, `src/test`, `src/integrationTest`) |
| `SideProject/` | Practice Java: DSA problems (`dsa/`) and system design demos (`systemdesign/`: consistent hashing, message queue, microservices, saga). | Plain Java (IntelliJ module, no build tool) |
| `lld-lowleveldesign-main/` | Low-level design (LLD) practice code, imported from GitLab. | Java 21, Maven |
| `spring-petclinic/` | Upstream Spring PetClinic, used to reverse engineer a standard Spring Boot app. | Spring Boot 4.x, Gradle/Maven |
| `todos/` | Own Spring Boot TODO API built while learning. | Spring Boot 4.x, Gradle |
| `cryptography/` | PyJWT / OAuth2 experiments, a 16-module PyJWT course (`pyjwt-course/`), and a static learning site (`sitegen/` → `site/`). | Python 3.13+, `uv` |
| `notes/` | Concise revision notes (see below). | Markdown |

## Working Rules Per Project

- **`panel-aggregationengine/`**
  - Treat as a study copy. Prefer explaining over modifying.
  - If editing, follow existing Java + Spring Boot patterns, naming, and package layout.
  - Domain context: dimensions (Retailer, Demographics, Market) and models (e.g. `BD_byProduct`, `BD_byRetailer`, `CSE`, `CPA`) tracked in `model_status.md`; docs live in `docs/`.
  - Do not touch `gradle.lockfile`, `Jenkinsfile`, `keystore/`, or `ci/` unless explicitly asked.
- **`SideProject/`** and **`lld-lowleveldesign-main/`**
  - Keep code simple and readable; one concept per file/class.
  - Match the existing package layout (`dsa/`, `systemdesign/<topic>/`, etc.).
  - Add short comments only where the idea is non-obvious.
- **`spring-petclinic/`** and **`todos/`**
  - Explain Spring concepts (layers, DI, annotations) in beginner terms.
  - Stay with idiomatic Spring Boot: controller → service → repository.
- **`cryptography/`**
  - Python via `uv` (`uv run python <file>`); deps are in `pyproject.toml`.
  - Course examples must stay runnable and self-contained; keep the `NN-topic/` module numbering intact.
  - Rebuild the site after course changes: `uv run --with markdown --with pygments python sitegen/build.py`. Output goes to `site/`; don't hand-edit generated files there.
  - Never hardcode real secrets or tenant IDs; use `.env` (via `dotenv`).

## Notes Style (`notes/`)

- Written in **layman terms**: simple, precise, no unnecessary jargon.
- Built for **quick revision**: concise, scannable, bullet points, short paragraphs, clear headings.
- Prefer practical syntax examples over long theory. For Java, use simple snippets, not advanced abstractions.
- Folder layout:
  - `notes/API/`, `notes/Security/`, `notes/Java Basics/`, `notes/DSA/`
  - `notes/Spring-SpringBoot/`: start from `README-START-HERE.md`
  - `notes/System Design/`: flat, one file per topic
  - `notes/LLD/`: `solid-principles.md` plus `Design-Patterns/{Creational,Structural,Behavioural}/<pattern>.md`
- Design pattern note format: title, category blockquote, What/Why, Java example, Without-pattern, When, Pitfalls, Quick Recap table (use `Behavioural/strategy.md` as the template).
- When adding a pattern note, update `notes/LLD/Design-Patterns/CHEATSHEET.md` (move it from "Still To Cover" into the covered tables).
- Reuse existing note folders; don't create new top-level ones without asking.

## Code Assistance

- Explain code and concepts clearly, as if teaching a beginner.
- Prefer simple, readable solutions over clever or over-optimized ones.
- When reverse engineering, trace the flow end to end (entry point → service → data layer) and summarize it in plain language.
- Keep answers short; expand only when asked.
- Don't add features, refactors, or docs beyond what was requested.
- Never commit, push, or run destructive commands without asking.
