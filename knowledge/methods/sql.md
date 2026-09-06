# SQL & Relational Databases Notes

## ACID Properties
- **Atomicity:** All operations in a transaction succeed or all fail.
- **Consistency:** Database transitions from one valid state to another.
- **Isolation:** Concurrent transactions don't interfere with each other.
- **Durability:** Once committed, changes survive system failures.

## Indexes
- An index speeds up data retrieval operations (SELECT) at the cost of slower writes (INSERT, UPDATE, DELETE) and extra storage.
- **When to use:** Columns frequently queried in `WHERE` clauses, JOIN keys.
- **When NOT to use:** Columns with low cardinality (e.g. booleans), tables with very few rows, columns frequently updated.

## Joins
- **INNER JOIN:** Returns records with matching values in both tables.
- **LEFT JOIN (or LEFT OUTER JOIN):** Returns all records from the left table, and matching records from the right. If no match, right-side columns are NULL.
