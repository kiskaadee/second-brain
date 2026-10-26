---
type: plan
status: active
project: skills
date: 2026-10-24
tags: [skills, agent-architecture, frontend-pilot, anne-droid, qa, armonia-del-ser]
---

# Pre-Experiment Baseline: Armonia Frontend Collaboration Pilot

> **Status:** Active Pre-Experiment Snapshot  
> **Target System:** `armonia-dashboard` (Operator Control Surface)  
> **Companion Repositories:** `armonia-api` (Backend), `armonia-del-ser/.profile` (Planning & Governance)  
> **Inspection Date:** 2026-10-24  
> **Epistemic Role:** Durable record of knowledge, hypotheses, repository baselines, and experimental protocols **prior** to running the frontend collaboration pilot. This is not a retrospective, an implementation plan for `rtt-agency`, or a declaration of validated results.

---

## Baseline Manifest

The following Git snapshots establish the verifiable repository state at the moment of inspection prior to any pilot execution:

| Repository | Current Branch | Full Commit Hash | Remote URL (Gitea) | Primary Relevance | Status / Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`armonia-dashboard`** | `main` | [`00b59182ac5c776879b7640e77eb6df6f3b085e9`](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/commit/00b59182ac5c776879b7640e77eb6df6f3b085e9) | `ssh://git@gitea.roadtotech.me:2223/armonia-del-ser/armonia-dashboard.git` | Target frontend application for the pilot implementation. | **Verified** (Clean tree, PR #8 merged) |
| **`armonia-api`** | `main` | [`d9c86e27d926bab3287857ccc9b53ec4fbcec91b`](https://gitea.roadtotech.me/armonia-del-ser/armonia-api/commit/d9c86e27d926bab3287857ccc9b53ec4fbcec91b) | `ssh://git@gitea.roadtotech.me:2223/armonia-del-ser/armonia-api.git` | Authoritative backend service; provides API contracts and test fixtures. | **Verified** (Clean tree, M2 completed) |
| **`.profile` (Workspace Root)** | `main` | [`89e3cffc8fc43ecb2ca5a05b6721f7bdbd75d3e8`](https://gitea.roadtotech.me/armonia-del-ser/.profile/commit/89e3cffc8fc43ecb2ca5a05b6721f7bdbd75d3e8) | `ssh://git@gitea.roadtotech.me:2223/armonia-del-ser/.profile.git` | Single Source of Truth for system roadmap, `todo.txt`, and cross-repo governance. | **Verified** (Clean tree, active SSOT) |

---

## 1. Problem Statement & Historical Context

### 1.1 The Armonia Workflow-Completeness Breakdown
The motivation for this pilot originated from a concrete failure in the initial delivery of the Armonia operator dashboard:

- **Original Scope**: Milestone M4 was defined in Gitea issue [`armonia-dashboard#1`](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/issues/1) (*"M4: Mobile-First Admin Dashboard for Jasmin & Assistant"*). It requested operational views for booking reviews, 48-hour pending payment follow-ups, payment acknowledgments, delayed-payment authorizations, and package/roster controls.
- **Implementation Sequence**: Anne Droid was delegated the frontend implementation under her existing persona instructions (`profile/agents/anne-droid.md`). In commit [`4e50f7c58606`](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/commit/4e50f7c58606709dbc9e95e7ad557869fb4dea78) (merged via PR [#4](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/pulls/4)), Anne scaffolded the dashboard with `FollowUpQueue.ts`, `PaymentModal.ts`, `DailyAgenda.ts`, and `AllBookings.ts`.
- **The Observed Defect**: While the delivered code was modular, typed, accessible, and tested with passing unit tests, the dashboard was **operationally incomplete**: an operator had no capability to create new client appointments from the interface. Furthermore, the workshop roster and package tracker were omitted.
- **The Corrective Rework**: The missing appointment-creation workflow had to be addressed in subsequent rework across separate issues ([`armonia-dashboard#6`](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/issues/6) and [`armonia-dashboard#7`](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/issues/7)), merged in PR [#8](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/pulls/8) ([`7f56fe019a0a`](https://gitea.roadtotech.me/armonia-del-ser/armonia-dashboard/commit/7f56fe019a0a0be96ffeb999e5f15549880816a7)).
- **Causal Interpretation (Inferred Hypothesis)**: The working explanation is that Anne's self-review procedure evaluated visual presence, component rendering, and isolated unit tests rather than structural workflow completeness against explicit acceptance criteria. Because existing views looked aesthetically sound and passed local unit checks, Anne concluded the task was complete. This diagnosis is plausible, but remains an *inference* to be tested by the pilot's interventions rather than an established historical fact.

### 1.2 Epistemic Label
**Verified (Observed Defect & Rework Chain)**: The commit messages, issue descriptions, PR diffs, and roadmap entries confirm the omission and subsequent rework.  
**Inferred (Causal Diagnosis)**: The claim that the omission was caused specifically by a lack of requirement-informed workflow verification in Anne's review protocol is an inference to be tested, not a proven historical fact.

---

## 2. Current Technical State & Candidate Deliverable

### 2.1 Candidate Deliverable: Group Workshop Roster Quick Check-in
To test the refined collaboration workflow, the candidate deliverable must represent a real, pending, bounded operational journey:
- **Roadmap Position**: In [`ROADMAP.md#L84`](https://gitea.roadtotech.me/armonia-del-ser/.profile/src/commit/89e3cffc8fc43ecb2ca5a05b6721f7bdbd75d3e8/ROADMAP.md#L84), Milestone M4 retains one remaining unchecked item:
  > `- [ ] Multi-session package counter ('8 de 10') & Group Workshop Roster check-in view.`
- **Backend API Readiness**: The backend capabilities were implemented in Milestone M2 ([`armonia-api#6`](https://gitea.roadtotech.me/armonia-del-ser/armonia-api/issues/6)) and are active on `armonia-api/main` ([`d9c86e27d926`](https://gitea.roadtotech.me/armonia-del-ser/armonia-api/commit/d9c86e27d926bab3287857ccc9b53ec4fbcec91b)):
  1. `GET /rosters` ([`app/routers/rosters.py#L36-L150`](https://gitea.roadtotech.me/armonia-del-ser/armonia-api/src/commit/d9c86e27d926bab3287857ccc9b53ec4fbcec91b/app/routers/rosters.py#L36-L150)): Queries group sessions within `[date_from, date_to]`, grouping bookings by session instant, returning attendees and capacity metrics (`RosterSessionRead`).
  2. `POST /rosters/quick-checkin` ([`app/routers/rosters.py#L153-L250`](https://gitea.roadtotech.me/armonia-del-ser/armonia-api/src/commit/d9c86e27d926bab3287857ccc9b53ec4fbcec91b/app/routers/rosters.py#L153-L250)): Supports two operational modes:
     - *Mode 1 (Existing Booking)*: Marks attendee `COMPLETED` and optionally records a cash payment.
     - *Mode 2 (Walk-In)*: Directly registers and checks in an unregistered walk-in attendee.
- **Backend Test Coverage**: Fully verified by integration tests in [`armonia-api/tests/test_rosters.py`](https://gitea.roadtotech.me/armonia-del-ser/armonia-api/src/commit/d9c86e27d926bab3287857ccc9b53ec4fbcec91b/tests/test_rosters.py) using the `circulo-cacao-presencial` test fixture.
- **Frontend Baseline**: In `armonia-dashboard/src/`, grep inspection confirms **zero** roster code currently exists. The view is completely pending.

### 2.2 Epistemic Label
**Verified**: The backend API exists and is tested; the frontend capability is pending; the task represents authentic unfinished scope from M4.

---

## 3. Pilot Rationale & Scoping Boundaries

### 3.1 Why This Pilot Is Being Considered
The pilot explores whether introducing structured, pre-implementation specification contracts and requirement-informed, code-blind verification prevents omissions while preserving frontend engineering velocity.

### 3.2 Explicit Inclusions (In Scope)
- Formulating an explicit **Project Collaboration Plan** for this deliverable.
- Formulating a two-part **Specification Contract**: Requirements & Acceptance Criteria distinct from UX Flows & Interaction States.
- Assembling a reproducible **Verification Packet** (test seeds, initial state, expected outcomes).
- Delegating implementation to **Anne Droid** in an isolated git worktree with an explicit change/escalation protocol.
- Executing an independent QA review blind to Anne's source code and PR narrative.
- Evaluating the process overhead, traceability, and defect detection rate.

### 3.3 Explicit Exclusions (Out of Scope)
- Creating the permanent `rtt-agency` repository or extracting shared personas.
- Modifying project governance or runtime adapters in `~/.gemini/config/`.
- Refactoring existing dashboard views (`DailyAgenda`, `FollowUpQueue`, `PaymentModal`).
- Modifying backend endpoints in `armonia-api`.
- Deciding whether 5 independent agents are permanently superior to 1 agent using disciplined stages.

---

## 4. Hypotheses Under Investigation & Epistemic Uncertainties

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           The Pilot Hypotheses                          │
├─────────────────────────────────────────────────────────────────────────┤
│ Hypothesis 1: Specification Completeness Reduces Workflow Omissions     │
│   An explicit, owner-approved specification of required operator        │
│   workflows and observable acceptance criteria reduces ambiguity and    │
│   prevents essential capabilities from being omitted during coding.     │
│   (Separating Requirements from UX is an evaluated design choice).      │
├─────────────────────────────────────────────────────────────────────────┤
│ Hypothesis 2: Bounded Engineering Autonomy Is Workable in Practice      │
│   Anne can exercise local design judgment (components, state handling,  │
│   ergonomics) without silently drifting into product scope changes or   │
│   unauthorized architectural commitments.                               │
├─────────────────────────────────────────────────────────────────────────┤
│ Hypothesis 3: Implementation-Blind QA Detects Incremental Defects       │
│   A reviewer who evaluates the running build using a Verification Packet│
│   — blind to implementation code and self-audit claims — detects defects│
│   and omissions that self-verification misses.                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Detailed Hypothesis Profiles

#### Hypothesis 1: Specification Completeness
- **Evidence Motivating It**: In M4, high-level view names failed to convey the essential operator journeys, causing the appointment-creation action to be missed.
- **Narrowed Claim**: An explicit, owner-approved specification of required operator workflows and observable acceptance criteria reduces ambiguity and prevents essential capabilities from being omitted during implementation.
- **Evaluated Design Choice**: The separation between Requirements (what/why + AC) and UX Design (how/flows/states) is introduced as an architectural design choice. The pilot observes whether this separation adds tangible clarity or unnecessary overhead, without assuming persona separation is mandatory.
- **Observation That Would Strengthen**: Anne delivers all required workflows without halting for basic scope clarification or omitting actions.
- **Observation That Would Weaken**: Anne still misses essential actions despite the contract, or the specification requires extensive rework before coding begins.
- **Limitation**: A single pilot cannot prove that separate personas are necessary to author the specification; it only tests the value of the explicit specification contract.

#### Hypothesis 2: Bounded Engineering Autonomy
- **Evidence Motivating It**: Current Anne instructions permit branch and PR autonomy, but lack clear rules on when API friction must be escalated versus worked around.
- **What Remains Unknown**: Whether Anne will halt unnecessarily on routine technical choices or attempt to work around backend contract gaps without reporting them.
- **Observation That Would Strengthen**: Anne raises explicit contract friction notices for backend ambiguities while resolving local component details independently.
- **Observation That Would Weaken**: Anne silently mocks missing API fields or stops work to ask for minor styling guidance.
- **Limitation**: Autonomy boundaries tested on this feature may not generalize to unfamiliar tech stacks.

#### Hypothesis 3: Implementation-Blind QA
- **Evidence Motivating It**: The `awwwards` skill demonstrates that an agent who knows the implementation plan evaluates intent rather than rendered reality.
- **Methodological Requirement (Falsifiability)**: To ensure valid comparison, Anne's self-audit (her own AC evaluation and visual evidence) must be captured and frozen *before* independent QA executes.
- **Evaluated Outcomes**:
  1. *QA finds confirmed defects missed by Anne*: Evidence that independent verification contributed incremental detection value.
  2. *QA confirms the same findings Anne identified*: Validates test reproducibility, but does not demonstrate incremental defect detection.
  3. *QA reports false positives or blocked tests*: Reflects on the verification setup/tooling, not necessarily the implementation.
- **Observation That Would Strengthen**: Independent QA identifies a confirmed functional bug, broken state transition, or accessibility flaw that Anne’s self-audit passed.
- **Observation That Would Weaken**: Independent QA fails due to missing context that was obvious in the code, or produces high false-positive defect reports.
- **Limitation**: A pilot where QA finds zero defects is inconclusive regarding the comparative advantage of independence; it does not prove independent QA is unnecessary.

---

## 5. Proposed Pilot Protocol & Handoff Contracts

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Proposed Pilot Protocol Flow                     │
│                                                                         │
│   Phase 1: Project Collaboration Plan & Baseline Snapshot               │
│   • Input: Verified repository state, ROADMAP.md, and issue #1.         │
│   • Output: Active roster, handoff definitions, and escalation paths.   │
│   • Gate: Human Project Owner approves the operating model.             │
│                                │                                        │
│                                ▼                                        │
│   Phase 2: Contract Formulation & Verification Packet                   │
│   • Input: API schema, workshop operational goals.                      │
│   • Output: docs/specs/workshop-roster.md + Verification Packet.        │
│   • Gate: Human Project Owner approves the Acceptance Criteria (AC).    │
│                                │                                        │
│                                ▼                                        │
│   Phase 3: Isolated Implementation & Frozen Self-Audit (Anne Droid)     │
│   • Input: Approved specification contract + API contracts.             │
│   • Workspace: Isolated worktree ../armonia-dashboard-anne-roster       │
│   • Output: feat/anne/workshop-roster, code, unit tests, PR on Gitea.   │
│   • Invariant: Anne executes and FROZES her own AC evaluation & visual  │
│     evidence before Independent QA begins.                              │
│   • Rule: Escalate contract friction; no silent scope modification.     │
│                                │                                        │
│                                ▼                                        │
│   Phase 4: Independent QA Pass (QA Specialist / Subagent)               │
│   • Input: Running URL + Verification Packet (AC + Seed Data).          │
│   • Blind To: Anne's PR text, source code, and self-audit claims.       │
│   • Output: Independent Evidence Scorecard (Pass/Fail per AC + shots).  │
│                                │                                        │
│                                ▼                                        │
│   Phase 5: Owner Review & Pilot Post-Mortem                             │
│   • Input: PR diff + Anne Frozen Audit + QA Evidence Scorecard.         │
│   • Evaluation: Adjudicate discrepancies and decide on merge.           │
│   • Post-Mortem: Evaluate operational metrics, friction, and findings.  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.1 The Explicit Escalation & Change Protocol
If any stage encounters a blocking condition, work halts and routes strictly according to problem type:

```
┌──────────────────────────────┬────────────────────────┬─────────────────────────────────────────┐
│ Condition Encountered        │ Responsible Role       │ Required Action                         │
├──────────────────────────────┼────────────────────────┼─────────────────────────────────────────┤
│ Contradictory business rule  │ Requirements Engineer  │ Clarify domain invariant; update ACs.   │
│ Unworkable interaction flow  │ UX Designer            │ Revise state transitions or hierarchy.  │
│ API contract defect / gap    │ Backend Owner / Lead   │ File structured issue with schema fix.  │
│ Implementation defect        │ Anne Droid             │ Fix in worktree and update PR.          │
│ Ambiguous test criterion     │ Requirements + QA      │ Update Verification Packet.             │
│ Scope change / trade-off     │ Project Owner (You)    │ Explicit human decision required.       │
└──────────────────────────────┴────────────────────────┴─────────────────────────────────────────┘
```

---

## 6. Success Observations & Boundary Limitations

### 6.1 Required Minimum Outcomes
- [ ] Essential operator workflows and acceptance criteria are approved before code is written.
- [ ] Anne raises contract friction notices rather than silently resolving missing backend data.
- [ ] Anne's self-audit is captured and frozen before independent QA evaluates the running application.
- [ ] QA evaluates every acceptance criterion using reproducible evidence (screenshots, console logs, network responses).
- [ ] Discrepancies between Anne's self-audit and independent QA findings are explicitly adjudicated.
- [ ] Consequential product and architectural decisions remain strictly under Project Owner authority.
- [ ] The workflow executes successfully inside the existing NixOS development environment.

### 6.2 Evaluated Process Observations
During and after the pilot, the following operational metrics will be recorded:
1. **Ambiguity Resolution Timing**: Count of ambiguities identified before coding (during specification) versus during implementation.
2. **Defect Delta & Detection Profile**:
   - Defect count found by independent QA that Anne's self-audit missed (incremental detection).
   - Defect count confirmed by both Anne and QA (reproducible verification).
   - Defect reports that were false positives or blocked tests due to verification environment issues.
3. **Return Loops**: Number and root cause of workflow reversions to earlier stages.
4. **Owner Interventions**: Number of escalations requiring consequential human decisions.
5. **Setup & Tooling Friction**: Material setup failures, devShell library issues, or blocked browser runs.
6. **Elapsed Stage Duration**: Rough duration per stage to assess practical overhead.
7. **Artifact Utility**: Whether the specification and verification packet remain durable documentation post-merge.
8. **Commit Discipline & Decomposition Quality**:
   - Number of implementation commits and whether each has a clear, reviewable purpose.
   - Whether each commit is coherent and passes relevant intermediate checks.
   - Whether reviewers can connect individual commits to specific acceptance criteria.
   - Whether any defect identified in verification can be localized to a particular increment.
   - Whether commit discipline added material overhead or encouraged unnecessary fragmentation.

---

## 7. Constraints, Preconditions & Deferred Decisions

### 7.1 Technical & Environmental Constraints
- **NixOS Environment**: Playwright and browser automation must execute cleanly within the local Nix devShell (`flake.nix`).
- **Gitea Port & Auth**: Remote operations use port `2223` with scoped SSH keys (`anneux` for Anne; `kiskaadee` for Owner).
- **Branch Protection**: No direct commits to `main` in `armonia-dashboard`. All work occurs in ephemeral worktrees.

### 7.2 Preconditions Before Pilot Execution
1. Owner review and explicit approval of this baseline document.
2. Formulation and approval of the `workshop-roster` Specification Contract and Verification Packet.

### 7.3 Deferred Decisions (Explicitly Postponed)
- **Repository Architecture**: Whether to create `rtt-agency` or maintain personas within `skills`.
- **Persona Packaging**: Whether all 5 roles warrant dedicated personas or should be structured execution stages.
- **Automated Verification Standard**: What standard browser test suite should be mandated across all projects.

---

## 8. Evidence Gap Analysis (Audited Limitations)

During the pre-experiment inspection, the following gaps and limits were identified:
1. **Cloudflare Pages Production Parity**: Local testing occurs via `vp dev` / `vp preview`. Behavior under actual Cloudflare Pages edge runtime routing was not tested during baseline inspection.
2. **Gitea Issue Detail for Roster**: In `armonia-dashboard#1`, the workshop roster is mentioned in a single summary line without detailed UX wireframes. This confirms that the specification must be authored in Phase 2 before implementation can proceed.
3. **Pragmatic Test-Data Setup**: While `armonia-api` lacks a standalone CLI seed script, it possesses existing initialization logic (`init_schema_and_seed()`) and proven integration test helpers (`_book()`). To avoid turning test preparation into an unplanned infrastructure project, the Verification Packet will reuse these existing routines to instantiate a disposable local SQLite test database with known workshop attendees.
