# Backend Residency Checklist

## Rules
- [ ] One backend framework only (FastAPI).
- [ ] One programming language only (Python).
- [ ] One portfolio project only (BiteTrack Backend v2).
- [ ] Every concept learned must appear in the project.
- [ ] No starting new technologies unless required by the roadmap.
- [ ] AI is a mentor, reviewer, and debugger—not the primary implementation tool.

---

## Milestone 0: Development Environment & Setup
- **Status:** 🟢 Completed
- **Estimated Effort:** 5-10 hours

### Tasks
- [x] Configure workspace directories (`docs/`, `journal/`, `project/`)
- [x] Link main `todo.md` file to `~/todo.md`
- [x] Initialize Python environment using `uv`
- [x] Set up Ruff for linting and formatting
- [x] Set up Pyright for type checking
- [x] Write `docker-compose.yml` defining a PostgreSQL service

### Acceptance Tests
- [x] Docker compose services launch successfully.
- [x] FastAPI endpoint returns status `200` at `/docs`.

### Interview Checkpoint
- [ ] Explain virtual environments.
- [ ] Explain Docker image vs container.
- [ ] Explain Docker Compose benefits.

---

## Milestone 1: Secure User Registration & CRUD
- **Status:** 🟡 In Progress
- **Estimated Effort:** 15-20 hours

### Research
- [x] Read FastAPI official guides on Routing, Dependency Injection, and Pydantic models.
- [x] Read HTTP status codes guidelines.

### Implement
- [x] `POST /auth/register` (user registration route - dummy validation skeleton)
- [ ] `GET /users/me` (get profile route)
- [ ] `PATCH /users/me` (update profile route)

### Verify
- [x] Execute curls with incorrect payloads to confirm validation triggers.
- [x] Verify validation responses return clear field errors.

### Acceptance Tests
- [ ] Register new user, query their profile, and match the return payload fields.
- [x] Registering with invalid email payload returns HTTP `422`.

### Interview Checkpoint
- [ ] Explain the request-response lifecycle.
- [ ] Difference between `PUT` and `PATCH`.
- [ ] Why do we use Pydantic models?

---

## Milestone 2: Relational Schema & Persistence (PostgreSQL)
- **Status:** 🟥 Not Started
- **Estimated Effort:** 20-25 hours

### Research
- [ ] Read SQLAlchemy documentation on Async Sessions and Declarative Mappings.
- [ ] Read Alembic documentation on migration generations.

### Implement
- [ ] Relational schema models for User & Profile.
- [ ] Alembic migration initialization and initial upgrade.
- [ ] Dependency injection setup for Database session lifecycle management.

### Verify
- [ ] Inspect raw database records in Postgres to confirm indexing configurations.

### Acceptance Tests
- [ ] Run Alembic migrations and verify structural table creations.
- [ ] Register user, restart PostgreSQL service, and ensure user profile persists.
- [ ] Downgrade migrations, check table removal, and re-apply successfully.

### Interview Checkpoint
- [ ] Explain the ACID database properties.
- [ ] Difference between `INNER JOIN` and `LEFT JOIN`.
- [ ] What is database indexing and when do we avoid it?
- [ ] Why do we use migrations instead of directly editing database schemas?

---

## Milestone 3: Security & RBAC (Role-Based Access Control)
- **Status:** 🟥 Not Started
- **Estimated Effort:** 25-30 hours

### Research
- [ ] Read OAuth2 standard guides.
- [ ] Read JWT structures specifications.

### Implement
- [ ] Hashing helper functions.
- [ ] `/auth/token` authentication and JWT output routes.
- [ ] Access/Refresh token rotation flows.
- [ ] Role check route dependencies.

### Verify
- [ ] Check DB data to ensure passwords are hashed.
- [ ] Check token expiration constraints.

### Acceptance Tests
- [ ] Accessing protected profile returns `401 Unauthorized` without a valid token.
- [ ] Querying admin profile with a Customer role returns `403 Forbidden`.
- [ ] Token refresh requests yield rotated tokens.

### Interview Checkpoint
- [ ] How does JWT authentication work?
- [ ] Why do we use Refresh Tokens and where do we store them?
- [ ] What is Role-Based Access Control?

---

## Milestone 4: Product Inventory & Transactions
- **Status:** 🟥 Not Started
- **Estimated Effort:** 25-35 hours

### Research
- [ ] Read SQLAlchemy documentation on transactions.

### Implement
- [ ] Product and Category CRUD endpoints.
- [ ] Transactional order placement logic.
- [ ] Catalog pagination, filtering, and text search rules.

### Verify
- [ ] Check pagination responses to ensure metadata matches returned count.

### Acceptance Tests
- [ ] Order request decrements product stock atomically.
- [ ] Order request for quantities exceeding stock level returns error and rolls back database change.
- [ ] Concurrent checkouts confirm stock levels never drop below zero.

### Interview Checkpoint
- [ ] Explain transaction isolation levels.
- [ ] How do you handle race conditions?
- [ ] Offset vs keyset pagination.

---

## Milestone 5: Robust Testing, Logging & CI/CD
- **Status:** 🟥 Not Started
- **Estimated Effort:** 20-30 hours

### Research
- [ ] Read pytest documentation on async fixtures.
- [ ] Read Nginx/Caddy setup rules.

### Implement
- [ ] Integration testing client setups and route test suites.
- [ ] Structured logging settings.
- [ ] Multi-stage production `Dockerfile` and GitHub Actions pipeline configurations.

### Verify
- [ ] Verify actions launch automatically on code commits.

### Acceptance Tests
- [ ] Test coverage matches or exceeds 80%.
- [ ] Production Docker image size is under 200MB.

### Interview Checkpoint
- [ ] Unit vs Integration testing.
- [ ] Explain the utility of pytest fixtures.
- [ ] What is a reverse proxy?
