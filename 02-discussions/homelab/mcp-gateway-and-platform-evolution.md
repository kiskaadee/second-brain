---
type: discussion
status: open
project: homelab
date: 2026-10-21
tags:
  - homelab
  - mcp
  - architecture
  - gitops
  - orchestration
  - state-management
---

# Architectural Discussion: MCP Tool Gateway, State Boundaries, and Homelab Governance Evolution

## 1. Problem Statement & Historical Context

Platform orchestration for the homelab appliance (`roadtotech.me`) has historically centered around a bespoke command-line interface (`appctl`), declarative workload manifests (`app.yaml`), and manual or script-driven agent interactions. As AI-assisted development and operations became central to the workstation workflow, earlier planning explored creating specialized deployment-authoring AI agents to bridge natural language requests with homelab operational state.

During operational mitigation work on dynamic DNS infrastructure, an inspection of Hostinger's MCP (Model Context Protocol) integration revealed an alternative design pattern: exposing platform management capabilities through a standardized, protocol-level MCP server rather than encapsulating operational knowledge inside customized, monolithic AI agents.

Simultaneously, practical experience with cross-repository governance in the *Armonía del Ser* project (leveraging an organizational `.profile` repository for centralized documentation, cross-referencing milestones, and issue tracking) surfaced questions about whether the homelab appliance should evolve toward a similar multi-repository organizational structure, adopt an operational database alongside or in place of `app.yaml`, and rebrand away from the generic "Homelab" moniker.

Because the active architecture consolidation roadmap is fixed, this discussion explores the trade-offs, conceptual boundaries, and architectural implications of these ideas to preserve the reasoning without disrupting immediate operational priorities.

---

## 2. Context & Analysis: Core Dilemmas

### A. Dedicated Deployment Agent vs. Standardized Protocol Gateway (MCP)

A common design instinct in AI tooling is to build dedicated, domain-specific autonomous agents (prompt harnesses, memory stores, and custom agent loops). However, this introduces substantial architectural coupling:

1. **Model Lock-In**: The orchestration system becomes tied to specific agent frameworks or model APIs. If a new or more capable model arrives (e.g., local models via Ollama, Claude Code, Antigravity, or Cursor), the custom agent must be re-engineered.
2. **Loss of Determinism**: When an agent directly writes deployment scripts or runs arbitrary SSH commands, operational safety invariants become difficult to enforce consistently.

An **MCP Gateway** shifts the boundary:
* `appctl` remains the deterministic, testable Python engine enforcing schemas, execution policies, and system-level boundaries.
* The MCP server serves strictly as a protocol adapter exposing structured tools (`appctl_status`, `appctl_logs`, `appctl_audit`, `appctl_verify_workload`) over JSON-RPC.
* The model/client layer remains completely decoupled: the developer selects whichever AI assistant or model they prefer, while the MCP server enforces schema validation and tool boundaries.

```
+-------------------------------------------------------------+
|               Client & Model Layer (Decoupled)              |
|   (Antigravity IDE / Claude Code / Cursor / Local LLM)      |
+------------------------------+------------------------------+
                               | Model Context Protocol (JSON-RPC)
+------------------------------v------------------------------+
|                     Homelab MCP Server                      |
|      (Tool Definitions, Resource Providers, Schema Guards)  |
+------------------------------+------------------------------+
                               | Local invocation
+------------------------------v------------------------------+
|                    Platform Engine (appctl)                 |
|       (Validation, Manifest Parser, Compose Orchestration)  |
+------------------------------+------------------------------+
                               | Runtime operations
+------------------------------v------------------------------+
|                    Appliance Runtime Host                   |
|              (Docker Engine, Traefik, NixOS Core)           |
+-------------------------------------------------------------+
```

### B. Declarative GitOps (`app.yaml`) vs. Operational Database

Earlier discussions considered whether to replace workload `app.yaml` files with a centralized database (such as SQLite, PostgreSQL, or Turso). Evaluating this requires distinguishing between two fundamentally different types of state:

1. **Desired State (What the system *should* be)**:
   * Attributes: Subdomains, container images, port exposures, Traefik middleware requirements, branch policies.
   * *Best suited for Git*: Git provides immutable commit history, line-by-line attribution (`git blame`), branch isolation, pull-request reviewability, and effortless rollback via `git revert`. Moving desired state into a database forfeits native GitOps workflows and offline local reproducibility.
2. **Observed & Telemetry State (What the system *currently is*)**:
   * Attributes: Deployment run timestamps, exit codes, health check latency, uptime metrics, error logs, audit trail of which user or agent invoked actions.
   * *Best suited for a Database*: Querying across twenty workload YAML files to answer historical questions ("When did SnappyMail last deploy?", "Which workloads failed health checks this week?") is awkward in Git. A lightweight SQLite or LibSQL store on `Core` provides relational indexing and rapid querying for status dashboards or `appctl list` caching without compromising declarative Git invariants.

---

## 3. Evaluated Dilemmas & Rejected Alternatives

