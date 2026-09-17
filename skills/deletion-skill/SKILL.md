---
name: safe-deletion
description: Safe deletion protocol for AI coding agents. Prove code is actually dead before removing it by checking static references, string and dynamic usages, external consumers, and contract surfaces; stage removals with deprecation windows for anything public; and verify nothing breaks after the delete. Apply whenever the task is to remove code, features, endpoints, fields, flags, files, or "dead" code cleanup.
---

# antiskill/deletion: Safe Deletion

> Deleting code is easy. Proving it was dead is the job.

---

## 1. PROVE IT DEAD FIRST

Before deleting any code, file, endpoint, column, flag, or feature, check:

1. **Static references** - grep the symbol/filename across the whole repo: code, tests, config, scripts, CI, docs.
2. **String/dynamic references** - names in configs, reflection (`getattr`, `Class.forName`), DI registrations, event names, route strings, feature-flag keys, database column names in raw SQL, template files.
3. **External consumers** - public API endpoints, webhooks, exported packages, CLI flags, DB schemas, event payloads. Outside consumers may exist and can't be grepped.
4. **Temporal usage** - cron jobs, migrations that reference it, analytics events, scheduled reports, rarely-hit admin paths.
5. **Git history** - `git log -- <path>`: recently touched means someone may still depend on it.

**Verdict:** fully internal + zero references = deletable. Anything else = staged deletion (Section 3).

---

## 2. DELETE IN THE RIGHT ORDER

When removing a feature across layers, delete consumers before producers:
1. UI/entry points that call it
2. Handlers/routes/controllers
3. Services/business logic
4. Data access
5. Schema (ONLY via migration, and last - see below)
6. Config, docs, flags, CI references

Deleting a producer while consumers still reference it turns a clean deletion into a runtime crash in a code path you didn't test.

---

## 3. STAGED DELETION FOR ANYTHING PUBLIC

If the thing has (or might have) external consumers:
1. **Deprecate** - keep working, mark deprecated, announce removal, log a warning on use (rate-limited).
2. **Flag** - disable by default behind a config flag; rollout observation period.
3. **Delete** - remove code in a later release. Schema removal follows expand-contract timing (data first archived/exported if needed).

Silent removal of a public surface is a breaking change disguised as cleanup.

---

## 4. SCHEMA & DATA DELETION

- Column/table drops = migrations, run through the migration safety rules (expand-contract, separate final step, never bundled with the code that stopped using them).
- Deleting data requires explicit user confirmation (see change-precautions guardrails). Always.
- Prefer `DROP COLUMN`-style declarative removal through the project's migration tool; never raw destructive SQL outside a migration.

---

## 5. AFTER THE DELETE

- Run the affected test surface. Green? Deleted paths that tests still referenced would have failed - good.
- Grep the symbol ONE more time post-delete: docs, comments, configs, CHANGELOGs are allowed to keep historical mentions; live config/code must not.
- Build/typecheck catches statically-referenced leftovers in compiled languages; dynamic languages need the grep.
- Report: what was deleted, what was verified, and the deprecation notes if staged.

---

## 6. GIT IS NOT A BACKUP FOR OTHERS

You can restore deleted code from git. Your API consumers can't. Your analytics pipeline can't. The staging rules in Section 3 exist because "it's in git history" protects only you.

---

## 7. ANTI-PATTERNS (banned)

- **The vibe delete** - "looks unused" without a reference check.
- **The string-blind spot** - grepping code but not configs/events/SQL/templates.
- **The producer-first delete** - removing the library code while UI still imports it.
- **The instant drop** - deleting a public endpoint in one commit, no deprecation.
- **The data shrug** - `DROP TABLE` without confirmation or export.
- **The dead-test deletion** - removing tests that referenced the deleted code just to get green, without checking what those tests were actually verifying.
