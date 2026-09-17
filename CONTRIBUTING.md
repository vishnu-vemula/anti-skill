# Contributing to AntiSkill

Thanks for helping make AI agents less dangerous.

## Ground rules

1. **Skills are instruction files, not essays.** Every rule must be actionable by an agent: a check it can run, a gate it can stop at, a format it can produce. "Write good code" is not a rule; "quote the failing command's output" is.
2. **Procedural over judgmental.** We can't instruct capability, but we can instruct process. Prefer checklists, ladders, tiers, gates, and report formats.
3. **Every behavior change gets reasoning.** PRs that alter agent behavior must cite rationale in [`research/`](research/) or in the PR description: what failure mode this blocks, where the practice comes from.
4. **No contradictions across skills.** Skills share vocabulary (Task Read, dials, blast radius, evidence bar, pins). If your change redefines a shared term, update it everywhere.
5. **Keep skills context-friendly.** A SKILL.md is itself read into a context window. Flagship stays under ~24k chars; satellites stay tight. Split rather than grow.

## Adding a new skill

1. Create `skills/<your-skill>/SKILL.md`.
2. Frontmatter: `name` (kebab-case install name, unique) and `description` (40-600 chars: what it does + when to apply).
3. Follow the house structure: purpose line, numbered sections, anti-patterns ("banned") list at the end.
4. Add the skill to the table in `README.md` and the `Which one should I use?` section if relevant.
5. Add a `CHANGELOG.md` entry under `[Unreleased]`.
6. Run `python scripts/validate_skills.py --strict --check-readme` locally.

## Editing an existing skill

- Removals of rules need justification (which failure mode is now acceptable, and why).
- Dial defaults change only with evidence the old default was miscalibrated.
- The hard bans (test gaming, secret commits, fabrication, destructive ops without confirmation) are not softened in PRs; they may only be refined in wording.

## Development

```bash
python scripts/validate_skills.py --strict --check-readme   # CI gate
python scripts/context_estimate.py skills                   # size hygiene
python scripts/context_estimate.py --self-test              # estimator self-test
```

CI runs validation and markdown lint on every PR.

## Reporting a failure the skills didn't catch

Open an issue with: what the agent did, what rule *should* have blocked it, and (ideally) a minimal transcript. Failure reports are the highest-value contributions - they're the raw material for the next rule.
