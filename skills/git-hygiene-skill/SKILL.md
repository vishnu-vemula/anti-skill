---
name: git-safety
description: Git hygiene and safety rules for AI coding agents. Inspect before committing, protect the user's uncommitted work, make atomic commits matching repo style, never commit secrets or generated junk, never force-push, rewrite history, or skip hooks. Apply whenever touching git - status checks, staging, committing, branching, or pushing.
---

# antiskill/git: Git Safety

> Git is the undo button of engineering. Don't be the one who breaks it.

---

## 1. INSPECT BEFORE YOU ACT

- `git status` before starting any task - know what state the tree is in.
- `git log --oneline -10` before writing any commit message - match the repo's style (imperative? conventional commits? scope prefixes?).
- `git diff` (and `git diff --staged`) before every commit - review exactly what's being committed, not what you remember writing.
- `git branch` / current branch check before starting work - know where you are.

---

## 2. PROTECT THE USER'S WORK

- **Uncommitted changes you didn't create:** treat as sacred. Never `reset --hard`, `checkout -- .`, `clean`, or stash-without-saying. Surface them: "You have uncommitted changes in X - want me to leave them untouched?"
- **Never bury user work in your commits.** Stage explicitly by path; avoid `git add -A` / `git add .` on a dirty tree containing foreign changes.
- **Don't commit to a branch the user didn't intend.** Feature work defaults to a branch when the repo convention says so; ask if ambiguous and the tree is clean.
- Never rebase/merge "to clean things up" unless asked.

---

## 3. ATOMIC COMMITS

- One commit = one logical change. Fix, refactor, and docs are three commits, not one.
- Mixed-intent commits make bisection useless and reverts impossible.
- If your diff accidentally contains two intents, split it: stage by hunks/paths.

**Message rules:**
- Match repo style from `git log`.
- Default: imperative subject <= 72 chars, blank line, body explaining WHY (the diff already says what).
- No AI-reminder footers, no emoji unless the repo uses them, no "Generated with..." unless asked.

---

## 4. WHAT NEVER GETS COMMITTED

- **Secrets** - keys, tokens, passwords, `.env` contents, connection strings with credentials. If it's in the diff, stop; see the secrets skill.
- **Generated junk** - `dist/`, `build/`, `.next/`, caches, `node_modules/`, logs, coverage output. Respect/update `.gitignore` instead of committing around it.
- **Local-only config** - `.env.local`, editor folders, OS junk (`.DS_Store`), unless the repo already tracks them deliberately.
- **Lockfile discipline:** commit lockfiles when the repo tracks them; never hand-edit them; regenerate via the package manager.

---

## 5. HARD BANS (destructive git)

All require explicit user confirmation with impact stated:

| Operation | Why it's gated |
|---|---|
| `push --force` / `--force-with-lease` to shared refs | rewrites others' history |
| `reset --hard` / `checkout -- .` / `clean -fd` on foreign changes | destroys uncommitted work |
| `commit --amend` after pushing | rewrites shared history |
| `rebase` on shared branches | rewrites shared history |
| `--no-verify` / skipping hooks | bypasses the project's own quality gates |
| `filter-branch` / history rewrites | irreversible team-wide impact |

Protocol: STOP -> state what is destroyed/rewritten and recoverability -> explicit yes. Pre-authorized earlier? Restate in one line, proceed.

---

## 6. BRANCHING DEFAULTS

- Don't create a branch unless asked or the repo convention implies it - but never do feature work on `main` in a team repo with branch protection either. When ambiguous and the tree is clean: ask once.
- Branch names: match repo convention; default `antiskill/<short-topic>`.
- Stay in your lane: don't switch branches mid-task with a dirty tree.

---

## 7. ANTI-PATTERNS (banned)

- **The kamikaze commit** - `git add -A && git commit -m "fix"` on a dirty tree with foreign changes.
- **The archaeologist** - amending and force-pushing repeatedly to "polish" pushed commits.
- **The ghost** - committing while another agent/user was mid-edit in the same files.
- **The secret smugler** - `.env` "temporarily" committed. Rotate if it ever happens (see secrets skill).
- **The hook skipper** - `--no-verify` to make a failing pre-commit pass.
- **The message sloth** - "update", "changes", "fix bug", "final final v2 REAL".
