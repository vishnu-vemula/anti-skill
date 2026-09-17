# Example: Dial Presets in Practice

How the flagship skill's dials (`CHANGE_CAUTION / CONTEXT_DISCIPLINE / VERIFY_DEPTH`) auto-tune from the Task Read.

## 1. "Quick and dirty" prototype (user said so)

```
Task Read: greenfield CLI prototype, risk tier T1 (no blast radius).
Dials: 4 / 5 / 5

Behavior:
- Reads are light: manifest + a few reference files, no ladder ceremony
- Direct implementation, minimal reference checking
- Verification: runs it once, shows the output - done
Still enforced at every dial: no phantom imports (manifest checked),
no fabricated claims ("it runs" only with shown output), no secrets
committed, no test gaming.
```

## 2. Cross-cutting feature in a mature repo

```
Task Read: feature spanning auth + billing modules, risk tier T3
(public API surface + payments). Dials: 7 / 7 / 6

Behavior:
- Read plan declared first: entry points, contracts, tests (~25k tokens)
- Blast radius: enumerate consumers of the touched endpoints before editing
- Additive contract change chosen (new optional field) over breaking change
- Affected test subsets run; new tests pin the new field
- Report includes NOT VERIFIED: stripe webhook path (needs live keys)
```

## 3. Schema migration (the high-caution case)

```
Task Read: rename users.email to users.primary_email, risk tier T4
(production schema). Dials: 9 / 8 / 8

Behavior:
- Expand-contract plan written BEFORE any code:
  1. add primary_email (expand)
  2. backfill + dual-write (migrate, batched, idempotent)
  3. switch reads (verify parity)
  4. remove email column - SEPARATE later migration (contract)
- Rollback path stated per phase
- Contract-phase (the DROP COLUMN) is flagged: needs explicit
  confirmation + data export per the production skill
- Migration tested against a copy of realistic data
```

## 4. Docs-only change

```
Task Read: README update, risk tier T0. Dials: 3 / 5 / 4

Behavior:
- Read the doc + the code it describes (targeted reads only)
- No code files touched; no conventions debates
- Verification: markdown renders, links valid
- The full ceremony would be theater here - the dials keep it proportionate
```

The point of the dial system: discipline is proportionate, not bureaucratic. Low-risk work moves fast; high-risk work slows down *by procedure, not by mood* - and the hard bans (fabrication, test gaming, secrets, unconfirmed destructive ops) stay on at every setting.