### Option 1: Autonomous Deployment AI Agent
* **Attempted Purpose**: Automate end-to-end workload provisioning and deployment drafting via a dedicated LLM agent.
* **Friction & Failure Mode**: Bypasses the operational safety boundaries established in the platform guidelines (which mandate human ownership of production deployments and atomic commit proposals). Custom agent frameworks also require constant maintenance as LLM interfaces evolve.
* **Trade-off Rationale**: Set aside in favor of a standard MCP server wrapping deterministic `appctl` verbs. The MCP protocol natively supports tool confirmation and schema validation, preserving human approval boundaries while remaining client-agnostic.

### Option 2: Replacing `app.yaml` Entirely with a Central Application Database
* **Attempted Purpose**: Provide a single CRUD API for all application metadata, eliminating manual YAML editing and synchronization scripts.
* **Friction & Failure Mode**: Breaks GitOps invariants. When an outage occurs or a bad configuration deploys, rolling back requires database rollbacks or transaction replays rather than standard Git operations. It also prevents developers from validating configurations locally in isolated Git branches before touching production.
* **Trade-off Rationale**: Rejected for desired state. Retained solely as a prospective approach for *observed runtime telemetry* (deployment history, health metrics, and audit logging).

### Option 3: Monolithic Appliance Repository vs. Multi-Repo Governance with `.profile`
* **Attempted Purpose**: Keeping all workloads and Core configurations tightly coupled in a single repository tree.
* **Friction & Failure Mode**: Shared commit histories blur ownership, increase CI trigger noise, and complicate cross-project roadmapping. 
* **Trade-off Rationale**: The organizational pattern validated in *Armonía del Ser*—using a top-level `.profile` repository for global architecture, roadmaps, and cross-cutting milestones alongside dedicated repositories for workloads—offers clean domain isolation while retaining unified platform visibility.

---

## 4. What Became Possible After the Architectural Separation

| Dimension | Monolithic / Agent-Centric Model | Decoupled MCP & Tiered State Model |
| :--- | :--- | :--- |
| **Model Portability** | Coupled to bespoke agent code and prompt templates. | Client-agnostic: any MCP-compatible agent interacts via standard JSON-RPC tools. |
| **Operational Safety** | Agent executes ad-hoc commands or shell scripts. | Agent invokes strictly typed `appctl` tools with predictable failure modes and approval prompts. |
| **Desired State Authority** | Risk of split-brain between database records and Git files. | Git remains the sole authority for desired state (`app.yaml` + Compose). |
| **Telemetry & Auditing** | Grepping decentralized logs across containers. | Optional operational SQLite database records deployment events and health telemetry. |
| **Platform Governance** | Single repo tracking disparate concerns. | Organization structure with `.profile` meta-repo coordinating independent workload repos. |

### Rebranding Opportunities
The generic name "Homelab" reflects a hardware/hobbyist categorization rather than the platform's actual identity as a personal edge application cloud. Potential directions include:
* **Avian / Biological Heritage**: Drawing from the *Great Kiskadee* (`kiskaadee`):
  * **Pitangus**: The scientific genus (*Pitangus sulphuratus*); distinct, technical, and grounded.
  * **Benteveo**: Regional vernacular for the Kiskadee; phonetically punchy.
  * **Tyran**: Rooted in the Tyrannidae family, representing agile, territorial adaptability.
* **Platform & Journey Focus**:
  * **RoadToTech Platform (RTT-Core)**: Direct alignment with the public appliance domain (`roadtotech.me`).
  * **Waypoint / Odyssey**: Reflecting the long-term career transition journey from biological science to software engineering.

### Feasibility: Gitea Organization to GitHub Migration
An architectural evaluation of moving from self-hosted Gitea to GitHub organizations reveals clear delineations:
* **Code, Commits, Branches, and Tags**: *Lossless and trivial*. Git's decentralized design allows full-mirror pushes (`git push --mirror`) in minutes without history loss.
* **CI/CD Workflows**: *Minimal friction*. Gitea Actions (`act_runner`) syntax mirrors GitHub Actions. Workflows migrate directly with minor adjustments for runner environments (`ubuntu-latest` vs self-hosted).
* **Issues, Discussions, and Pull Request Metadata**: *Moderate friction*. Requires API-based migration scripting if historical issue threads must be transferred, or adopting a pragmatic cutover where Gitea remains an immutable historical archive while new milestones commence on GitHub.

---

## 5. Convergence & Successors

The exploration converged on the following conceptual model:
1. **Tooling**: Wrap `appctl` capabilities into a standard MCP server rather than building a custom deployment agent. This delegates model and interface choices to developer preference while keeping the operational core deterministic and safe.
2. **State**: Preserve `app.yaml` in Git for desired state (GitOps). Confine any future database adoption to operational telemetry, execution history, and status caching.
3. **Structure**: Adopt the `.profile` meta-repository pattern within a dedicated organization when repository separation occurs, accompanied by an intentional platform rebrand.

**Succession Path**:
* **Current State**: Parked. Active execution remains strictly focused on the current consolidation roadmap and DNS/infrastructure stability.
* **Successor Artifacts**: When the roadmap reaches the appropriate milestone, this discussion will inform:
  * An Architectural Decision Record (ADR) specifying the Homelab MCP server specification and schema contract.
  * A Platform Rebranding & Repository Migration Plan.
