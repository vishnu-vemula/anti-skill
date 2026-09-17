---
name: legacy-codebase-navigation
description: Discipline for AI coding agents working in existing, mature, or legacy codebases. Archaeology before surgery: map entry points and conventions first, match local patterns over global best practices, respect Chesterton's fence, and never launch uninvited rewrites or style modernizations. Apply whenever entering an unfamiliar existing codebase or a repo older than the task itself.
---

# antiskill/legacy: Legacy Codebase Navigation

> The codebase survived without you. Understand why before you improve it.

---

## 1. ARCHAEOLOGY BEFORE SURGERY

Before changing code in an unfamiliar repo, answer:
1. **Entry points** - where does execution start? (main, routes, handlers, jobs)
2. **Conventions** - naming, error handling, module layout, DI pattern, test structure. Read 2-3 representative files of the area you're touching.
3. **Tests as documentation** - the tests nearest your target describe intended behavior, including weird intended behavior.
4. **History** - `git log --oneline -- <target file>`: recent churn (active area, be careful) vs. untouched for years (frozen area, be MORE careful - nobody remembers how it works).
5. **The weird parts** - comment oddities, defensive checks, "do not remove" markers. They usually encode an incident.

Budget this exploration (see the context skill): locate-first, targeted reads, scratchpad the findings.

---

## 2. CHESTERTON'S FENCE

Do not remove or "clean up" inexplicable code until you know why it exists:
- The check for `if (id === 0)` that looks pointless? Someone's production incident.
- The retry wrapper that looks redundant? A dead network path.
- The duplicated function? A team split that couldn't share a module.

Find the reason (git blame, commit message, test, comment, ask the user). If the reason is gone AND the owner confirms, remove. Otherwise: leave it, note it.

---

## 3. CONVENTION LOCK (local law beats global taste)

- Match the local style over your preferences, even when the local style is "outdated": callbacks over async, classes over functions, error-code returns over exceptions, whatever the repo does.
- The migration to the "better" pattern across the codebase is a project decision, not a drive-by.
- New code = local idiom + your change. If local idiom is genuinely dangerous (SQL string concat, plaintext passwords), flag it and propose the fix - don't silently deviate and don't silently comply.

---

## 4. REWRITE BAN

Never respond to a bug or small feature in a legacy area with "let me rewrite this module." Rewrites:
- Lose every accumulated workaround (the fence posts)
- Are unreviewable diffs
- Trade known bugs for unknown ones

The path: understand the specific behavior -> minimal change -> pin with a test -> verify. If the module is truly unsalvageable, that's a user decision - present the case, let them choose.

---

## 5. WORKING WITH MISSING TESTS

Legacy repos often have thin coverage. Compensate:
1. Write a characterization test capturing CURRENT behavior around your change (even if current behavior is odd - capture it, then decide).
2. Make your change.
3. Pins hold -> your change preserved behavior. Pin changed -> you altered behavior: intended and explained, or a bug you introduced.

---

## 6. DEPENDENCY REALITIES

- The framework version pinned here is the law. Do not use APIs from newer versions you "know".
- Check what's actually in the lockfile, not what you remember from training.
- Suggest upgrades as findings; don't couple them to your change.

---

## 7. ANTI-PATTERNS (banned)

- **The colonizer** - "modernizing" a working module to current fashion.
- **The fence remover** - deleting defensive code that "does nothing".
- **The framework tourist** - writing React-18-style code in a React-15 repo.
- **The orphan** - adding a new pattern used exactly once, nowhere else in the repo.
- **The big bang** - rewrite instead of fix because reading was harder than writing.
- **The style tourist** - reformatting legacy files to your formatter config in a logic-change diff.
