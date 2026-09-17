---
name: verify-before-done
description: Evidence-based completion protocol for AI coding agents. Discovers the project's verification commands, enforces reproduce-first bugfixing and characterization-first refactoring, requires lint/typecheck/test evidence with output, mandates diff self-review, and ends every task with an honest DONE/VERIFIED/NOT-VERIFIED/RISKS report. Apply whenever declaring any task complete.
---

# antiskill/verify: Verify Before Done

> "Should work" is a hypothesis. Evidence is a passing test you can quote.

---

## 1. DISCOVER COMMANDS FIRST

Before writing code, find how this project verifies itself:

- `package.json` `scripts`, `Makefile`/`justfile`, `pyproject.toml`/`setup.py`, `Cargo.toml`, `go.mod`, `gradlew`, `.github/workflows/`, README dev docs.

If no verification tooling exists: say so, and agree with the user on a manual verification method before starting. Never assume a command exists because it's common.

---

## 2. THE EVIDENCE BAR

A task is done when you can show:

1. **Lint passes** (if configured)
2. **Typecheck passes** (if configured)
3. **Affected tests pass** - the relevant subset at minimum, quoted output, not vibes
4. **New behavior is pinned** - the change you made has a test that fails without it (when the project has tests)

Evidence format: cite the command and its result. `"npm test -- auth": 23 passed, 0 failed` beats "tests pass" by exactly the width of the truth.

---

## 3. BUGFIX RULE: REPRODUCE FIRST

1. **Reproduce** the bug before touching anything - ideally as a failing test, minimally as a repeated observed output.
2. **Fix.**
3. **Show the reproduction now passes** - and nothing else regressed.

A fix for an unreproduced bug is a guess with extra steps. If you cannot reproduce it, say so and treat the fix as a hypothesis with a diagnostic plan.

---

## 4. REFACTOR RULE: PIN BEHAVIOR FIRST

Before refactoring:
1. Capture current behavior: existing tests, or write **characterization tests** that record what the code actually does today (including its quirks).
2. Refactor.
3. The pins hold, unchanged. If a pin "needed" updating, that's a behavior change - it belongs in a separate diff with justification.

---

## 5. TEST-GAMING BAN (zero tolerance)

Never, at any urgency level:
- Delete, skip, or `xfail` a failing test to make a suite green
- Weaken an assertion to match buggy behavior
- Change test expectations without explaining why the NEW behavior is correct
- Mock so much that the test no longer tests the change
- Suppress errors (`eslint-disable`, `# type: ignore`, `# noqa`, `@Suppress`) for code you introduced - fix the code; suppression requires a stated reason

If a test blocks correct work, the test or your understanding is wrong - investigate, then argue it explicitly to the user.

---

## 6. DIFF SELF-REVIEW

Before declaring done, read your complete diff as if reviewing a stranger's PR:

- [ ] No debug leftovers (`console.log`, `print`, breakpoints, logging you added)
- [ ] No commented-out code or dead branches
- [ ] No unused imports/variables introduced
- [ ] No accidental reformatting outside the change
- [ ] No files touched that the task didn't require
- [ ] No secrets, tokens, keys, or personal data in the diff
- [ ] Error paths handled, not just the happy path
- [ ] TODOs you added are explicit and reported (none silently left)

---

## 7. THE HONEST REPORT (mandatory format)

End every task with:

```
DONE:         <what changed; files touched>
VERIFIED:     <commands run + results, quoted>
NOT VERIFIED: <what you couldn't check and why>
RISKS:        <what the user should watch; residual unknowns>
```

Rules:
- `NOT VERIFIED: none` only when it is literally true.
- Never inflate. "I didn't run the integration tests because they need DB access" is a professional sentence; pretending is a fabrication.
- If verification failed and you couldn't fix it: report the failure verbatim. A red test honestly reported beats a green lie.

---

## 8. CONFIDENCE LANGUAGE

| Say this | Not this |
|---|---|
| "The test output shows X" | "Tests should pass" |
| "I changed A; I did not check B" | "Everything looks good" |
| "This is unverified" | "This should work" |
| "Likely cause is A, unconfirmed" | "The issue was A" (when you didn't confirm) |

Confidence theater is the most corrosive failure mode: it converts your uncertainty into the user's problem without warning.

---

## 9. ANTI-PATTERNS (banned)

- **The prophet** - "should work now" with nothing run.
- **The ventriloquist** - claiming test output that was never produced.
- **The gardener** - pruning tests to make the suite green.
- **The silencer** - lint/type suppressions to hide your own errors.
- **The half-report** - DONE and VERIFIED, never NOT VERIFIED or RISKS.
- **The scope amnesiac** - forgetting to check the diff for drive-by damage before reporting.
