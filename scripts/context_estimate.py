#!/usr/bin/env python3
"""context_estimate.py - estimate the token budget for files before reading them.

Practices what the context-window-budgeting skill preaches: budget before you read.

Given paths (files or dirs), estimates tokens per file, classifies the task into
a budget tier (T1 micro .. T4 expedition), flags search-only files (lockfiles,
generated, minified, vendored, binaries), and prints a read strategy.

Heuristic: ~chars/4 for text, tuned per extension. Order-of-magnitude accuracy,
which is all budgeting needs.

Usage:
  python scripts/context_estimate.py path/to/file.py src/ package.json
  python scripts/context_estimate.py --self-test

Exit code 0 unless --self-test fails.
Zero dependencies: stdlib only.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

BYTES_PER_TOKEN_TEXT = 4.0  # chars/4 heuristic; UTF-8 bytes used as proxy
LINES_PER_TOKEN_CODE = 1.0 / 10.0  # ~10 tokens/line, used as cross-check

SEARCH_ONLY_EXACT = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "poetry.lock",
    "Pipfile.lock",
    "uv.lock",
    "Cargo.lock",
    "go.sum",
    "composer.lock",
    "Gemfile.lock",
}
SEARCH_ONLY_DIR_PARTS = {
    "node_modules",
    "dist",
    "build",
    ".next",
    "out",
    "vendor",
    "target",
    "coverage",
    ".terraform",
}
SEARCH_ONLY_SUFFIXES = {
    ".min.js",
    ".min.css",
    ".map",
    ".lock",
    ".bin",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".woff",
    ".woff2",
    ".ttf",
    ".class",
    ".pyc",
    ".so",
    ".dll",
    ".exe",
}
CODE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".c", ".h", ".cpp", ".cs", ".swift", ".kt", ".php", ".sh", ".sql", ".yaml", ".yml", ".toml", ".json", ".md"}

TIER_TABLE = [
    (5_000, "T1 micro", "read the few files fully; ladder optional"),
    (20_000, "T2 standard", "locate-then-read unknowns; full-read edit targets + contracts"),
    (80_000, "T3 deep", "declare read plan first; working set discipline; scratchpad after exploration"),
    (float("inf"), "T4 expedition", "subagent exploration; phase-by-phase compaction; main context reserved for the change"),
]


def classify_search_only(path: Path) -> str | None:
    if path.name in SEARCH_ONLY_EXACT:
        return "lockfile"
    lowered = path.name.lower()
    if any(lowered.endswith(s) for s in SEARCH_ONLY_SUFFIXES):
        return "binary/minified/asset"
    for part in path.parts:
        if part.lower() in SEARCH_ONLY_DIR_PARTS:
            return "generated/vendored dir"
    return None


def estimate_file(path: Path) -> tuple[int, int, str | None]:
    """Return (tokens, lines, search_only_reason)."""
    reason = classify_search_only(path)
    try:
        data = path.read_bytes()
    except OSError:
        return 0, 0, "unreadable"
    lines = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    if reason:
        return 0, lines, reason
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return 0, lines, "binary/minified/asset"
    tokens = math.ceil(len(text) / BYTES_PER_TOKEN_TEXT)
    return tokens, lines, None


def walk(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        out: list[Path] = []
        for p in sorted(path.rglob("*")):
            if p.is_file() and classify_search_only(p) is None:
                out.append(p)
        return out
    return []


def self_test() -> bool:
    import tempfile

    ok = True
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "a.py").write_text("x = 1\n" * 100, encoding="utf-8")  # 700 chars
        (root / "package-lock.json").write_text("{}" * 1000, encoding="utf-8")
        (root / "app.min.js").write_text(";", encoding="utf-8")
        tokens, lines, reason = estimate_file(root / "a.py")
        if reason is not None or tokens != 175:
            print(f"SELF-TEST FAIL: a.py -> tokens={tokens} reason={reason}")
            ok = False
        _, _, reason = estimate_file(root / "package-lock.json")
        if reason != "lockfile":
            print(f"SELF-TEST FAIL: lockfile not flagged (reason={reason})")
            ok = False
        _, _, reason = estimate_file(root / "app.min.js")
        if reason is None:
            print("SELF-TEST FAIL: .min.js not flagged")
            ok = False
    print("SELF-TEST PASS" if ok else "SELF-TEST FAIL")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate token budget for paths before reading.")
    parser.add_argument("paths", nargs="*", help="files or directories to estimate")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return 0 if self_test() else 1
    if not args.paths:
        parser.error("provide at least one path (or --self-test)")

    total = 0
    flagged: list[str] = []
    print(f"{'tokens':>8}  {'lines':>7}  path")
    print("-" * 60)
    for raw in args.paths:
        for f in walk(Path(raw)):
            tokens, lines, reason = estimate_file(f)
            if reason:
                flagged.append(f"{f}  [{reason}: search-only, do not read]")
                continue
            total += tokens
            print(f"{tokens:>8}  {lines:>7}  {f}")

    for line in flagged:
        print(f"{'--':>8}  {'--':>7}  {line}")

    limit, tier, strategy = next(t for t in TIER_TABLE if total <= t[0])
    print("-" * 60)
    print(f"TOTAL (readable): ~{total:,} tokens  -> budget tier {tier}")
    print(f"strategy: {strategy}")
    if total > 0.25 * 128_000:
        print("note: estimate exceeds ~25% of a typical 128k window; prefer search-first or delegate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
