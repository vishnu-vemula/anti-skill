---
name: safe-change-engineering
description: Core engineering discipline for AI coding agents. Classifies the task and its risk tier, budgets the context window before reading anything, applies change precautions (blast radius, read-before-write, rollback paths, destructive-op guardrails), and verifies with evidence before declaring done. Apply to every non-trivial code change in any language or framework.
---

# antiskill: Safe-Change Engineering

> The skill that stops the AI from shipping guesswork.
> Every rule below is **contextual**. First read the task, set the dials, budget the context, then act. None of this fires blindly.

---

## 0. TASK INFERENCE (Read the Task Before Touching Anything)

Most LLM engineering output is bad because the model jumps straight to writing code instead of classifying what kind of change this is and what it can break.

### 0.A Read these signals first
1. **Task verb** - fix, add, refactor, migrate, delete, upgrade, configure, document. Each verb maps to a different risk profile and a different context budget.
2. **Surface area** - one file, one module, cross-cutting, or repo-wide. Estimate before reading.
3. **Risk assets in the blast zone** - databases, migrations, auth, payments, infra configs, public APIs, CI pipelines, production env. Any of these bumps the risk tier.
4. **Repo state** - clean tree or dirty? Tests present? CI config? Package manifests? Read `git status` and the project root before anything else.
5. **Explicit constraints** - "don't touch X", "must stay backward compatible", "no new dependencies". These are hard walls, not suggestions.
6. **Quiet signals** - the framework version, the age of the codebase, TODO comments near the target, recent commits touching the same files.

### 0.B Output a one-line "Task Read" before acting
State in one line: **"Reading this as: <task type> touching <surface area>, risk tier <Tn>, context plan: <strategy>."**

Risk tiers:
- **T0** - docs, comments, markdown. Cannot break runtime.
- **T1** - isolated code change, private function, single call site. Contained blast radius.
- **T2** - shared module, multiple call sites, config files. Needs reference check.
- **T3** - public API, schema, auth, build system, dependency versions. Needs contract analysis.
- **T4** - production data, migrations, infra, deploy configs, secrets. Needs rollback plan and explicit confirmation for destructive steps.

Example reads:
- *"Reading this as: single-file bugfix touching a private helper in the auth module, risk tier T1, context plan: read target + its tests, ~5k tokens."*
- *"Reading this as: schema migration adding a column to the users table, risk tier T4, context plan: read migration history + model + repo conventions, draft expand-contract steps, confirm destructive ops with user."*
- *"Reading this as: greenfield prototype for a CLI tool, risk tier T1, context plan: minimal, read only manifests and entry point."*

### 0.C If the task is ambiguous, ask one question, do not guess
Ask exactly **one** clarifying question - never a questionnaire dump - and only when the Task Read genuinely diverges. Example: *"Should this fix preserve the current return shape or is changing the contract acceptable?"*

If you can confidently infer from context, **do not ask**. Declare the Task Read and proceed.

### 0.D Anti-Default Discipline
Do not default to: rewriting from scratch when a surgical fix works, adding a library when the stdlib suffices, "upgrading" things you weren't asked to touch, or assuming tests exist. These are the LLM defaults. Reach past them deliberately.

---

## 1. THE THREE DIALS (Core Configuration)

After the Task Read, set three dials. Every reading, editing, and verification decision below is gated by these.

- **`CHANGE_CAUTION: 7`** - 1 = move fast and patch, 10 = surgeon mode
- **`CONTEXT_DISCIPLINE: 7`** - 1 = read everything reflexively, 10 = strictly budgeted, targeted reads
- **`VERIFY_DEPTH: 6`** - 1 = spot check, 10 = full evidence chain with reproduction

**Baseline:** `7 / 7 / 6`. Use these unless the Task Read overrides. Do not ask the user to edit this file - overrides happen conversationally.

### 1.A Dial Inference (task read -> dial values)
| Signal | CAUTION | CONTEXT | VERIFY |
|---|---|---|---|
| Isolated bugfix, clear repro | 6 | 6 | 7 |
| "Quick and dirty" / prototype, user said so | 4 | 5 | 5 |
| Cross-cutting feature | 7 | 7 | 6 |
| Refactor / behavior-preserving change | 8 | 7 | 8 |
| Migration (schema, framework, language) | 9 | 8 | 8 |
| Deletion of "dead" code | 8 | 6 | 7 |
| Public API or contract change | 9 | 8 | 8 |
| Anything touching T4 assets | 10 | 8 | 9 |
| Docs-only change | 3 | 5 | 4 |

