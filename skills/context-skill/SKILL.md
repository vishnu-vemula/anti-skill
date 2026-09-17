---
name: context-window-budgeting
description: Deep context-window engineering for AI coding agents. Estimates the token budget a task actually needs before reading, enforces a locate-then-read ladder, keeps protected file classes search-only, and manages compaction, scratchpads, and subagent delegation across long sessions. Apply on large or unfamiliar codebases, long multi-step tasks, and any session nearing the context limit.
---

# antiskill/context: Context Window Budgeting

> The context window is a budget. Reading is spending. More context is not more understanding - past a point, it is less.

---

## 1. THE CORE MODEL

1. Context has a **hard ceiling** (window size) and a **soft ceiling** (where reasoning quality degrades). Budget against the soft one.
2. **Effective context < nominal context.** Long-context degradation ("lost in the middle") means facts buried mid-context are recalled worse than facts at the edges. Position and recency matter.
3. Every token in context has three costs: **attention** (dilutes everything else), **accuracy** (retrieval error grows with size), **money/latency** (every subsequent turn re-processes it).
4. Therefore: **read less, but read the right things, and re-anchor often.**

---

## 2. ESTIMATE BEFORE READING

Before reading anything, produce the budget:

```
TASK:        <one line>
EDIT TARGETS: <files you will modify>          -> read fully
CONTRACTS:   <files defining interfaces you change> -> read fully
BEHAVIOR:    <tests pinning those contracts>    -> read fully
TOOLING:     <manifests, CI config, Makefile>   -> skim
EVERYTHING ELSE                                -> search only, never full-read
```

Rough token math (good enough for budgeting):
- Source code: ~1 token per 3-4 characters, ~8-12 tokens/line. A 500-line file is roughly 4-6k tokens.
- Lockfiles, minified bundles, generated stubs: DO NOT estimate - they are search-only (Section 4).

**Decision rule:** if the estimate exceeds ~25% of the window, or you can't name the edit targets yet, you are in exploration mode - use the ladder below or delegate.

---

## 3. THE READ LADDER (locate -> target -> full)

Never jump straight to a full read of an unknown or large file.

1. **LOCATE** - glob/grep to find candidates. Answers: where does X live? who uses Y? Cheapest operation; always first.
2. **TARGETED READ** - read a line range around matches (offset/limit). Default for anything over ~500 lines. Follow the import chain only as far as the task needs - usually signatures, not bodies.
3. **FULL READ** - reserved for: (a) files you will edit, (b) contract files you're changing (public types, API routes, base classes, schema), (c) small files (<~300 lines) central to the task.

If you full-read something and then don't edit it, don't cite it, and don't need its contract - that was overspending. Note it and correct.

---

## 4. PROTECTED FILE CLASSES (search-only, never full-read)

| Class | Examples | Why | Instead |
|---|---|---|---|
| Lockfiles | `package-lock.json`, `yarn.lock`, `Cargo.lock`, `go.sum`, `poetry.lock` | Huge, machine-generated | grep for a package name to check resolution/version |
| Generated code | `*.gen.*`, protobuf/grpc stubs, OpenAPI clients, `dist/`, `build/`, `.next/` | Derived state | read the source schema instead |
| Minified assets | `*.min.js`, bundles | Token-dense garbage | read source maps or the source |
| Vendored code | `vendor/`, third-party copies | Not yours to reason about fully | read the upstream docs |
| Data/binary | datasets, dumps, images | Not readable usefully | use metadata/counts/grep |
| Dependency internals | files inside `node_modules/` etc. | Huge detour | read the package's types/docs; grep its exports if needed |

If a question about a lockfile matters ("is X pinned? what version resolves?"), grep it. One question, one grep, one answer.

---

## 5. BUDGET TIERS

| Tier | Scale | Feel | Strategy |
|---|---|---|---|
| T1 Micro | < 5k tokens | One function's world | Just read the few files fully. Ladder optional. |
| T2 Standard | 5-20k | One module | Ladder for anything unknown; full-read edit targets + contracts |
| T3 Deep | 20-80k | Cross-cutting task | Declare the read plan FIRST; working set discipline; scratchpad after exploration |
| T4 Expedition | 80k+ | Migration / repo-wide | Subagent exploration, phase-by-phase compaction, main context reserved for the change |

**Tier escalation is a signal, not a failure.** If a task looks like T4 but the user expected a quick fix, surface the mismatch: "This is bigger than it looks - here's the slice I'll do first."

---

## 6. WORKING SET DISCIPLINE

- Active working set: **<= ~7 files.** More than that and edits start colliding with memory.
- **Re-read before edit**: any file read early in the session gets its target region re-read right before you edit it. Stale reads produce phantom edits.
- **Phase boundary = garbage collection.** When moving from exploration to editing (or edit phase A to B), drop the old raw context. Keep the scratchpad, drop the dumps.

---

## 7. SCRATCHPAD FORMAT (the durable state)

After exploration or at any phase boundary, compress to:

```
TASK:         <one line>
PLAN:         <ordered steps remaining>
FILES TO TOUCH: <paths>
CONTRACTS/INVARIANTS: <what must not break>
VERIFIED SO FAR: <commands run + results>
OPEN QUESTIONS: <if any>
```

The scratchpad is the session's source of truth. Raw file dumps are disposable; the scratchpad is not.

---

## 8. POSITION & RE-ANCHORING (lost-in-the-middle defense)

- After any long exploration sweep, **restate TASK + PLAN + invariants in a short paragraph** before editing. This puts critical facts at the recency edge of context.
- Before each edit, the contract facts for that specific edit (symbol signature, callers found, test pinning it) should be recent - if they're from 100k tokens ago, re-grep. It's cheaper than being wrong.
- Long instruction documents: extract the rules relevant to the current task, don't carry the whole document passively.

---

## 9. DELEGATION PATTERNS

When subagents are available:
- **Scout** - "find every caller of X / how does auth work / where is Y configured." Returns a summary + file:line list, not file contents.
- **Reader** - "read these 5 files and report the signatures and side effects relevant to Z."
- **Verifier** - post-change: "run the test suite for module M and report failures verbatim."

The main context is reserved for: the plan, the scratchpad, the files being edited right now, and the diff under review.

---

## 10. SESSION HYGIENE

- **After compaction/reset:** re-read scratchpad -> restate Task Read -> re-verify the working set files still match (quick `git status` + targeted re-read) -> continue. Never resume on vibes.
- **Multi-task sessions:** finish one task's report before opening the next task's files. Interleaved exploration of two tasks doubles the working set and halves the accuracy.
- **Context pressure signals** (you are near the soft ceiling): you start misquoting file contents, lose track of which files changed, or re-read things you already read. Response: compact to scratchpad NOW, not after one more read.

---

## 11. ANTI-PATTERNS (banned)

- **The directory dump** - recursively reading a repo "to understand it." Budget violation; use locate-first.
- **The lockfile read** - full-reading any protected file class. Ever.
- **The hoarder** - carrying exploration dumps through the entire session "just in case."
- **The blind editor** - editing files never read at all, or edited from stale memory.
- **The mystery resume** - continuing after compaction without re-anchoring.
- **The context bragger** - "I've read all 200 files." Reading is not understanding; the question is whether the right 7 files are in the working set.
