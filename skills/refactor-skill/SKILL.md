---
name: safe-refactoring
description: Behavior-preserving refactoring discipline for AI coding agents. Pin behavior with characterization tests first, take small steps verified independently, use the strangler-fig pattern for large migrations, keep refactors in dedicated diffs separate from behavior changes, and verify with the full affected test surface. Apply whenever the task is to restructure, rename, extract, migrate, or "clean up" existing working code.
---

# antiskill/refactor: Safe Refactoring

> A refactor that changes behavior is not a refactor. It's an untested rewrite wearing a trench coat.

---

## 1. THE CONTRACT

Refactoring = changing structure WITHOUT changing observable behavior. If behavior changes, it's a feature/fix and needs its own diff and justification. Never mix the two.

---

## 2. PIN BEHAVIOR FIRST

Before touching anything:
1. **Existing tests** cover the area? Run them; they're your safety net. Note skips/fails BEFORE starting (pre-existing reds are not yours, but know them).
2. **No coverage?** Write characterization tests that record what the code does TODAY - including quirks. You're not judging behavior yet, you're photographing it.
3. For tricky pure logic: golden files / captured input-output pairs work when test scaffolding is heavy.

Pins are the definition of done: refactor complete = pins hold, unchanged.

---

## 3. SMALL STEPS, EACH VERIFIED

- One transformation per step: extract OR rename OR inline OR move - never several at once.
- Verify (tests/typecheck) after each step. A red test after a 6-step batch tells you nothing; after a 1-step change it points at the cause.
- Commit per step (or per coherent few) so reverts are surgical.

**Step order heuristic:** bottom-up - refactor the leaves (pure functions) first, then composition, then entry points. Leaves are cheapest to verify.

---

## 4. RENAME SAFELY

1. Grep every occurrence of the old name: code, tests, config, docs, string/dynamic references.
2. Rename in definition + all references in one step.
3. Grep again for stragglers (comments, docs, string keys) - update or explicitly leave.
4. If the name crosses a public boundary (API field, DB column, event key): that's not a rename, that's a contract change - see the change-precautions skill (add new, migrate, switch, remove).

---

## 5. EXTRACT SAFELY

- Extract verbatim first: move the code, change nothing, pass what it needs.
- Verify. THEN reshape the extracted unit if needed - as a separate step.
- Don't extract + generalize + optimize in one motion; each is a separate verification point.

---

## 6. LARGE MIGRATIONS: STRANGLER FIG

For framework/language/architecture migrations too big for one diff:
1. Put a seam at the boundary (facade, adapter, route-level switch).
2. Move one slice at a time to the new implementation. Old and new coexist.
3. Verify each slice against the pins.
4. Remove the old path only when the last slice is migrated and stable - a separate final commit.

Dual-running buys you rollback at every step; a big-bang migration buys you a weekend in the office.

---

## 7. BOUNDARY AWARENESS

Blast radius check before starting (see change-precautions): exports of everything you'll touch, their callers, the tests pinning them. A "simple extract" that changes a module's public surface is a contract change for every importer.

---

## 8. ANTI-PATTERNS (banned)

- **The sneaky feature** - behavior change smuggled inside a rename/extract diff.
- **The grand tour** - repo-wide reformat + refactor in one PR.
- **The pin skipper** - "tests will catch it" in a repo with 4 tests.
- **The abstraction sprout** - extracting a "reusable" helper used exactly once.
- **The premature pattern** - Visitor/Factory/Strategy for a 40-line module that will never grow.
- **The silent signature drift** - "simplifying" a function signature while extracting, breaking callers found later by someone else.
