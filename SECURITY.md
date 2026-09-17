# Security Policy

## Reporting a Vulnerability

AntiSkill is a repository of instruction files (SKILL.md) and small validation scripts - it does not run in production services. Still, take anything unexpected seriously.

- Report privately via [GitHub security advisories](../../security/advisories/new) or open an issue marked `security`.
- You will get an acknowledgment within a few days.

## Scope

- Malicious or injected instructions hidden in skill files (prompt-injection payloads disguised as rules).
- Vulnerabilities in `scripts/*.py` (path traversal, unsafe parsing).
- Supply-chain concerns in CI workflows (pinned actions, permissions).

## Not in scope

- Prompt-injection attacks against agents *using* these skills from external content (websites, files in your repo). AntiSkill's guardrails reduce some of this surface (destructive-op confirmation, read-before-write), but no instruction set is a security boundary. Keep real secrets and production access out of agent reach.
