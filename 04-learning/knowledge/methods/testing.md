---
type: knowledge
status: stable
topics: ['testing', 'pytest']
related: ['../technologies/python/pytest.md']
---

# Testing Notes

## Unit Testing vs. Integration Testing
- **Unit Testing:** Tests individual components (e.g. functions, helper methods) in isolation. External dependencies (like databases or APIs) are mocked.
- **Integration Testing:** Tests how different parts of the system work together (e.g. hitting an endpoint to ensure it writes to a test database and returns the correct response).

## pytest best practices
- For an in-depth reference on fixtures and Dependency Injection, see [Pytest Fixtures & Dependency Injection](../technologies/python/pytest.md).
- Use fixtures (`@pytest.fixture`) for setup and teardown logic (e.g., creating and rolling back database sessions).
- Keep tests fast by using in-memory databases (sqlite) or a separate Postgres test database that gets cleaned/re-seeded before each test.
- Use `pytest-cov` to measure and monitor code coverage.
