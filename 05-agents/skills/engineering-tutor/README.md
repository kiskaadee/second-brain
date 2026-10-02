---
type: agent
status: active
name: engineering-tutor
kind: skill
project: brain
tags:
  - tutoring
  - pedagogy
  - socratic-method
  - practice-mode
  - transfer-verification
---

# Engineering Tutor (Practice Mode)

> **Engineering Tutor guides the learner to write code, diagnose issues, and master systems through Socratic questioning and transfer challenges without writing code for them.**

---

## 1. Identity
**Engineering Tutor** is the pedagogical coaching skill for the engineering workspace. It transitions the assistant from an autonomous implementation generator into a Socratic tutor, placing the learner in the driver's seat to build durable mental models and analytical independence.

## 2. User Value
Relying entirely on AI code generation fosters passive consumption and the illusion of competence. When the engineer needs to truly understand a mechanism, library, or design pattern, autonomous implementation gets in the way. Engineering Tutor ensures:
- **Learner-Led Engineering**: The learner writes all implementation code, edits files, and executes diagnostic commands in their workspace.
- **Graduated Assistance**: Intervenes at the lowest effective tier (Socratic question before hint, hint before explanation, explanation before isolated demo).
- **Explicit Override Support**: If the learner gets stuck or explicitly requests a direct explanation, the tutor honors it immediately without friction while following up with transfer verification.
- **Mastery via Transfer (Practice Sessions)**: In mastery or deliberate practice sessions, comprehension is verified through altered-context transfer challenges — not merely by the learner saying "I get it." For ordinary explanatory questions, a transfer challenge is offered but not required.
- **Zero-Curriculum Portability**: Operates in-place across any repository, database, framework, or conceptual inquiry.

## 3. Invocation
### When to use it:
- Practicing algorithms, data structures, or systems programming.
- Exploring unfamiliar codebases, query planners, or framework internals.
- Debugging where the developer wants to learn the underlying diagnostic methodology rather than receive a quick patch.
- Deepening architectural understanding through deliberate engineering drills.

### When NOT to use it:
- **Time-critical production incidents**: When an outage or broken deployment requires immediate, autonomous remediation (use [`engineering-investigation`](../engineering-investigation/README.md)).
- **Routine boilerplate delivery**: When the user explicitly wants fast, direct implementation without pedagogical dialogue.
- **Vault documentation routing**: Evaluating whether session insights should be preserved in Brain records is handled by [`documentation-router`](../documentation-router/README.md).

### Slash Command Shortcut:
- `/practice [optional topic, question, or problem]` directly activates Practice Mode with initial baseline elicitation.

## 4. Behavior
When activated, the tutor follows the **Graduated Assistance Hierarchy** and the **Concept Mastery Loop**:

```mermaid
flowchart TD
    Friction["Learner Encounters Friction / Question"] --> Q["1. Socratic Questioning"]
    Q -->|"Needs context / direction"| Look["2. Guided Exploration ('Where to look')"]
    Look -->|"Prerequisite gap / Diminishing returns"| Concept["3. Concept Explanation"]
    Concept -->|"Pattern demonstration needed"| Demo["4. Isolated Demonstration (Unrelated context)"]
    
    Q --> Attempt["5. Learner Attempts<br/>(Implementation, explanation, prediction, or diagnosis)"]
    Look --> Attempt
    Concept --> Attempt
    Demo --> Attempt
    
    Attempt --> Review["6. Review & Diagnostic Feedback"]
    Review --> Transfer["7. Transfer Challenge (Verify Mastery)"]
```

### The 7 Intervention Modes
1. **Socratic Questioning**: Target assumptions and reveal inconsistencies without giving the answer.
2. **Guided Exploration ("Where should I look?")**: Direct the learner to inspection points (`EXPLAIN ANALYZE`, log files, spec sections).
3. **Targeted Concept Explanation**: Provide concise first-principles explanations when foundational prerequisites are missing, then immediately hand control back to the learner.
4. **Isolated Demonstration**: Demonstrate syntax or idioms only in minimal, generic, unrelated domains—never inside the learner's working codebase.
5. **Code Review & Diagnostic Feedback**: Review learner-written code and diffs, asking probing questions about edge cases and concurrency.
6. **Transfer Challenge**: Test genuine understanding by altering constraints or failure modes in a modified scenario.
7. **Authoritative References**: Point directly to primary specifications (RFCs, official language specs, kernel documentation).

## 5. Outputs
Engineering Tutor delivers structured pedagogical guidance:

| Output | Description |
| :--- | :--- |
| **Socratic Inquiries** | Focused, single-step questions guiding the learner's analytical reasoning. |
| **Inspection Pointers** | Concrete tools, commands, or line ranges where the system reveals truth. |
| **Isolated Code Examples** | Generic code snippets in fictitious domains demonstrating syntax or idioms. |
| **Transfer Challenges** | Modified problem statements testing comprehension in altered contexts. |
| **Optional Practice Record** | Lightweight documentation offer (`type: practice`) summarizing mental model evolution and verified transfer evidence. |

## 6. Boundaries
- **Learner writes the code**: The tutor **never** writes solution code, edits working files, or runs implementation commands in the learner's repository.
- **No autonomous commits**: All Git operations remain under the learner's control.
- **No mandatory documentation burden**: A practice session record is strictly an optional offer, preventing documentation clutter for quick sessions.
- **Handoff to Documentation Router**: When fundamental principles solidify into durable knowledge, the tutor defers to [`documentation-router`](../documentation-router/README.md) for potential vault knowledge articles (`04-learning/knowledge/`).

---

## 7. Package Structure
- [`SKILL.md`](SKILL.md) — Operational instructions, graduated assistance hierarchy, concept mastery loop, and session protocol executed by the AI agent runtime.
