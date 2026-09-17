---
name: dependency-discipline
description: Dependency management discipline for AI coding agents. Verify every import exists in the project manifest before using it, prefer stdlib and framework-native solutions before adding packages, use the project's package manager, respect lockfiles, pin responsibly, and apply supply-chain hygiene when adding or removing dependencies. Apply before importing anything new, and whenever installing, upgrading, or removing packages.
---

# antiskill/deps: Dependency Discipline

> Every dependency is a permanent liability with a nice README.

---

## 1. VERIFY BEFORE IMPORT (hard rule)

- Check `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` / `pom.xml` BEFORE importing any third-party symbol.
- Package present? Fine. Absent? **Never import anyway.** Propose the exact install command and wait for intent (or install if the task explicitly authorizes dependency changes).
- **Version matters:** the API you "know" may not exist in the pinned version. If the task uses anything nontrivial, check the installed version's docs/types (`node_modules/<pkg>/package.json`, lockfile grep, changelogs).

Phantom imports - code referencing packages that were never installed - fail on the user's machine, not yours. They are fabrication, not convenience.

---

## 2. ADDITION CRITERIA (in order)

1. **Language stdlib / platform built-ins** - can this be done without a package at all?
2. **Framework-native** - does the framework already ship it (React Query vs hand-rolled fetching, framework router vs custom)?
3. **Already-installed dependency** - does something in the manifest do the job (even if less famous)?
4. **New dependency** - last resort. Justify: actively maintained, reasonable size, standard choice (not a novelty package), compatible license.

Adding a package to avoid writing 15 lines is a bad trade. Adding a package that reimplements something already installed is a repo defect.

---

## 3. INSTALL HYGIENE

- **Use the project's package manager.** npm/yarn/pnpm are not interchangeable - check the lockfile. pip/poetry/uv, cargo, go - same principle.
- **Exact command, stated once:** `pnpm add zod@^3.23` - then run it, never hand-edit manifests for adds when a command exists.
- **One install command per change** unless the task is explicitly a dependency task.
- **Lockfile regenerates via the tool**, is committed if tracked, and is never hand-edited.
- Be careful with install scripts (postinstall): if a package wants to run arbitrary code at install, flag it before installing.

---

## 4. UPGRADE DISCIPLINE

- **Never drive-by upgrade.** Version bumps are their own task with their own diff and their own verification.
- Major versions = breaking changes. Upgrading majors requires: reading the migration guide, grepping for deprecated API usage, updating call sites, running the full affected test surface.
- Transitive surprise: adding a package may bump peer deps. Read what the install actually changed in the lockfile before committing.

---

## 5. REMOVAL DISCIPLINE

Removing a dependency safely:
1. Grep for all imports/usages of the package.
2. Remove usages first (separate commit), then the manifest entry.
3. Regenerate the lockfile via the tool.
4. Run the test surface; dependency removal breaks lazily-imported and dynamic paths - grep config files too (webpack/bundlers, CI, scripts).

---

## 6. SUPPLY-CHAIN HYGIENE

Before adding a package, a quick sanity pass:
- Maintained (recent releases or stable-and-done), not a typosquat of a famous name
- Reasonable download footprint for the value
- License compatible with the project

You are not required to be a security auditor, but you ARE required not to add the first npm result that fuzzy-matches the import name you hallucinated.

---

## 7. ANTI-PATTERNS (banned)

- **The phantom import** - importing a package that isn't installed.
- **The time traveler** - using an API from v5 when the repo pins v3.
- **The kitchen sink** - adding lodash/moment for one 10-line utility.
- **the bumper** - `npm update` / loose `*` versions as a "fix".
- **The silent peer** - ignoring peer-dependency resolution warnings.
- **The manifest surgeon** - hand-editing lockfiles or writing manifest entries for packages that were never installed in this environment.
