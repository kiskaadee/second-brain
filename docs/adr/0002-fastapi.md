# ADR 0002: Backend Framework Choice (FastAPI)

## Status
Accepted

## Context
We need a modern backend web framework with automatic docs, typing support, and dependency injection to build REST APIs efficiently.

## Decision
Use **FastAPI** as the primary backend framework.

## Consequences & Trade-offs
- **Pros:** Automatic OpenAPI/Swagger generation, standard dependency injection, asynchronous support, strong ecosystem integration with Pydantic.
- **Cons:** Less prescriptive structure than Django, requiring us to define our own architectural standards.
