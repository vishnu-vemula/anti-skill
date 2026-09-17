# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-17

### Added

- **antiskill** (`safe-change-engineering`) - flagship skill: task inference with risk tiers T0-T4, three dials (CHANGE_CAUTION / CONTEXT_DISCIPLINE / VERIFY_DEPTH) with inference and preset tables, context window protocol (budget-first, read ladder, protected file classes, working set, scratchpad, delegation), context budget table by task type, change precautions (read-before-write, blast radius analysis, minimal diff, convention lock, protected files, destructive-op guardrails, checkpoints, expand-contract migrations, contract change rules, scope lock), verification protocol (evidence bar, reproduce-first, characterization-first, diff review, honest reporting), AI failure-mode blacklist, mechanical pre-flight check.
- **context-skill** (`context-window-budgeting`) - token estimation, locate-then-read ladder, search-only file classes, budget tiers T1-T4, scratchpad format, lost-in-the-middle defense, delegation patterns, session hygiene.
- **change-safety-skill** (`change-precautions`) - blast radius analysis with change classification, minimal diff rule, convention lock, protected files, destructive guardrails, checkpoints and rollback, expand-contract ordering.
- **verification-skill** (`verify-before-done`) - evidence bar, command discovery, reproduce-first and pin-first rules, test-gaming ban, diff self-review checklist, DONE/VERIFIED/NOT VERIFIED/RISKS report format, confidence language table.
- **git-hygiene-skill** (`git-safety`) - inspect-before-act, uncommitted-work protection, atomic commits, never-commit list, destructive git bans, branching defaults.
- **dependency-skill** (`dependency-discipline`) - manifest verification before import, addition criteria ladder, install/upgrade/removal discipline, supply-chain sanity.
- **secrets-skill** (`secrets-hygiene`) - hard rules against hardcoded secrets, env pattern matching, gitignore checks, diff scanning, leak-rotation protocol, PII handling.
- **legacy-skill** (`legacy-codebase-navigation`) - archaeology protocol, Chesterton's fence, convention lock, rewrite ban, characterization tests for low-coverage repos.
- **refactor-skill** (`safe-refactoring`) - behavior-preservation contract, pin-first workflow, small verified steps, safe rename/extract, strangler-fig migrations.
- **deletion-skill** (`safe-deletion`) - prove-it-dead protocol including string/dynamic references, consumer-first deletion order, staged removal for public surfaces.
- **production-skill** (`production-change-guard`) - reversibility-first, expand-contract schema changes, migration mechanics, infra/config/deploy guardrails, pre-flight statement format.
- Repo tooling: `scripts/validate_skills.py` (frontmatter, size, banned-pattern, README-sync checks) and `scripts/context_estimate.py` (token budget estimator with tier classification and search-only flagging).
- CI (validation + markdown lint) and release (bundle) workflows, Claude plugin manifests, research docs, example sessions.

[1.0.0]: https://github.com/YOUR_USERNAME/antiskill/releases/tag/v1.0.0
