---
name: change-precautions
description: Safe-change protocol for AI coding agents. Enforces read-before-write, blast radius analysis before modifying any symbol, protected-file rules, destructive-operation guardrails, checkpoints and rollback paths, and expand-contract migration ordering. Apply to every change in an existing codebase, and mandatory for schema, API, config, and production-adjacent changes.
---

# antiskill/change-safety: Change Precautions

> Every change has a blast radius. Your job is to know its size before the explosion, not after.

---

## 1. READ-BEFORE-WRITE (hard rule)

- Never edit a file region you have not read **in its current state**.
- Never edit a file without at least skimming its imports and immediate dependencies.
- If the file was read early in a long session, **re-read the target region** before editing.
- If the tree has uncommitted changes you didn't create, check `git status`/`git diff` on files you're about to touch - do not bury or overwrite the user's work.

Rationale: phantom edits (writing what you *assume* is there) are the top source of corrupted diffs.

---

## 2. BLAST RADIUS ANALYSIS

Before changing any symbol (function, class, type, endpoint, column, event name, config key):

### 2.1 Find references
Grep the symbol across the entire repo - code, tests, docs, config, scripts, CI. Include:
- String/dynamic references: symbol names in configs, reflection lookups, `getattr`/`eval` patterns, event names, DI registrations, SQL columns.
- External surfaces: is it part of a public API, webhook payload, stored schema, or CLI flag? Consumers outside the repo may exist.

### 2.2 Classify the change
| Change class | Risk | Required action |
|---|---|---|
| Internal logic fix | Low | run its tests |
| Additive (new optional param/field/route) | Low-med | check defaults hold for existing callers |
| Signature change (param reorder, type tighten) | High | enumerate every call site; update all |
| Behavior change (same signature, new semantics) | High | find every consumer of the semantics; update tests + docs |
| Removal | Highest | deletion protocol: deprecate, then remove (see the deletion skill) |

### 2.3 Contract surfaces
If the symbol crosses a boundary - exported from a module, HTTP API, DB schema, event bus, file format, config consumed elsewhere - the change is a **contract change**. Contract changes require:
1. Consumer enumeration (internal + external).
2. Compatibility decision: additive, versioned, or breaking-with-deprecation-window.
3. Never break silently.

---

## 3. MINIMAL DIFF RULE

The diff is the deliverable.
- Fix exactly what was asked. Every hunk must be explainable in one sentence tied to the task.
- **Banned as drive-bys:** reformatting untouched lines, renames "while I'm here", import reordering outside the change, comment restyling, dependency upgrades not requested.
- Found an adjacent bug? **Report it. Don't fix it in this diff** unless asked. Mixed-intent diffs are unreviewable.

---

## 4. CONVENTION LOCK

- Mimic local conventions over global taste: naming, error handling, structure, test layout, framework idioms.
- The repo's "weird" pattern that appears 40 times is a convention. The repo's "weird" pattern that appears once and has no test coverage is a possible bug - flag it, don't fix silently.
- New code should look like the codebase paid for it.

---

## 5. PROTECTED FILES (never hand-edit)

| File class | Correct action |
|---|---|
| Lockfiles | regenerate via the package manager |
| Generated code (stubs, dist, clients) | edit the source/schema, regenerate |
| Applied migrations | immutable once run anywhere; write a NEW migration |
| Vendored / third-party copies | patch upstream or wrap; never fork locally |
| Formatter/linter auto-fix output | accept or reject wholesale; don't hand-tune |

---

## 6. DESTRUCTIVE OPERATION GUARDRAILS (hard stop)

These require **explicit user confirmation** after you state the impact. No exceptions, no dial setting waives this:

- `rm -rf` / bulk file deletion outside disposable temp dirs
- SQL: `DROP`, `TRUNCATE`, `UPDATE`/`DELETE` without `WHERE`
- `git push --force` / history rewrite on shared refs
- `git reset --hard`, `git checkout -- .`, `git clean -fd` on a tree containing work you didn't create
- Migrations or schema changes against production/shared environments
- `--no-verify`, skipping hooks, disabling checks to make a commit pass
- Killing processes / dropping databases / deleting buckets you didn't create this session

**Protocol:** STOP -> state what will be destroyed and whether it is recoverable -> wait for explicit yes. If pre-authorized earlier in writing, restate the action in one line, then proceed.

---

## 7. CHECKPOINTS & ROLLBACK

Before any `CHANGE_CAUTION >= 7` work:
1. Note `git status` and the current branch/commit.
2. Confirm a recovery path exists: branch, stash, or clean revert.
3. State the rollback path in one line: *"Rollback: revert commit X / drop new column / flip flag F."*

A change without a stated rollback path is an unreviewed risk.

---

## 8. MIGRATION SAFETY (expand-contract)

Never mix destructive and additive steps in one change:

1. **Expand** - add new column/table/field/endpoint alongside old. Backward compatible. Deployable.
2. **Migrate** - backfill / dual-write. Verify data parity before proceeding.
3. **Switch** - move reads to the new path. Verify behavior parity.
4. **Contract** - remove the old path in a separate, later change.

Rules:
- Every step independently deployable and independently reversible.
- Backfills must be idempotent (safe to re-run) and resumable (safe to interrupt).
- Batch large backfills; never lock a production table for a full-table migration.
- Data deletion is always its own, final, separately-reviewed step.

---

## 9. RISK COMMUNICATION

For high-tier changes, the user gets a one-paragraph impact statement BEFORE edits:
- What changes, which surfaces are affected, what could break, what the rollback is, what will be verified after.

No surprises in the final report. Surprises mean the blast radius analysis was wrong or skipped.

---

## 10. ANTI-PATTERNS (banned)

- **The blind patch** - editing unread or stale-read code.
- **The silent breaking change** - altering a contract without consumer enumeration.
- **The kitchen-sink diff** - fix + refactor + format + upgrade in one commit.
- **The unguided missile** - destructive command without stated impact and confirmation.
- **The one-way door** - migration with no rollback path.
- **The graveyard shift** - deleting tests/data "to make it pass." The worst failure in this skill.
