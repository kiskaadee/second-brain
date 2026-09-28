---
type: plan
status: active
project: praxis
tags:
  - praxis
  - architecture
  - ddd
  - python
  - implementation
  - blueprint
---

# Praxis Implementation Blueprint

Blueprint translating [SRS v1.0.2](../praxis-srs-v1.0.2.md) + [Domain Model v1.0.1](../praxis-domain-model-v1.0.1.md) into concrete Python decisions.

> [!NOTE]
> This document is the canonical Phase 0 deliverable (v0.2.0 — Phase 0 Complete). All Phase-1-blocking ambiguities are resolved. Remaining open questions are explicitly deferred to the phases indicated below.

---

## Package Structure

```
src/praxis/
├── domain/
│   ├── aggregates/      exercise.py, routine.py, workout_session.py
│   ├── value_objects/   identifiers.py, measurement.py, enums.py, snapshot.py, set_data.py
│   ├── policies/        completion_policy.py, metric_validation.py, workload_calculator.py, adherence_calculator.py
│   └── factories/       session_snapshot_factory.py
└── application/
    ├── ports/           repositories.py, auth_provider.py, clock.py
    ├── use_cases/       routine/, session/, query/
    └── dtos/
```

---

## Dependency Direction

```
domain/                    ← No external dependencies
application/use_cases/     ← depends on: domain/, application/ports/
application/ports/         ← depends on: domain/ (Protocol definitions only)
infrastructure/            ← depends on: domain/, application/ports/
                             (NEVER depends on application/use_cases/)
```

---

## Key Decisions

### Immutability Strategy

- Value objects → `@dataclass(frozen=True)`
- Entities → `@dataclass(eq=False)` with identity-based `__eq__`
- `SessionPrescriptionSnapshot` uses `tuple` children for physical immutability
- `SetData` is an explicit frozen value object in `domain/value_objects/set_data.py` (prevents `record_set()` and `MetricValidationPolicy` from developing divergent representations)

### IDs

- Newtype frozen dataclasses wrapping `uuid.UUID`
- All defined in `domain/value_objects/identifiers.py`

### Aggregate Construction

- `create()` is the public API surface.
- The dataclass `__init__` is the implementation mechanism; left available for infrastructure adapter rehydration only.

### Repository Ports

- Defined as `Protocol` classes in `application/ports/repositories.py`.
- Method signatures are provisional; the existence of ports as `Protocol` classes is frozen.

---

## Resolved Ambiguities (Phase 0 Pass)

| Ambiguity | Resolution |
| :--- | :--- |
| `SetPerformance` metric fields | `actual_distance: Distance \| None` added to `SetPerformance` for `DistanceDuration` sprint-style sets. Continuous cardio distance stays on `ActivityPerformance`. |
| `CompletionPolicy` | Count-based rule only: `count(logged sets) >= target_sets`. "Honest effort" language is UX copy, not a domain predicate. |
| `finish()` override states | Legal overrides: `Completed` and `Partially_Completed` only. `In_Progress` and `Skipped` are illegal overrides; use `skip()` for skipped sessions. |
| Metric snapshotting | `PrescriptionSnapshotItem` explicitly freezes `metric_type: MetricType` so validation uses the exercise's metric type at session-start time. |
| `ScheduledWorkout` | Read model / application DTO — never persisted; constructed on the fly by `QueryWeeklyCalendarUseCase`. |
| `Phase.end_week = None` fallback | Returns the last-defined phase. An empty `phases` list raises `ValueError` at construction time. |

---

## Implementation Phase Sequence

| Phase | Scope |
| :--- | :--- |
| 0 | Implementation Readiness (**Complete** — this document) |
| 1 | Pure Domain Foundation — aggregates, value objects, policies, 90%+ coverage |
| 2 | Application Layer — use cases with in-memory fakes |
| 3 | Infrastructure — SQLAlchemy/SQLite |
| 4 | FastAPI Interface |
| 5 | Containerisation + Authelia |

---

## Phase 1 Implementation Order

```
identifiers → enums → measurement → RepRange → SetData
    → Exercise
    → Routine (+ Phase + get_current_phase)
    → MetricValidationPolicy
    → SessionSnapshotFactory
    → WorkoutSession
    → CompletionPolicy → WorkloadCalculator → AdherenceCalculator
```

Each step is **test-first**. Domain tests only: no mocks, no database, no HTTP.

---

## Deferred Open Questions

| # | Question | Blocking Phase |
| :--- | :--- | :--- |
| OQ-1 | `session_date` uniqueness enforcement level | Phase 2 |
| OQ-3 | Weight unit preference storage location | Phase 2 |
| OQ-4 | Bodyweight prescription (`target_weight = None`) UI communication | Phase 4 |
| OQ-5 | Exercise catalog seeding mechanism | Phase 3 |
