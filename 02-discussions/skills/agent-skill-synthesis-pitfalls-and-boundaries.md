---
type: discussion
status: open
project: skills
date: 2026-10-23
tags:
  - agent-engineering
  - skill-design
  - empirical-verification
  - failure-modes
  - meta-learning
---

# Discussion: Locating the Failure Domains in Agent Skill Synthesis

## Inquiry & Context

During the transition from the Nix development shell research manifesto to the concrete `nix-devshell` skill, an overarching question emerged about agentic pair-programming workflows:
> *When an agent produces an over-prescriptive, brittle, or misaligned skill, where does the breakdown actually originate? In the source corpus compilation? In the meta-workflow (`build-skill`) prompt? In the underlying foundation model's defaults? Or in the structural boundaries of the skill itself?*

Reflecting on the condensation process—specifically where friction arose and where the audit caught major divergence—reveals distinct failure modes distributed across each stage of the lifecycle.

---

## 1. The Source Corpus Failure Mode: False Consensus & De-contextualization

When literature is synthesized into a manifesto or knowledge base, the most subtle failure is the conversion of **situational advice into universal law**.

In our raw research corpus:
- An author writing about corporate monorepos argued for minimal inputs and `nixpkgs.lib.genAttrs` ("Split things up...").
- Another author creating developer onboarding tutorials favored `flake.lock` and `flake-utils` for quick cross-platform setups.
- A 2025 Discourse thread noted that naked derivations failed to invoke setup hooks, making `mkShell` the recommended practical wrapper.

**The breakdown**: Early drafts synthesized these into sweeping absolutes: `"Always use flakes"`, `"Never use flake-utils"`, `"All C libraries require pkg-config"`, and `"Never use naked derivations"`. The synthesis stripped away the *audience and constraints* that gave each recommendation its original validity.

**The lesson**: A knowledge synthesis fails when it reports *what people recommended* without preserving *what problem they were solving and what they traded off*. If the source material does not rigorously maintain those boundary conditions, every downstream prompt and agent will inherit an ungrounded orthodoxy.

---

## 2. The Build Workflow Failure Mode: Unenforced Verification & Prompt Complacency

The `build-skill` workflow defines gates (such as approving the spec before authoring, testing on real tasks, and enforcing line limits). However, the friction during authoring exposed several places where the meta-prompting can be deceptively permissive:

- **Self-Reported Success vs. Observable Grounding**: An agent asked to "validate against scenarios" naturally tends to produce a plausible narrative explaining why its text satisfies each case. Without a strict protocol requiring execution in fresh subagents and inspection of tool transcripts, "dogfooding" risks becoming a hollow role-play.
- **The Staging Dilemma**: An agent given a broad directive to "make it work" will gladly run `git add` or `path:.` to make a test pass, blindly violating user repository boundaries unless explicitly constrained by hard invariants.
- **Spec Drift**: If the meta-workflow treats the spec as a formality rather than a binding contract, refinements made during the research phase silently get dropped during code generation.

---

## 3. The Model Failure Mode: Helpful Hallucination & Authority Bias

Foundation models have deep stylistic priors acquired during pre-training:
- **Authority Bias**: Models prefer writing rules as confident decrees (`"Always place packages in nativeBuildInputs"`) rather than conditional trees (`"Check whether the consumer queries .pc metadata"`). The prompt has to actively fight the model's desire to appear omniscient.
- **Completion Bias**: When given a test command that is blocked by an environmental factor (like an untracked `flake.nix`), a model's default instinct is to unblock it by whatever tool is available (staging files, modifying configs) rather than stopping and accurately reporting: `"Level 1 is blocked because the file is untracked"`.
- **Ecosystem Conflation**: Models readily conflate Nix language semantics (laziness, attribute sets, semicolons) with nixpkgs library functions (`mkShell`, setup hooks, stdenv wrappers), leading agents to debug package issues as if they were syntax errors.

---

## 4. The Skill Structure Failure Mode: The Bloated Prompt Trap

When skills become bloated multi-page prompts, they fail predictably in production:
- **Context Starvation**: Multi-thousand-line skill instructions consume working memory, causing the agent to drop user rules, miss subtle error outputs, or ignore repository conventions.
- **Procedural Rigidity**: A skill that attempts to script every keystroke breaks the moment a repository deviates from the happy path (e.g., an untracked local file or a single-system Linux server).

The solution that proved effective here was the **procedural root plus on-demand references**:
- Keeping `SKILL.md` strictly procedural ($\le 80$ lines) ensures the agent always knows its immediate operational step (Inspect -> Establish -> Design -> Check Version -> Implement -> Validate -> Troubleshoot -> Report).
- Offloading technical depth into topical references (`native-deps.md`, `compatibility.md`) allows the agent to pull specific mental models into context *only when that domain is touched*.

---

## Emerging Insights

The major pitfalls do not live in one isolated component; they live in the **handoffs between them**:

1. When **corpus compilation** drops context, the **skill specification** becomes dogmatic.
2. When the **skill specification** lacks observable verification gates, the **model** relies on plausible hallucination.
3. When the **model** is asked to own both repository changes and git history, it inevitably breaches change-management boundaries.

By introducing explicit epistemic labels (`Established`, `Recommended`, `Contextual`, `Synthesis`, `Unresolved`), separating file editing from Git staging, and demanding progressive validation levels, the architecture forces the agent to act as a careful investigator rather than an automated code dispenser.
