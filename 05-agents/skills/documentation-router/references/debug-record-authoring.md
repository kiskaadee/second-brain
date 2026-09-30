# Debug Record Authoring Specification

## Epistemic Role & Core Purpose

A **Debug Record** is a durable **historical investigation / RCA record**. It documents the empirical diagnosis and root-cause determination of bugs, regressions, system anomalies, failed migrations, configuration errors, or unexpected runtime behaviors. It answers:
> *"What empirically broke, how did the investigation diagnose it, and what was the root cause?"*

A debug record preserves institutional memory: how an obscure failure was uncovered, which hypotheses were eliminated, what the causal mechanism was, and what operational heuristics prevent recurrence.

---

## 1. Epistemic Invariants & Boundaries

1. **Empirical & Evidence-Based**:
   Ground all statements in verifiable observations. Include raw error messages, exit codes, or log snippets.
2. **Strictly Separate Observation from Inference**:
   Clearly demarcate what the system reported (raw fact) from what the investigator inferred or hypothesized.
3. **Document Diagnostic Rationale**:
   Explain why diagnostic inspection commands were run and what each command was intended to confirm or refute.
4. **No Hindsight Bias**:
   Present the actual reasoning progression. Do not manufacture a tidy, linear narrative that erases reasonable working hypotheses eliminated during the investigation.
5. **Declarative Remediation & Parity**:
   Document the minimal, isolated, and reversible fix applied, along with validation commands proving recovery.
6. **Zero Secret Leakage**:
   Never include real passwords, API tokens, HMAC keys, or session secrets. Use redacted placeholders.
7. **Scope**:
   Not restricted to production outages. Applies to any non-obvious engineering anomaly across development, CI, testing, and operations where the diagnostic reasoning carries durable learning value.

---

## 2. Standard Document Structure

```markdown
---
type: debug
date: YYYY-MM-DD
project: <project-name>
tags: [operations, troubleshooting, debugging, <subsystems>]
---

# <Descriptive Incident / RCA Title>

## 1. System Context & Fundamentals
* Relevant components, data flow, architecture layer, and operational expectations.

## 2. Problem & Observations
* Observed symptoms vs. expected behavior.
* Raw error logs, stack traces, and failure manifestation (facts separated from interpretation).

## 3. Diagnostic Inquiries & Hypotheses
* Guiding questions formulated to narrow down the failure domain.
* Initial working hypotheses and plausibility mechanisms.

## 4. Investigation & Hypothesis Testing Log
* Reasoning progression: Working Hypothesis $\to$ Diagnostic Command $\to$ Evidence (Expected vs. Actual) $\to$ Outcome (Confirmed or Eliminated).

## 5. Root Cause Analysis
* Synthesis of proven evidence and explanation of the underlying causal mechanism.

## 6. Declarative Remediation & Local Validation
* Minimal, declarative fix applied.
* Test execution, validation checks, and output proving resolution.

## 7. Deployment & Recovery Runbook
* Production rollout steps, rollback instructions, and runtime health verification.

## 8. Discussion & Transferable Learnings
* Architectural takeaways or false assumptions dispelled.
* Transferable diagnostic heuristics and preventative measures.

## 9. References
* Links to affected manifests, commits, pull requests, or protocol specifications.
```
