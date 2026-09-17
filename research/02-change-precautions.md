# Research: Change Precautions and Blast Radius

Background for `change-precautions`, `production-change-guard`, and Section 4 of `safe-change-engineering`.

## 1. Blast radius

The term entered engineering mainstream via tools like GitHub's blast-radius (visualization of Terraform change impact) and Google's internal change-risk tooling (Critique/Tricorder data showing review quality correlates with change size and coupled concerns). The concept: **every change has an impact set, and the cost of a change is dominated by the size of that set, not by the difficulty of writing the code.**

For an AI agent, blast radius analysis is mechanical:

1. Grep the symbol across code, tests, config, scripts, CI, docs.
2. Include string/dynamic references - reflection, DI registration, event names, raw SQL, templates. Static analyzers miss these; greps catch the obvious ones; only discipline catches the habit.
3. Classify the change (internal / additive / signature / behavior / removal) - each class has a required action.
4. Treat boundary crossings (exported API, schema, wire formats, CLI flags) as contract changes requiring consumer enumeration.

The classification table in the skill is deliberately small. A taxonomy an agent won't apply is worthless.

## 2. Read-before-write

The single most common agent-caused defect is the **phantom edit**: writing what the model *believes* is at a location rather than what is there. Causes: never read the file; read it but the session has drifted; read a different file with a similar name. The fix is procedural, not clever: never edit unread regions, skim dependencies before editing, re-read the target region right before the edit if the read is stale. Every serious agent harness enforces variants of this; the skill makes it the agent's own rule rather than the harness's fallback.

## 3. Minimal diffs and review gravity

Code review research (e.g., SmartBear/Cisco studies popularized in *Best Kept Secrets of Peer Code Review*) converges on: review effectiveness falls sharply as diff size grows; beyond ~200-400 lines, defects are missed at high rates. Small diffs are not aesthetic preference - they are the mechanism by which humans (and the model itself, during diff self-review) can actually verify the change.

Corollaries encoded in the skills:

- **One intent per diff.** Mixed-intent diffs (fix + refactor + format) defeat bisection and make reverts blunt instruments.
- **No drive-by changes.** "While I'm here" hunks are unreviewable scope creep wearing a helpful face.
- **Report adjacent bugs, don't fix them.** The agent's context advantage (it just read the neighborhood) is best spent flagging, not expanding scope.

## 4. Conventions as load-bearing structure

A codebase's conventions encode decisions - often expensive ones. Agents that "improve" structure create orphan patterns: one file modernized in a codebase that doesn't use the new idiom, a class hierarchy introduced where functions reign. The result is a codebase with two systems and no owner for either. Hence **convention lock**: local law beats global taste. The escape hatch (flag genuine hazards, propose, don't silently deviate) exists because some local patterns are load-bearing bugs.

## 5. Chesterton's fence

From G.K. Chesterton's 1929 formulation: a reformer who doesn't understand why a fence exists has no standing to remove it. In code: the pointless-looking check, the duplicated function, the 30-second sleep before retry - these usually encode an incident. `git blame` and commit messages are the archaeology tools; tests are the fossil record. The legacy skill's rule - know why before removing - is Chesterton's fence operationalized.

## 6. Migrations: expand-contract

The dominant pattern for safe schema/contract evolution (formalized in the DB community as "parallel change"; popularized in web engineering by Brandur Leach's *Expand/Contract Pattern* and documented by Stripe and PlanetScale engineering blogs):

1. **Expand** - add the new structure alongside the old; both valid.
2. **Migrate** - backfill/dual-write; verify parity.
3. **Switch** - move reads; verify behavior.
4. **Contract** - remove the old structure later, separately.

Properties: every step deploys independently, rolls back independently, and never couples a destructive step with an additive one. The production skill adds operational mechanics: idempotent, resumable, batched backfills; never long-locking live tables; immutable applied migrations.

The pattern generalizes beyond SQL: API payloads, config formats, event schemas, and file formats all follow the same physics - you cannot atomically swap a contract that consumers read at uncontrolled times.

## 7. Reversibility and one-way doors

Amazon's one-way/two-way door framing is the right decision lens for agents: most code changes are two-way doors (revert the deploy), while schema drops, history rewrites, deleted buckets, and leaked secrets are one-way doors. An agent has no intuitive sense of which door it's pushing on - the skill makes it state the rollback path before starting and hard-stops at one-way doors for explicit confirmation.

## 8. Protected files

Hand-editing derived state is a category error: lockfiles, generated stubs, built assets, and vendored code are *outputs* of processes. Editing them desynchronizes the process: the next regeneration silently reverts the fix, or worse, bakes the hand-patch into tool assumptions. The rule - regenerate, never hand-edit - is universally applicable and cheap to check.

## References

- Brandur Leach, *The Expand/Contract Pattern* (brandur.org/expand-contract).
- PlanetScale, *How to do zero-downtime database migrations* (expand-contract in practice).
- Fowler, *Strangler Fig Application* (martinfowler.com) - the incremental-migration sibling used by the refactor skill.
- Feathers, *Working Effectively with Legacy Code* (2004) - characterization tests, seams.
- SmartBear, *Best Kept Secrets of Peer Code Review* (review size vs defect detection).
- Chesterton, *The Thing* (1929), the fence.
