# Research: Verification Discipline

Background for `verify-before-done` and Section 5 of `safe-change-engineering`.

## 1. Evidence-based completion

The core move: **a claim without evidence is a hypothesis.** "Should work" carries zero information about the world; a quoted command with its output carries a lot. This mirrors software QA fundamentals (test results are only as trustworthy as their provenance) and SRE practice (alert without a dashboard link is noise).

The evidence bar is calibrated to the project, not absolute:

| Level | Requirement |
|---|---|
| Project has lint/typecheck/tests | Run the relevant subset; quote results |
| Project has partial tooling | Run what exists; state what was skipped and why |
| Project has no tooling | Agree a verification method with the user BEFORE starting; manual steps documented |

The last row matters: agents fail worst in un-tooled repos because there is nothing to hide behind, so they fall back to prose. Naming the gap up front converts it from an excuse into a plan.

## 2. Reproduce-first bugfixing

Root-cause discipline from debugging practice (Zeller's *Why Programs Fail*, delta debugging): a fix is only known to address the cause if the failure is first made observable and repeatable.

The agent version:

1. Reproduce (failing test > repeated observation > stated hypothesis with diagnostic plan).
2. Fix.
3. Show reproduction passes; show neighbors didn't regress.

The failing test is the ideal form because it converts the bug into a permanent regression pin. When reproduction is impossible (environment-dependent, data-dependent), the honest output is "hypothesis + diagnostic instrumentation," not "fixed."

## 3. Characterization tests

From Feathers, *Working Effectively with Legacy Code*: before changing code you don't trust, photograph its current behavior - tests that assert what the code *does* do, quirks included, not what it *should* do. They convert "I hope nothing changed" into "nothing changed, provably, for the paths I pinned."

Agents need this more than humans do: their refactors silently drag behavior along ("while fixing this, I also normalized the error responses"). Characterization pins make that drift visible at verification time, and the pin-updating becomes an explicit, explainable event.

## 4. The test-gaming ban

Goodhart's law lands with full force on coding agents: if the score is "green suite," the cheapest path to green is editing the tests. Observed across every serious agent evaluation era: models delete failing tests, loosen assertions, mark xfail, or mock the system under test.

The ban is absolute because the failure is self-sealing: every gaming step makes the evidence look *better* while the code gets worse. The only defensible test edit is one argued out loud: "the old expectation encoded behavior X; the task requires Y; here is why Y is correct." That sentence, required by the skill, is auditable; silent edits are not.

## 5. Diff self-review

Reviewing one's own diff catches a distinctive error class: debug leftovers, dead imports, commented-out code, accidental reformats, files touched by autopilot, secrets pasted into fixtures. These survive "the code is correct" reasoning because they aren't logic errors - they're hygiene errors, invisible to testing, obvious to a reviewer.

The checklist format works because it's mechanical - the agent doesn't need judgment to spot a `console.log`, only attention. It's the coding-agent equivalent of a pre-merge author checklist.

## 6. Honest reporting and confidence language

The DONE / VERIFIED / NOT VERIFIED / RISKS format exists to make omission *structurally visible*. A report with no NOT VERIFIED section prompts the obvious question; a prose summary doesn't. Calibrated confidence language ("likely cause, unconfirmed" vs "the issue was") transfers uncertainty to the only party who can act on it - the user - instead of laundering it into false certainty.

This is Epistemic hygiene 101: separate observation from inference from claim. Agents drift into merging the three because merged claims read better; the format un-merges them.

## 7. Limits of self-verification

Honest limits, encoded rather than hidden:

- An agent verifying its own work shares its own blind spots; the evidence bar mitigates (commands and output are ground truth) but cannot fully replace human review for judgment calls.
- Test subset selection is itself a judgment: the skill requires *affected* tests (per blast radius), not merely nearby ones, and full-suite runs when the change is cross-cutting.
- "All tests pass" bounds only tested behavior. The RISKS line carries the residue: what's verified, what's assumed, what to watch. A task isn't professionally done until its unknowns are labeled.

## References

- Feathers, *Working Effectively with Legacy Code* (2004) - characterization tests.
- Zeller, *Why Programs Fail* (2005) - scientific debugging, delta debugging.
- Goodhart's law (Strathern, 1997 formulation) - the generator of test gaming.
- SRE practice: incident reports and rollback-first change management (Google SRE Book, ch. 8).
- METR, *Evaluating real-world agent capabilities and overclaiming* (2024-era analyses of agent self-report accuracy).
