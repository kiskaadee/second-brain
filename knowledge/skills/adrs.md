# Quick Guide to Architecture Decision Records (ADRs)

Without the proper documentation, the critical reasons _why_ a system was built a certain way exist only in developers' heads, chat histories, or forgotten meeting notes. As a software project grows, a development team will eventually stare at a piece of code, a database schema, or an infrastructure choice and ask themselves: _"Why on earth did we build it this way?"_

Imagine joining a team and discovering that the application uses three different caching layers, or that a perfectly good relational database was swapped out for a NoSQL document store that doesn't quite fit the current data model.

Naturally, the first question is: _"Who made this decision, and what were they thinking?"_

## Why You Must Start Tracking ADRs on Day 1

The biggest mistake teams make is waiting until a codebase feels "complex enough" to warrant documentation. By then, it is already too late. You must establish ADRs at the very beginning of a software project for three critical reasons:

- **The Velocity Trap**: Early-stage projects move fast. Decisions made over a casual lunch or a quick Slack message form the foundation of your entire system. Without ADRs, that foundational context is lost in weeks, not years.
- **Compound Technical Debt**: Early mistakes are cheap to fix but expensive to change later. Documenting decisions early forces the founding team to explicitly state their assumptions before building a fragile foundation.
- **Seamless Scaling**: When the project grows and you hire your first wave of new developers, you will not waste dozens of hours in onboarding meetings. The ADR log acts as a historical archive that brings them up to speed instantly.

## The First Solution Most Teams Try

When developers try to understand the history or architecture of a system, they usually rely on two flawed approaches:

1. **Tribal Knowledge**: You track down the most senior engineer and ask them. They explain that three years ago, there was a specific scaling constraint that forced the NoSQL migration. If that engineer leaves the company, the knowledge evaporates.
2. **The Mega-Document**: The team tries to maintain a massive "Architecture.docx" or a sprawling wiki page. Because it is disconnected from the codebase and requires significant effort to update, it rots. It usually describes a system that existed two years ago, not the system running today.

What if you could capture the _context_ of a decision at the exact moment it was made, and store it right next to the code it affects?

## Meeting the ADR

An Architecture Decision Record (ADR) is a short text file that captures a single, architecturally significant decision, along with its context and consequences. As defined by the [adr.github.io](https://adr.github.io/) community, it is a justified design choice addressing a functional or non-functional requirement.

Instead of writing a book about your architecture, you write a sequence of short logs.

A typical ADR lives directly in your source code repository (e.g., inside a `docs/adr/` folder) as a plain Markdown file. It is version-controlled, reviewed via Pull Requests, and highly accessible to developers exactly where they work.

## The Anatomy of an ADR

While there are multiple templates (such as MADR or Y-Statements), the original format proposed by Michael Nygard remains the most widely used due to its simplicity. A standard ADR contains five sections:

1. Title  
A short noun phrase with a number.  
_Example: `ADR 004: Use Redis for Session Storage`_

2. Status  
What is the current state of this decision? Common states are _Proposed, Accepted, Deprecated,_ or _Superseded_.  
Crucially, if ADR 004 is replaced by ADR 012 two years later, you do not delete ADR 004. You simply change its status to _Superseded by ADR 012_.

3. Context  
What is the problem? What forces are at play? This is the most important section. You must describe the technological, political, or business constraints that exist _today_.

4. Decision  
What is the actual choice you are making? Be direct and active.

5. Consequences  
What happens next? Every architectural decision is a trade-off. Document the good, the bad, and the neutral impacts.

---

## Anatomy of a _Good_ ADR vs. a _Bad_ ADR

An ADR is only useful if it contains meaningful data. Many teams write poor ADRs that fail to capture the true engineering trade-offs.

Here is how to ensure your ADRs are high quality:

## 1. The Context Section

- 🛑 Bad: _"We need a database for user sessions because Postgres is too slow."_ (Vague, lacks data, emotional).
- Good: _"Our current Postgres database is hitting connection limits (averaging 95% capacity) during peak traffic. We need a distributed session store. Constraints: We have zero budget for enterprise cloud tools and a hard launch deadline in two weeks."_

## 2. The Decision Section

- 🛑 Bad: _"We will look into using NoSQL solutions like Redis or Mongo."_ (Wishy-washy, passive, not an actual decision).
- Good: _"We will extract session management from Postgres and implement an open-source, self-hosted Redis cluster."_

## 3. The Consequences Section

- 🛑 Bad: _"Everything will run faster and the system will be better."_ (Unrealistic, ignores the inevitable downsides of engineering choices).
- Good:
- _"Good: Postgres connection load decreases immediately by an estimated 40%."_
- _"Bad: We now introduce a new infrastructure component that requires custom monitoring and alerting templates."_
- _"Neutral: Developers must learn basic Redis CLI commands for local debugging."_

---

## Why are they so powerful?

When you read an ADR, you are not just reading what was built; you are reading _why_ it was built that way, based on the reality of that specific moment in time.

If a new engineer looks at the Redis decision three years later—when the company has a massive budget—and asks, "Why didn't they just use a managed enterprise database?", the ADR provides the defense. It proves the decision was not made out of ignorance, but out of strict budget and time constraints.

By keeping ADRs as lightweight Markdown files in the Git repository:

- They are naturally versioned alongside the code they affect.
- They integrate smoothly into the standard code review (PR) process.
- They do not require context-switching to an external wiki.
- They form an immutable, append-only "decision log" of the system's evolution.

## When should I write an ADR?

You do not need an ADR for every minor library update or trivial refactor. You write one when a decision is architecturally significant.

Before writing an ADR, ask yourself:

- Does this affect non-functional requirements? (Security, scalability, performance, availability).
- Is this hard to reverse? Swapping a sorting algorithm is easy. Swapping a core database or changing the API protocol from REST to gRPC is expensive and painful.
- Will another developer ask "why" in six months? If a choice seems counter-intuitive but is necessary due to a strange business constraint, you must document it.

## The Mental Picture

Think of an ADR log like a ship's logbook.

A captain does not write a massive, predictive manual of the entire voyage before leaving the port. Instead, they write short, chronological entries:

_"Day 14: Encountered severe storm from the north. Decided to reroute south to avoid structural damage. Consequence: Arrival will be delayed by two days, but the cargo remains safe."_

If the ship arrives late, the owners do not have to guess why. The context, the decision, and the trade-offs are permanently recorded.

## One Principle to Remember

When writing an ADR, your goal is not to prove that you made the perfect choice. Your goal is to prove that you made a rational choice given the constraints you faced.

Whenever you make a structural change that involves a significant trade-off, pause and ask:

_"If I leave the company tomorrow, will the next engineer understand why we accepted this trade-off?"_

If the answer is no, it is time to write an ADR.

---

## References

- Architectural Decision Records (ADRs) Community Page [1]
- [Documenting Architecture Decisions - Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
