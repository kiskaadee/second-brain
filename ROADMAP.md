# Strategic Roadmap - Backend Residency

This document outlines the milestones and gates of the Backend Residency. Instead of strict dates, it tracks progress using explicit status states, estimated efforts, and verification tests.

---

## 🏁 Flagship Project: BiteTrack Backend v2
Rebuild the original BiteTrack backend using modern Python technologies and production-grade engineering practices.
- **Mission:** Rebuild BiteTrack from the ground up focusing on professional backend engineering. The goal is not feature parity with legacy version, but demonstrating clean code, tests, and API standards.
- **Key Modules:** Auth & RBAC, Products & Categories, Orders & Transaction safety, Search & Filtering, and logging.
- **Reference Docs:** [project/README](https://github.com/kiskaadee/bitetrack-api/blob/main/README.md), [project/architecture](https://github.com/kiskaadee/bitetrack-api/blob/main/docs/architecture.md), [project/api-design](https://github.com/kiskaadee/bitetrack-api/blob/main/docs/api-design.md), [project/database](https://github.com/kiskaadee/bitetrack-api/blob/main/docs/database.md).

---

## Milestones

### Milestone 0: Development Environment & Setup
- **Status:** 🟢 Completed
- **Estimated Effort:** 5–10 hours
- **Tasks:**
  - Configure workspace structure & symlink (`~/todo.md`)
  - Initialize Python environment using `uv`
  - Configure Ruff, Pyright, and code formatter
  - Setup multi-container Docker Compose file (`FastAPI` & `PostgreSQL`)
- **Relevant ADRs:**
  - [ADR 0001: Language Choice (Python)](docs/adr/0001-python.md)
  - [ADR 0002: Framework Choice (FastAPI)](docs/adr/0002-fastapi.md)
  - [ADR 0003: Database Choice (PostgreSQL)](docs/adr/0003-postgresql.md)
  - [ADR 0004: Project Structure](docs/adr/0004-project-structure.md)
- **Acceptance Tests:**
  - [x] Running `docker compose up` starts the PostgreSQL database container.
  - [x] Running `curl http://localhost:8000/docs` yields a valid HTML response (FastAPI running in local devShell).
- **Interview Checkpoint:**
  - [ ] Why do we use virtual environments (e.g., `uv`)?
  - [ ] What is the difference between a Docker image and a Docker container?
  - [ ] Why do we use Docker Compose for local development?

---

### Milestone 1: Secure User Registration & CRUD
- **Status:** 🟥 Not Started
- **Estimated Effort:** 15–20 hours
- **Research:**
  - Read FastAPI official documentation on path parameters and Pydantic models.
  - Read HTTP specifications for Methods and Response Status Codes.
- **Implement:**
  - `POST /auth/register` (user creation)
  - `GET /users/me` and `PATCH /users/me` profile endpoints
- **Verify:**
  - [ ] Test endpoints manually with `curl` and parse response with `jq`.
  - [ ] Verify validation errors format matches standard JSON error formats.
- **Acceptance Tests:**
  - [ ] Create user through API, fetch details, and verify fields match input payload.
  - [ ] Attempting to register a user with invalid email syntax returns `422 Unprocessable Entity`.
- **Interview Checkpoint:**
  - [ ] What is the request-response lifecycle?
  - [ ] What is the difference between `PUT` and `PATCH`?
  - [ ] Why do we use Pydantic for validation and serialization?

---

### Milestone 2: Relational Schema & Persistence (PostgreSQL)
- **Status:** 🟥 Not Started
- **Estimated Effort:** 20–25 hours
- **Research:**
  - Read SQLAlchemy documentation on Declarative Mappings and Async Sessions.
  - Read Alembic documentation on migration generations.
- **Implement:**
  - User and Profile relational model tables.
  - DB sessions injection dependencies.
  - Initial migration scripts.
- **Verify:**
  - [ ] Run raw SQL commands directly inside PostgreSQL client container to verify data fields.
- **Acceptance Tests:**
  - [ ] Initialize migration database successfully.
  - [ ] Register user, restart the database container, and verify the user still exists (persistence check).
  - [ ] Run Alembic downgrade and upgrade successfully without errors.
- **Interview Checkpoint:**
  - [ ] What are the ACID properties in databases?
  - [ ] What is the difference between an `INNER JOIN` and a `LEFT JOIN`?
  - [ ] What is database indexing, and when should you avoid using it?
  - [ ] Why do we use migrations instead of executing direct SQL statements against production databases?

---

### Milestone 3: Security & RBAC (Role-Based Access Control)
- **Status:** 🟥 Not Started
- **Estimated Effort:** 25–30 hours
- **Research:**
  - Read OAuth2 password flow specifications.
  - Read JWT standard specifications (claims, signatures).
- **Implement:**
  - Secure `/auth/token` login endpoint generating Access/Refresh tokens.
  - Token verification guards and user role decorators (Admin, Staff, Customer).
- **Verify:**
  - [ ] Ensure passwords stored in the database are hashed (never plaintext).
  - [ ] Verify access tokens expire in 15 minutes and refresh tokens rotate properly.
- **Acceptance Tests:**
  - [ ] Attempt to access a protected endpoint without an Authorization header returns `401 Unauthorized`.
  - [ ] Attempt to access an Admin resource using a Customer credential returns `403 Forbidden`.
  - [ ] Tokens refreshed successfully via HttpOnly cookie endpoints.
- **Interview Checkpoint:**
  - [ ] How does JWT authentication work?
  - [ ] Why do we use Refresh Tokens, and where should they be stored?
  - [ ] What is Role-Based Access Control (RBAC)?

---

### Milestone 4: Product Inventory & Transactions
- **Status:** 🟥 Not Started
- **Estimated Effort:** 25–35 hours
- **Research:**
  - Read SQLAlchemy documentation on transactions and concurrency locks.
- **Implement:**
  - Product and Category tables.
  - Stock control routes.
  - Transaction-safe `/orders` processing endpoint.
- **Verify:**
  - [ ] Verify query parameters for filtering, pagination, and text search yield the expected subsets.
- **Acceptance Tests:**
  - [ ] Place an order for an item: check that stock levels are decremented atomically.
  - [ ] Attempt to order an item with quantity exceeding stock level: check that the order is rejected and transaction rolls back.
  - [ ] Concurrently place orders to verify stock level never falls below zero.
- **Interview Checkpoint:**
  - [ ] What is transaction isolation, and why does it matter?
  - [ ] How do you handle database race conditions?
  - [ ] What is offset pagination vs keyset pagination?

---

### Milestone 5: Robust Testing, Logging & CI/CD
- **Status:** 🟥 Not Started
- **Estimated Effort:** 20–30 hours
- **Research:**
  - Read pytest documentation on fixture scopes and async support.
  - Read Nginx/Caddy documentation for reverse proxy configuration.
- **Implement:**
  - Full pytest integration test client suite.
  - Multistage Dockerfile.
  - GitHub Actions testing workflow.
- **Verify:**
  - [ ] Verify application tests execute on every push in GitHub.
- **Acceptance Tests:**
  - [ ] Test suite executes successfully with >80% code coverage.
  - [ ] Production Docker image builds under 200MB.
- **Interview Checkpoint:**
  - [ ] What is the difference between unit testing and integration testing?
  - [ ] Why do we use fixtures in pytest?
  - [ ] What is reverse proxying, and why should you place your backend behind it?
