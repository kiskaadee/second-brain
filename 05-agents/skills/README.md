---
type: agent
status: active
name: skill-collection-index
kind: skill
project: brain
tags:
  - skills
  - agent-engineering
  - system-architecture
---

# Global Skill Collection

> **The authoritative source of truth for all agent skills has been consolidated into the standalone [`skills`](https://github.com/kiskaadee/skills) repository.**

---

## Repository & Installation

Skills are maintained, versioned, and tested in [`kiskaadee/skills`](https://github.com/kiskaadee/skills).

They are installed into runtime agent configurations via the repository's `install.sh` script:

```bash
cd ~/Projects/active/skills
./install.sh
```

---

## Active Skills Index

### Portable Skills

- **[`practice`](https://github.com/kiskaadee/skills/blob/main/skills/practice/SKILL.md)**: Socratic tutoring mode where the learner writes all code and drives analysis.
- **[`diagnose`](https://github.com/kiskaadee/skills/blob/main/skills/diagnose/SKILL.md)**: Empirical troubleshooting following the scientific method and 6-part checkpoints.
- **[`git-commit`](https://github.com/kiskaadee/skills/blob/main/skills/git-commit/SKILL.md)**: History hygiene, atomic slicing, and Conventional Commit construction.
- **[`document`](https://github.com/kiskaadee/skills/blob/main/skills/document/SKILL.md)**: Second-order knowledge classifier for Discussions, ADRs, Plans, Debug Records, and Knowledge Articles.
- **[`build-skill`](https://github.com/kiskaadee/skills/blob/main/skills/build-skill/SKILL.md)**: Interactive skill design, sizing, authoring, and empirical dogfooding.

### Brain Extensions

- **[`inbox-curation`](https://github.com/kiskaadee/skills/blob/main/brain/inbox-curation/SKILL.md)**: Triages, classifies, formats, and validates incoming drafts from `00-inbox/` into canonical lifecycle directories.
- **[`commit-logger`](https://github.com/kiskaadee/skills/blob/main/brain/commit-logger/SKILL.md)**: Immutable event capture script logging Git commits into `00-inbox/commit-log.csv` (planned consumer of future `journal-builder`).
