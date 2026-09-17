---
name: secrets-hygiene
description: Secrets and sensitive-data discipline for AI coding agents. Never hardcode or commit credentials, use the project's env/config patterns, keep secrets out of logs and error messages, scan diffs for sensitive patterns before committing, and know the rotate-first protocol when a secret leaks. Apply whenever code touches credentials, tokens, API keys, connection strings, PII, or environment configuration.
---

# antiskill/secrets: Secrets Hygiene

> A leaked secret is not fixed by deleting the commit. It is fixed by rotation.

---

## 1. HARD RULES

- **Never hardcode secrets** in source, tests, configs, scripts, comments, or commit messages. Not "temporarily". Not "just for local". Not in examples that look real.
- **Never commit real values** in `.env` files. Commit `.env.example` with placeholder keys and empty/dummy values instead.
- **Never log secrets** - no `console.log(token)`, no `print(api_key)`, no secrets in error messages, URLs (query strings carry tokens), or debug output.
- **Never paste secrets** from the user's files into your responses more than needed - redact (`sk-...abc123` style) when discussing them.

If a task requires a secret to function: read it from the environment/config at runtime and document what variable to set.

---

## 2. USE THE PROJECT'S PATTERN

Before writing any config/env code, find how THIS project handles secrets:
- `.env` + `dotenv`-style loading, platform env (Vercel/CI secrets), secret manager (Vault, SSM, Doppler), framework config
- Match it. Do not invent a parallel secrets mechanism.

When creating a new pattern, default to:
- `.env` (gitignored) + `.env.example` (committed, placeholders only)
- Fail fast at startup with a clear message when a required variable is missing - not a cryptic `None` crash three layers deep.

---

## 3. GITIGNORE CHECK

Before any task that creates env/config files:
- Is `.env` (and friends: `.env.local`, `*.pem`, `*.key`) in `.gitignore`? If not: add it FIRST, before creating the file.
- Never rely on "I just won't commit it". Check the ignore rule exists.

---

## 4. DIFF SCAN BEFORE COMMIT

Before every commit containing env/config/auth/logging changes, scan the diff for:
- High-entropy strings (random-looking base64/hex, 20+ chars)
- Known prefixes: `sk-`, `ghp_`, `AKIA`, `AIza`, `xoxb-`, `-----BEGIN`
- Connection strings with embedded credentials: `postgres://user:pass@...`
- Private keys, certificates, `.pem` blocks
- Real-looking emails/PII in fixtures that were "sample" data

Found one? Stop the commit. It never goes in, even in test fixtures - fixtures use obviously fake values (`test-token-123`, `AKIAXXXXXXXXXXXXXXXX`).

---

## 5. LEAK PROTOCOL (if a secret reached a repo)

1. **Rotate first.** Revoke/replace the credential with its provider. This is the only real fix.
2. Then scrub history (`git filter-repo` / BFG) if the repo is shared; for a fresh unpushed local repo, rewriting before first push is enough.
3. Check logs/CI output that may have captured it.
4. Report honestly: what leaked, where, what was rotated.

Deleting the line and pushing a "fix" leaves the secret valid in history. Rotation is the fix.

---

## 6. PII & SENSITIVE DATA

- Test fixtures use synthetic data. Never copy production rows/logs into tests.
- When writing log statements: log identifiers (user ID), not attributes (email, token, card number).
- Error messages shown to users never include internals; full detail goes to server-side logs only - and those logs still don't include secrets.

---

## 7. ANTI-PATTERNS (banned)

- **The placeholder that isn't** - `const API_KEY = "sk-live-a8f3..."` "for now".
- **The logger** - printing headers/auth objects "just to debug".
- **The URL dropper** - tokens in query strings (they land in logs, proxies, history).
- **The fixture from prod** - real data pasted as test data.
- **The example that works** - `.env.example` with actual working keys.
- **The delete-and-pray** - removing a leaked secret from HEAD without rotation.
