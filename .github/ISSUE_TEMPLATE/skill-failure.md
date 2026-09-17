---
name: Skill failure report
about: The agent did something a skill should have blocked, or a rule misfired
labels: skill-failure
---

**What the agent did**

<transcript or concise description>

**Which skill was loaded at the time**

- [ ] safe-change-engineering (antiskill)
- [ ] context-window-budgeting
- [ ] change-precautions
- [ ] verify-before-done
- [ ] git-safety
- [ ] dependency-discipline
- [ ] secrets-hygiene
- [ ] legacy-codebase-navigation
- [ ] safe-refactoring
- [ ] safe-deletion
- [ ] production-change-guard
- [ ] none / not sure

**What should have blocked or changed this behavior**

<which rule, or "no rule covers this">

**Agent + environment**

<e.g., Claude Code 2.x, Codex, Cursor - model, OS>

**Additional context**

<was the task ambiguous? was a dial override in effect?>
