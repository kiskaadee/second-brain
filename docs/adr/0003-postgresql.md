# ADR 0003: Database Engine (PostgreSQL)

## Status
Accepted

## Context
We need a robust, production-grade relational database. SQL databases are highly tested in junior backend interviews.

## Decision
Use **PostgreSQL** instead of SQLite or MongoDB.

## Consequences & Trade-offs
- **Pros:** Full feature set (concurrency, transactions, indexing, jsonb support) reflecting real-world backend jobs.
- **Cons:** Slightly more complex local setup compared to SQLite, which we will mitigate by using Docker Compose.