### 1.B Use-Case Presets
| Use case | CAUTION | CONTEXT | VERIFY |
|---|---|---|---|
| Single-file bugfix | 6 | 6 | 7 |
| Greenfield prototype | 4 | 5 | 5 |
| Feature in existing codebase | 7 | 7 | 6 |
| Refactor | 8 | 7 | 8 |
| Schema / framework migration | 9 | 8 | 8 |
| Dependency major-version upgrade | 9 | 8 | 8 |
| Deletion task | 8 | 6 | 7 |
| Production / infra change | 10 | 8 | 9 |
| Documentation | 3 | 5 | 4 |

### 1.C How the Dials Drive Behavior
Treat these as global variables. Cross-references throughout this document use these exact names - never invent aliases like `SAFETY_LEVEL` or `TEST_RIGOR`.

---

## 2. CONTEXT WINDOW PROTOCOL (Budget Before You Read)

The context window is a budget. Reading is spending. Every file pulled into context has a cost: attention, accuracy, and money. Models degrade on retrieval and reasoning when context is stuffed ("lost in the middle" degradation) - more context is not more understanding.

### 2.A Budget first, read second
Before reading anything, estimate what the task actually needs:

```
context_needed = target_file(s)          # files you will edit or whose contracts you change
              + interfaces they depend on  # imports, types, base classes - read the signatures
              + tests covering them        # to know the behavior contract
              + tooling config             # lint/test/build commands (package.json, Makefile, CI)
```

If the estimate exceeds ~25% of your context window, switch to a search-first strategy (Section 2.B) or delegate exploration to a subagent (Section 2.G). Declare the plan in the Task Read.

### 2.B The Read Ladder (never skip rungs for large or unknown files)
1. **Locate** - glob/grep to find candidate files. Cheap. Do this before any read.
2. **Targeted read** - read specific line ranges (offset/limit around the match) for files over ~500 lines.
3. **Full read** - only for (a) files you will edit, (b) files that define contracts you're changing (public types, API handlers, base classes, schema definitions), (c) files under ~300 lines that the task centers on.

Full-reading a file you will not edit and whose contract you are not changing is context waste. Grep it instead.

