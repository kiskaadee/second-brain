---
type: knowledge
status: stable
topics:
  - engineering-practices
  - troubleshooting
  - scientific-method
  - incident-investigation
  - observability
tags:
  - methods
  - operations
  - postmortem
  - root-cause-analysis
---

# Scientific Incident Investigation & Epistemic Journaling

This document establishes the canonical engineering methodology for investigating complex system failures and authoring durable, reproducible incident journals.

---

## 1. Epistemological Foundation: Investigation as Science

In complex distributed systems, post-incident documentation often suffers from two opposing failure modes:
1. **The Superficial Summary**: Merely recording the declarative fix without explaining how the failure was diagnosed, which teaches the reader almost nothing about system behavior.
2. **The Fictionalized Postmortem (Hindsight Bias)**: Reconstructing the investigation as a neat, linear narrative that pretends the root cause was obvious from the beginning.

The **Epistemic Investigation Method** treats system troubleshooting as an empirical scientific inquiry. Its goal is to preserve and communicate the **reasoning process** used to narrow down an unfamiliar failure, transforming an operational outage into durable engineering intuition.

```
       ┌─────────────────────────────────────────────────────────┐
       │                   1. Raw Observations                   │
       │           (Terminal dumps, logs, error codes)           │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                 2. Diagnostic Inquiries                 │
       │       (What questions narrow down the failure space?)    │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                3. Hypothesis Formulation                │
       │    (What causal models could produce these symptoms?)   │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                4. Discriminating Tests                  │
       │     (Commands designed to falsify specific hypotheses)  │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │              5. Root Cause Demonstration                │
       │       (Connecting proven evidence to mechanism)         │
       └────────────────────────────┬────────────────────────────┘
                                    │
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │          6. Generalization & Transferable Rules         │
       │      (Abstracting architectural and diagnostic heuristics)│
       └─────────────────────────────────────────────────────────┘
```

---

## 2. Core Epistemic Principles

### A. Observation vs. Inference
A fundamental discipline of scientific investigation is strictly separating raw evidence from deductive interpretations:

* **Observation (Machine Output)**: What the system literally produced (e.g. `webhook logged: Signature mismatch`, `status code 403`, `db column secret was ""`).
* **Inference (Mental Model)**: What the operator deduced from the observation (e.g. *"The verification digest calculated locally differed from the signature sent by Gitea"*).
* **Hypothesis (Causal Candidate)**: A plausible mechanism explaining the inference (e.g. *"The intermediate webhook daemon modified the body bytes during parameter extraction"*).

### B. Discriminating Tests & Command Rationale
Never present terminal commands as unexplained recipes. Every diagnostic step must answer:
1. **Target Layer**: What component or boundary does this command inspect?
2. **Rationale**: Why is this inspection relevant to the active hypothesis?
3. **Falsification Criteria**: What specific observation would **support** the hypothesis, and what would **refute** it?

### C. Anti-Hindsight Bias (Chronological Integrity)
Investigations in real systems rarely proceed in a straight line. They branch, hit dead ends, revisit earlier questions, or discover new phenomena midway through.
* Preserve the transitions where evidence shifted attention.
* If a crucial causal insight was discovered only retrospectively after fixing the issue, **explicitly label it as retrospective analysis**. Do not present it as if it guided the initial investigation.

### D. Transferable Diagnostic Knowledge vs. Literal Replication
While exact commands are useful for auditability, the primary value of an incident journal is **transferable diagnostic intuition**:
* *Literal Replication*: "Run `docker exec gitea sqlite3 ...`"
* *Transferable Heuristic*: "When an authenticated webhook fails at the receiver, verify configuration and secret synchronization at both protocol endpoints before diagnosing payload corruption."

### E. Proportionality
Scale investigative depth to the actual learning value of the incident:
* For a simple typosquat or routine restart, keep the entry concise and focused.
* For subtle protocol discrepancies, serialization bugs, race conditions, or cryptographic failures, provide full deep-dive rigor.
* Never manufacture artificial hypotheses or boilerplate purely to satisfy a template.

### F. Source Attribution for Protocol Contracts
Never rely on remembered behavior for protocol specifications, container entrypoints, or framework internals. Explicitly cite the canonical source (e.g. *"According to Gitea's webhook implementation..."*, *"Per RFC 2104 (HMAC)..."*).

### G. Safe Credential Verification Without Secret Leakage
When verifying whether two endpoints possess matching credentials, never log raw or truncated secrets. Instead, document cryptographic proof (e.g., comparing SHA-256 digests of the credentials in memory) or safe boolean assertions.

---

## 3. Modular Investigation Structure

When authoring an incident journal (`Brain/records/journal/YYYY-MM-DD-<slug>.md`), apply the following modular sections as appropriate:

### 1. System Context & Fundamentals
* Establish the specific role of the affected subsystem.
* Diagram component boundaries, data flow, and security/protocol contracts with source citations.
* Reference canonical documentation (avoid copying static architectural overviews).

### 2. Problem & Observations
* State expected behavior vs. actual behavior.
* Provide verbatim error snippets, exit statuses, and terminal states.
* Clearly isolate raw facts before offering any interpretations.

### 3. Diagnostic Inquiries
* Formulate the evolving questions that organize the investigation.

### 4. Investigation & Hypothesis Testing
* Walk through each meaningful investigative inquiry:
  * **Rationale**: Why this path was explored.
  * **Inspection**: The commands or queries executed.
  * **Prediction**: What results were expected under candidate hypotheses.
  * **Observed Evidence**: What the system actually returned.
  * **Outcome**: Whether the working hypothesis was supported, refuted, or refined.

### 5. Findings & Root Cause Analysis
* Synthesize the validated evidence.
* Detail the exact physical or logical causal chain (e.g. how data structures, memory, networks, or serializers behaved under the hood).
* Explicitly distinguish between evidence proven during triage and insights discovered via retrospective analysis.

### 6. Declarative Remediation & Local Validation
* Present the minimal declarative configuration change.
* Document local verification commands (unit tests, flake checks, compose validations).

### 7. Deployment & Recovery Runbook
* Document production deployment steps.
* If deployment requires privileged operations (such as `sudo nixos-rebuild switch`), explicitly label the operational privileges and provide the operator runbook.
* Provide concrete post-deployment verification proving that the service recovered under real operating conditions.

### 8. Discussion & Generalization
* **Architectural Takeaways**: Design flaws or implicit assumptions exposed by the incident.
* **Transferable Diagnostic Rules**: General heuristics that apply to future troubleshooting across other domains (avoiding overgeneralization).
* **Preventative Measures**: Systemic hardening or monitoring improvements.

### 9. References
* Code pointers, forge commit links, external RFCs, and upstream issue trackers.

---

## 4. Epistemic & Evidence Self-Audit Checklist

Before finalizing an incident journal, execute the following 7-point audit:

1. **Epistemic Classification**: Is every substantive statement clearly categorized as an *observation*, *inference*, *hypothesis*, or *conclusion*?
2. **Evidence Demonstration**: Does the journal *demonstrate* the causal mechanism with concrete evidence rather than merely asserting it?
3. **Auditability**: Is the supporting evidence actually shown in the record rather than assumed?
4. **Chronological Integrity**: Is historical investigation reasoning distinguished from retrospective reconstruction?
5. **Proportional Claims**: Does the conclusion claim only what the evidence strictly establishes without overreaching?
6. **Sound Generalization**: Are local lessons generalized safely (avoiding absolute claims like *"it is always X"* when other failure modes exist)?
7. **Transferability**: Could an unfamiliar engineer apply the diagnostic reasoning to a dissimilar problem without already knowing the solution?
