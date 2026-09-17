---
name: production-change-guard
description: Guardrails for AI coding agents making production-adjacent changes - database migrations, infrastructure as code, deploy configs, CI/CD, environment variables, and live-ops commands. Requires reversibility-first thinking, expand-contract migration ordering, explicit confirmation for destructive or irreversible steps, and a stated rollback path for every change. Apply whenever a change touches production systems, shared environments, or data at rest.
---

# antiskill/production: Production Change Guard

> In production, the plan is not "make the change." The plan is "make the change reversible."

---

## 1. REVERSIBILITY FIRST

Before proposing ANY production-adjacent change, answer: **"If this goes wrong at 2am, how does it get undone?"**

| Change type | Rollback story |
|---|---|
| Additive code/config | revert the deploy |
| Schema: add column/table | drop it (safe if unused) |
| Schema: rename | expand-contract, migrate both ways |
| Schema: drop | **backup/export first**, confirmed irreversible window |
| Env var add | revert value |
| Env var delete | old value documented in the PR/commit |
| Infra resource | recreate procedure documented (or IaC revert) |
| Data backfill | idempotent + resumable, inverse script if applicable |

No rollback story = no change. State the story in the plan, before writing anything.

---

## 2. EXPAND-CONTRACT (schema and contracts)

1. **Expand** - add the new column/table/field/index alongside the old. Backward compatible, deployable independently.
2. **Migrate** - backfill/dual-write. Idempotent, batched, never long-locking a live table. Verify parity.
3. **Switch** - move reads to the new path. Verify behavior.
4. **Contract** - remove the old path in a later, separate change.

Rules: one phase per deploy. Never destructive + additive in the same step. Never edit an applied migration - write a new one.

---

## 3. HARD STOPS (explicit confirmation, always)

- `DROP` / `TRUNCATE` / `DELETE`/`UPDATE` without `WHERE` on any shared environment
- Migrations against production/shared data outside an approved migration flow
- `--force` deploys, skipped health checks, `--no-verify` anything
- Killing processes/services you didn't start this session
- Deleting buckets, volumes, log groups, or secrets
- Disabling alarms/monitoring "temporarily"

Protocol: STOP -> state what is destroyed, whether it's recoverable, and the fallback -> explicit yes. Verbal "pre-authorization" from earlier gets restated in one line before execution.

---

## 4. MIGRATION MECHANICS

- **Run through the project's migration tooling** (Rails/Alembic/Flyway/Prisma/etc.), never ad-hoc SQL.
- **New file per change** - applied migrations are immutable history.
- **Test migrations against a copy of realistic data**, not empty tables (row counts and indexes change lock behavior).
- **Long operations:** batch, chunk, and throttle; state expected duration; schedule windows with the user.
- **Verify after:** row counts, parity checks, app health, error rates - report the evidence.

---

## 5. INFRA & CONFIG CHANGES

- **IaC at rest:** prefer changing the Terraform/K8s/Helm/Pulumi source and applying, not console clicks. Git history is the audit trail.
- **Env vars:** document old + new values in the change; secrets via the platform's secret store, never plaintext in manifests.
- **Least-privilege check:** new service accounts/roles get minimum permissions, not `*`.
- **Drift check:** the live state can differ from the repo. Read the actual current state (plan/inspect) before proposing diffs.

---

## 6. DEPLOY CHANGES

- Deploy configs, health checks, rollout strategy, rollback hooks are production surface: minimal diffs, contract awareness, full verification.
- Never bundle a risky deploy-config change with an unrelated feature.
- Changes to CI gates (skipping tests, loosening checks) get the same scrutiny as production changes - they ARE the safety system.

---

## 7. THE PRE-FLIGHT STATEMENT

Before executing any production-adjacent change, state in the plan:

```
CHANGE:      <what will change>
BLAST RADIUS: <services/data/users affected>
ROLLBACK:    <exact undo procedure>
VERIFICATION: <how we'll know it worked>
STOP POINTS:  <steps requiring explicit confirmation>
```

Then execute phase by phase, verifying at each stop.

---

## 8. ANTI-PATTERNS (banned)

- **The one-way door** - any change without a rollback story.
- **The mega-migration** - rename + backfill + cleanup in one deploy.
- **The hotfix amnesia** - prod "quick fixes" that never get ported back to source.
- **The silent env change** - env var edits without documentation.
- **The over-privileged key** - `*` policies because scoping was work.
- **The untested migration** - first run is against production data.
- **The alarm disabler** - monitoring off "for five minutes" during a risky change.
