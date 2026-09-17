# Research: Context Window Engineering

Background for `context-window-budgeting` and Section 2 of `safe-change-engineering`.

## 1. The window is a budget, not a feature

Marketing treats long context as capability: "1M tokens!" In practice, the context window behaves like a **workbench with a degradation curve**, not a warehouse. Three distinct costs apply to every token admitted:

1. **Attention cost** - relevance scores dilute as context grows; the model's effective per-fact attention drops with volume.
2. **Accuracy cost** - retrieval and reasoning over long contexts measurably degrade (see "lost in the middle" below).
3. **Economic cost** - every token in context is reprocessed on every subsequent turn of the session. A stuffed context is a tax on every future step.

The engineering conclusion: **read less, read the right things, re-anchor often.** This is why the skills treat reading as spending and demand a budget before reads begin.

## 2. Lost in the middle

Liu et al., *"Lost in the Middle: How Language Models Use Long Contexts"* (2023) demonstrated that LLM retrieval over long contexts is U-shaped: facts near the beginning and end of the context are recalled well; facts in the middle are recalled poorly - even by models that score well on needle-in-a-haystack tests. Follow-up work on multi-needle and reasoning-heavy tasks shows the effect worsens when the model must *combine* scattered facts rather than surface one.

Implications baked into the skills:

- **Re-anchoring (Section 8 of context-window-budgeting):** after a long exploration sweep, restate the task, plan, and invariants. This physically relocates critical facts to the recency edge of the context.
- **Scratchpad compaction:** raw file dumps age badly; a compressed scratchpad is the durable state that survives phase transitions.
- **Freshness before edits:** re-read the target region right before editing. A file read 100k tokens ago is, attentionally, a rumor.

## 3. Nominal vs effective context

Independent of the degradation curve, effective context is further reduced by:

- **Instruction saturation** - rules, conventions, and system prompts already occupy the window before any code arrives.
- **Working-set pressure** - an agent juggling 20 "active" files makes more cross-file mistakes than one holding 7, independent of window size. Working memory limits show up in agent behavior much as they do in humans (Miller-style limits are a useful metaphor even if the literal 7±2 number is folklore).
- **Task interference** - interleaving two tasks' explorations doubles working-set pressure and increases cross-contamination (fixes applied to the wrong task's mental model).

Hence the working-set cap (≤ ~7 active files), phase-boundary garbage collection, and one-task-at-a-time discipline.

## 4. Cost estimation for source code

Token counting without a tokenizer is approximate, but budgeting doesn't need precision - it needs order of magnitude:

- English prose: ~1 token per 4 characters (~75 tokens per 100 words).
- Source code: ~8-12 tokens per line for typical formatted code (punctuation and identifiers tokenize densely).
- A 500-line source file ≈ 4-6k tokens. A 3,000-line "God file" ≈ 25-35k tokens - already a significant fraction of a 128k window.
- Lockfiles and minified assets are pathological: `package-lock.json` for a mid-size project routinely exceeds 500k tokens. These are never read; they are grep targets. (This is why protected file classes exist at all.)

`scripts/context_estimate.py` implements the chars/4 heuristic with per-extension tuning, plus the search-only file classification, so a human or agent can produce the budget mechanically.

## 5. The read ladder

Three rungs, in order:

1. **Locate (search)** - glob/grep. Cost is near-zero and it answers "where" and "how many" - the two questions that size the budget. Skipping this rung is how context stuffing starts.
2. **Targeted read** - offset/limit windows around matches. For files > ~500 lines this is the default; most of a large file is irrelevant to any single task.
3. **Full read** - reserved for edit targets, contract files, and small central files. Full-reading a file you won't edit and whose contract you don't change is the canonical overspend.

This mirrors how senior engineers read unfamiliar code (search, jump, skim signatures) versus how junior ones do (open file, scroll from line 1).

## 6. Budget tiers

| Tier | Scale | Strategy |
|---|---|---|
| T1 (<5k) | one function's world | read freely; ladder optional |
| T2 (5-20k) | one module | ladder for unknowns; full-read targets/contracts |
| T3 (20-80k) | cross-cutting | declared read plan, working set, scratchpad |
| T4 (80k+) | migration/expedition | subagent exploration, compaction at phase boundaries, main context reserved for the change |

Tier escalation is a finding, not a failure: if the user expected T1 and the estimate says T4, surfacing the mismatch *is* the value ("this is bigger than it looks - here's the first slice").

## 7. Delegation

Subagents (where the runtime supports them) convert context pressure into parallelism: scouts explore and return summaries, readers digest files into signatures and side effects, verifiers run suites and return failures verbatim. The main context is reserved for the plan, the scratchpad, the current edit targets, and the diff under review. The failure mode to avoid: subagents returning file *contents* instead of *answers* - that just relocates the stuffing.

## 8. Session hygiene

- **Post-compaction re-orientation** is mandatory: re-read scratchpad, restate the Task Read, re-verify working set state (`git status` + targeted re-read). Resuming "on vibes" after a reset is the mystery-resume anti-pattern.
- **Context pressure signals** - misquoting file contents, losing track of which files changed, re-reading known things - mean the soft ceiling is hit. Response: compact immediately, not after one more read. Agents, like humans, are bad at noticing their own degradation in the moment; the skill encodes the checklist instead.

## References

- Liu et al., 2023, *Lost in the Middle: How Language Models Use Long Contexts* (TACL).
- Kamradt, 2023, *Needle in a Haystack* benchmark (context-retrieval degradation visualization).
- Golovneva et al., 2023, *Rosy Eyed LLMs? Impact of Contextual Conflicting Instructions* - instruction interference in long contexts.
- Industry practice: Claude Code / Codex / Cursor documentation on context management, compaction, and subagent patterns (progressive disclosure of instructions is the same principle at the prompt level: Anthropic's Agent Skills spec keeps SKILL.md metadata light and body content loaded on demand).
