# ADR 0004: Project Directory Structure

## Status
Accepted

## Context
A clean, scalable, and maintainable project directory structure is required for our flagship API to emulate production standards.

## Decision
Adopt a modular or layered architecture layout for the source code:
```
src/
├── main.py            # App entrypoint & lifespans
├── config.py          # Settings and environment config
├── database.py        # SQLAlchemy session & engine setup
├── models/            # SQLAlchemy database models
├── schemas/           # Pydantic schemas (requests/responses)
├── routers/           # FastAPI routers (endpoints)
├── services/          # Business logic and database operations
└── core/              # Security, dependencies, middleware
```

## Consequences & Trade-offs
- **Pros:** Distinct separation of concerns (validation, business logic, routing, persistence). Highly readable for interviewers.
- **Cons:** Slightly more boilerplate files to create compared to a single-file API.
