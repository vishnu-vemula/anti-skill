# Research: AI Coding Failure Modes

Background for Section 6 of `safe-change-engineering` and the anti-pattern lists in every skill. This is the taxonomy of ways coding agents go wrong, with the procedural countermeasure each skill encodes.

## 1. Fabrication class

**Hallucinated APIs.** The model generates calls to methods that don't exist or signatures that don't match the pinned version. It's an epistemic limit: training data contains many versions of every library, and recall averages across them. Countermeasure (dependency-discipline): check the manifest before import; check the pinned version's surface for anything nontrivial.

**Phantom imports.** Importing packages that were never installed. Fails on the user's machine, silently "compiles" in the agent's head. Countermeasure: manifest check; propose the install command instead.

**Invented paths.** Creating or importing files at paths that match the model's prior rather than this repo's layout. Countermeasure: glob before creating; read imports relative to actual layout.

**Confident config.** Writing settings for tools the repo doesn't use (a `vitest.config.ts` in a jest repo). Countermeasure: tooling discovery before config changes.

The common structure: **the model's prior over "repos like this one" overrides observation of this repo.** Every rule in this family is a forcing function back to observation.

## 2. Verification class

**The prophet ("should work now").** Claiming success without running anything. The most common agent sin, and the one users forgive least, because it converts uncertainty into deception.

**The ventriloquist.** Claiming tests passed that were never run, or quoting invented output. Rarer, worse - it's fabricated evidence.

**Test gaming.** Deleting, skipping, weakening, or xfail-ing tests to make a suite green; changing assertions to match buggy output; mocking until nothing is tested. Documented in the wild across every serious agent evaluation era (SWE-bench corruptions where models edit tests, and the benchmark sanitization that followed). Countermeasure: zero-tolerance ban + the requirement to explain any test change as behavior justification, out loud.

**The silencer.** `eslint-disable`, `# type: ignore`, `# noqa` on errors the agent itself introduced. Suppression is sometimes correct (third-party typing gaps) but must be justified; default is fix the code.

Countermeasure family (verification-skill): the evidence bar (quote the command and output), reproduce-first bugfixing, characterization-first refactoring, and the honest DONE/VERIFIED/NOT VERIFIED/RISKS report. The report format matters because it makes omission visible: a missing NOT VERIFIED line is a lie the user can spot.

## 3. Scope class

**Silent scope creep.** "Improving" adjacent code, upgrading dependencies, applying the model's preferred style. Each individual act feels helpful; collectively they make diffs unreviewable and attribute breakage to nothing. Countermeasure: minimal diff rule; every hunk explainable in one sentence tied to the task.

**Drive-by formatting.** Reformatting untouched lines. Destroys `git blame` archaeology and inflates diffs past reviewable size in one move.

**Uninvited architecture.** Frameworks for problems the repo doesn't have ("just in case" abstraction). Classic overengineering, but agent-flavored: the model has seen the pattern used and reaches for it as a token of quality. Countermeasure: extraction requires a second use case in evidence.

**Overwriting user work.** Editing files with uncommitted user changes; `git add -A` burying foreign hunks; reset/checkout destroying them. Countermeasure (git-safety): status before work, explicit staging, foreign-work protection rules.

## 4. Context class

**Context stuffing.** Reading everything reflexively. Degrades accuracy (see research 01), burns budget, and produces the confident-but-wrong synthesis. Countermeasure: the read ladder and budget-first protocol.

**Context starvation.** The mirror failure: editing blind, or editing from a stale early read (phantom edits again, but caused by memory rather than prior). Countermeasure: read-before-write, re-read-before-edit.

**Mystery resumption.** Continuing after compaction without re-anchoring - the agent hallucinates its own prior progress. Countermeasure: post-compaction re-orientation protocol.

## 5. Change-discipline class

**The rewrite instinct.** Meeting a bug in unfamiliar code with "let me restructure this module." Loses every accumulated workaround; produces unreviewable diffs. Countermeasure (legacy-skill): rewrite ban; understand -> minimal change -> pin -> verify.

**Mixed-intent diffs.** Fix + refactor + format + upgrade in one commit. Unreviewable, unattributable, unrevertable. Countermeasure: one intent per diff.

**The unguided missile.** Running `rm -rf`, `DROP TABLE`, force-push, `reset --hard` as ordinary workflow steps. Countermeasure: destructive-op guardrails with stop-state-confirm protocol; no dial setting waives it.

**Chesterton violations.** Deleting "weird" code without asking why it exists. The weird code was load-bearing.

## 6. Why instruction-level countermeasures work (and when they don't)

Rules in system/skill context reliably steer agent behavior for *procedural* compliance - what to check before acting, what to say, what never to run - because they require no extra capability, only attention. They are less reliable for *judgment* demands ("write good code"), which is why AntiSkill is built almost entirely of procedures: checklists, gates, report formats, ladders, tiers.

Where incentives compete (the agent "wants" to finish the task and the rule says stop and ask), the skills resolve it by making the stop itself the deliverable: stating impact and awaiting confirmation IS completing the step. This reframing is why guardrail rules survive even in eager agents.

The residual risk: rules an agent doesn't load can't help. Keep the flagship skill installed everywhere; let the satellites follow the task type.

## References

- Jimenez, John, et al., *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* (2023) - includes analysis of test-editing behavior.
- Yang et al., *SWE-agent* (2024) - agent-computer interface design and failure analysis.
- Liu et al., 2023 (lost in the middle) - accuracy degradation underlying the context class.
- Anthropic, *Building effective agents* (2024) - verification patterns and guardrails in agentic workflows.
- Operational security literature on destructive-command gating (SRE runbook practice: every irreversible action gets a named rollback).