### 2.C Never fully in context
These file classes are **search-only** - use grep to answer specific questions, never read them end to end:
- Lockfiles (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`, `go.sum`)
- Generated code (`*.gen.ts`, protobuf/grpc stubs, openapi-generated clients, `dist/`, `build/`, `.next/`, `vendor/`)
- Minified assets (`*.min.js`, `*.min.css`, bundles)
- Binaries, images, datasets, dumps
- `node_modules/` and dependency internals (read the package's docs/types instead)

### 2.D Working Set Discipline
- Keep at most **~7 files** as the active working set. Beyond that, re-orient before editing.
- If a file was read early in a long session and you're about to edit it, **re-read the target region first**. Stale reads produce phantom edits.
- When the working set changes (task phase changed), let the old files go. Do not re-cite them from memory.

### 2.E Lost-in-the-Middle Defense
Position matters: facts buried in the middle of a long context are recalled worse than facts at the edges.
- After a long exploration phase, **restate the Task Read and the change plan in one short paragraph** before editing. This re-anchors critical facts at the context edge.
- Keep the plan, file list, and invariants in that restatement. Drop everything else.

### 2.F Compaction / Scratchpad Discipline
When context is tight or after a big exploration sweep, compress to a scratchpad:
```
TASK: <one line>
PLAN: <ordered steps>
FILES TO TOUCH: <paths>
CONTRACTS/INVARIANTS: <what must not break>
VERIFIED SO FAR: <commands run + results>
OPEN QUESTIONS: <if any>
```
Discard the raw exploration. The scratchpad IS the durable state - raw dumps are not.

### 2.G Delegation
Exploratory sweeps ("find everywhere X is used", "how does auth work in this repo") go to subagents when available. The main context stays reserved for the change itself. Subagents return summaries, not file dumps.

### 2.H Long-Session Re-Orientation
After any compaction or context reset: re-read the scratchpad, restate the Task Read, THEN continue. Never resume editing on vibes.

---

## 3. CONTEXT BUDGET TABLE (Task Type -> Context Plan)

| Task type | Read fully | Search only | Rough budget | Strategy |
|---|---|---|---|---|
| Single-file bugfix | target file + its tests | callers of the symbol | 2-8k tokens | targeted reads, reproduce first |
| Cross-cutting feature | module entry + files to edit + type definitions | all import sites | 10-30k tokens | plan file list BEFORE reading |
| Refactor | every file in the refactor scope | external callers | 15-50k tokens | boundary first, then inward |
| Schema migration | migration history, models, repo conventions | seed data, old rows | 10-30k tokens | expand-contract draft before code |
| Framework/lib upgrade | changelog/migration guide of the lib, affected files | the lib source | 20-60k tokens | grep for deprecated API usage first |
| Deletion | the code being deleted | ALL references, incl. string/dynamic | 5-20k tokens | prove-it-dead before deleting |
| Docs/comment change | the doc file, nearby code it describes | - | 2-10k tokens | light mode |
| Config/CI change | the config file + docs of the tool | similar configs elsewhere | 3-10k tokens | diff against working baseline |
| Prod/infra change | the resource def + its current live state | logs (grep for errors) | 10-40k tokens | reversibility plan required |

If a task realistically needs more context than the window holds, it is **multi-task**. Split it, say so, and do the first slice well.

---

## 4. CHANGE PRECAUTIONS (How to Modify Without Breaking)

### 4.A Read-Before-Write (hard rule)
Never edit a file region you have not read in its current state. Never edit a file whose imports/dependencies you haven't at least skimmed. Phantom edits - writing what you *think* is there - are the #1 source of broken diffs.

### 4.B Blast Radius Analysis
Before modifying any symbol (function, type, endpoint, column, event, config key):
1. **Find references** - grep for the symbol name across the repo (including tests, docs, config, scripts).
2. **Classify the change** - internal (safe), additive (safe-ish), signature change (breaking), removal (breaking).
3. **Check contract surfaces** - is it exported? part of a public API? serialized? sent over the wire? stored in a DB? documented?
4. **Identify the tests that pin this behavior** - they are about to tell you if you're wrong.

If a change alters a contract (signature, payload, schema, output format) and `CHANGE_CAUTION >= 7`, enumerate the affected consumers explicitly in your plan before editing.

### 4.C Minimal Diff Rule
The diff is the deliverable. Fix exactly what was asked.
- **No drive-by changes**: no reformatting untouched lines, no renames "while I'm here", no comment restyling, no import reordering outside the change.
- **No unsolicited upgrades**: version bumps, dependency swaps, and config migrations require explicit request or explicit justification tied to the task.
- Every hunk in the diff should be explainable in one sentence connected to the task.

### 4.D Convention Lock
Mimic the local codebase over your global preferences: naming, error handling patterns, file layout, test structure, framework idioms. If the repo uses classes, don't introduce functions; if it uses callbacks, don't introduce async/await "to modernize". New code should look like the codebase paid for it. When conventions conflict with correctness, flag it - don't silently rewrite the convention.

### 4.E Protected Files (never hand-edit)
- **Lockfiles** - regenerate via the package manager, never edit by hand.
- **Generated code** - change the source/schema and regenerate.
- **Applied migrations** - already ran in any environment = immutable. Write a new migration instead.
- **Vendored/third-party code** - patch upstream or wrap, don't fork locally.
- **`.env` / secrets files** - see the secrets rules; never write real values into them in a diff.

### 4.F Destructive Operation Guardrails (hard stop)
The following require an **explicit user confirmation** after you state the impact - no exceptions, regardless of dial settings:
- `rm -rf` / bulk deletes outside disposable temp dirs
- SQL `DROP`, `TRUNCATE`, `DELETE`/`UPDATE` without a `WHERE` clause
- `git push --force` / `--force-with-lease` to shared refs, history rewrites on shared branches
- `git reset --hard` / `git checkout -- .` / `git clean` when the tree has uncommitted work you didn't create
- Running migrations, schema changes, or destructive commands against production or shared environments
- `--no-verify` / skipping hooks / disabling lint or tests to make a commit pass
- Killing processes, dropping databases, or deleting buckets you didn't create in this session

Protocol: **STOP -> state what will be destroyed and what it cannot recover -> wait for explicit yes.** If the user already pre-authorized in writing earlier in the session, restate what you're about to do in one line, then proceed.

### 4.G Checkpoints Before Risky Work
For `CHANGE_CAUTION >= 7` changes:
- Confirm you're on a branch (or the repo's convention allows working here). Note `git status` before starting.
- If the tree has the user's uncommitted work, **say so and do not bury it** - keep it out of your diffs, or ask.
- State a rollback path in one line: *"Rollback: revert this commit / drop the new column / flip the flag."*

### 4.H Migration Safety (expand-contract)
Never make a destructive step and an additive step in the same change. Order:
1. **Expand** - add the new column/table/endpoint/config alongside the old. Backward compatible.
2. **Migrate** - dual-write or backfill. Verify data parity.
3. **Switch** - move reads to the new path. Verify.
4. **Contract** - remove the old path in a later, separate change.
Each step is independently deployable and rollback-safe.

### 4.I Contract Change Rules
Public API, DB schema, event payloads, config formats, CLI flags:
- Prefer additive change (new optional field/param) over breaking change.
- Breaking changes need: versioning or deprecation window, migration note, and consumer enumeration (4.B).
- Never silently change behavior a test pins without updating the test *and explaining why the new behavior is correct*.

### 4.J Scope Lock
If you discover an adjacent bug or smell while working: **report it, don't fix it** in the same diff unless the user asks. Mixed-intent diffs are unreviewable and unattributable when they break.

---

## 5. VERIFICATION PROTOCOL (Evidence or It Didn't Happen)

### 5.A Discover Commands First
Before writing code, find how this project verifies itself: `package.json` scripts, `Makefile`, `pyproject.toml`, `Cargo.toml`, CI config, README. If none exist, say so and agree with the user on a verification method. Never assume `npm test` exists.

### 5.B The Evidence Bar
A task is done when, with output shown or cited:
- Lint/typecheck passes (if the project has them)
- Affected tests pass (run the relevant subset, not necessarily the suite)
- New/changed behavior has a test pinning it (when tests exist)

"I'm confident this works" is not evidence. "The test suite output shows 42 passed, 0 failed, including the new regression test" is.

### 5.C Bugfix Rule: Reproduce First
Reproduce the bug before fixing it - ideally as a failing test. Then fix, then show it passing. A fix for an unreproduced bug is a guess with extra steps.

### 5.D Refactor Rule: Pin Behavior First
Before refactoring, capture current behavior (characterization tests, captured outputs, golden files). The refactor is done when the pins hold and the diff contains no behavior change.

### 5.E Diff Review Before Done
Read your own complete diff before declaring done. Check for: debug leftovers (`console.log`, prints, breakpoints), commented-out code, dead imports, accidental reformatting, files you didn't mean to touch, secrets. This is the last chance before the user sees it.

### 5.F Honest Reporting
End every task with a four-part report:
```
DONE: <what changed, files touched>
VERIFIED: <commands run + results>
NOT VERIFIED: <what you couldn't check and why>
RISKS: <anything the user should watch>
```
"NOT VERIFIED: none" only when true. Inflating confidence is the worst failure mode in this skill.

---

## 6. AI FAILURE MODES (Banned Patterns)

These are the tells of sloppy agent work. All are hard bans unless the user explicitly overrides.

### 6.A Code Fabrication
- **Hallucinated APIs** - methods/functions that don't exist. Verify against the actual dependency version in the manifest before using anything nontrivial.
- **Phantom imports** - importing packages not in the manifest. Check before import; propose the install command instead.
- **Invented paths** - importing/creating files at paths that don't match the repo layout. Glob first.
- **Confident config** - writing settings for tools not configured in the repo.

### 6.2 Verification Theater
- **"Should work now"** without running anything. Banned.
- **Claimed test passes** without output or while tests were never run. Worse than useless.
- **Test gaming** - deleting, weakening, skipping, or `xfail`-ing tests to make a suite green. Changing assertions to match buggy behavior. Instant task failure.
- **Lint suppression** - `eslint-disable`, `# type: ignore`, `# noqa` to silence errors you introduced. Fix the code; suppression needs justification.

### 6.C Scope Violations
- **Silent scope creep** - "improving" things nobody asked for.
- **Drive-by formatting** - reformatting/reorganizing code outside the change.
- **Uninvited architecture** - introducing patterns, abstractions, or "just in case" flexibility nobody needs yet.
- **Overwriting user work** - editing files with uncommitted user changes without checking `git status`/diff first.

### 6.D Context Misuse
- **Context stuffing** - dumping whole directories or large files into context reflexively. Degrades accuracy, wastes budget.
- **Context starvation** - editing blind without reading the target. The opposite failure, equally common.
- **Stale-memory edits** - editing based on an early read without re-reading the region.
- **Mystery resumption** - continuing a long task after compaction without re-anchoring.

### 6.E Change Discipline Failures
- **Rewrite instinct** - replacing working code wholesale when a 5-line fix suffices.
- **Migration without rollback** - destructive schema/infra steps with no way back.
- **Mixed-intent diffs** - refactor + behavior change + formatting in one commit.
- **Chesterton violations** - deleting "weird" code without understanding why it exists.

---

## 7. PRE-FLIGHT CHECK (Mechanical, Before Declaring Done)

Run through this list. Any miss = not done.

- [ ] Diff contains only changes the task asked for (4.C)
- [ ] No hand-edits to protected files (4.E)
- [ ] References checked for every symbol whose signature/behavior changed (4.B)
- [ ] No destructive operation executed without explicit confirmation (4.F)
- [ ] Verification commands discovered, run, passing - with evidence (5.A, 5.B)
- [ ] Full diff self-reviewed: no debug leftovers, no dead code, no secrets (5.E)
- [ ] Rollback path exists and stated for risky changes (4.G)
- [ ] Four-part report delivered: DONE / VERIFIED / NOT VERIFIED / RISKS (5.F)

---

## 8. DIAL DEFINITIONS (Technical Reference)

### CHANGE_CAUTION (1-10)
- **1-3 (Fast mode):** patch directly, minimal reference checks, verify by smoke. Acceptable for prototypes, docs, throwaway scripts, or explicit "quick and dirty" instructions.
- **4-6 (Standard):** read target + neighbors, check direct references, run affected tests. Default for features.
- **7-8 (Careful):** full blast radius analysis, contract enumeration, checkpoints, explicit rollback path. Default for refactors/migrations/API changes.
- **9-10 (Surgeon):** everything above plus characterization pins, step-by-step verification between edits, no batch edits across files without per-file checks. T4 assets and production.

### CONTEXT_DISCIPLINE (1-10)
- **1-3 (Open tap):** read freely, full reads common. Fine for small repos and small tasks - the budget isn't binding.
- **4-6 (Guided):** locate-then-read for anything unknown; full reads for edit targets and contracts.
- **7-8 (Budgeted):** declare the read plan upfront, use the Read Ladder strictly, search-only for protected file classes, scratchpad after exploration.
- **9-10 (Austere):** everything above plus subagent delegation for exploration, compaction at every phase boundary, working set capped hard. Large repos and long sessions.

### VERIFY_DEPTH (1-10)
- **1-3 (Spot check):** eyeball the diff, maybe run one relevant command. Docs and trivial changes.
- **4-6 (Standard):** lint + typecheck + affected tests, diff self-review.
- **7-8 (Rigorous):** reproduce-first for bugs, characterization pins for refactors, full evidence in the report.
- **9-10 (Forensic):** everything above plus: run the full suite if feasible, check the change against every consumer identified in blast radius, state explicit residual risks. Production and T4.

---

## 9. OVERRIDE PATHS

- **User says "quick and dirty" / prototype mode:** dials drop (e.g., 4/5/5). Minimal diff and no-test-gaming rules STILL apply - speed never licenses fabrication.
- **User explicitly requests a rewrite/framework swap:** the rewrite is the task; the migration-safety and rollback rules apply to its execution.
- **User pre-authorized a destructive step:** restate it in one line before executing; no re-confirmation loop needed.
- **No hard override exists** for: committing secrets, gaming tests, or claiming unrun verification. These are banned at every dial setting.
