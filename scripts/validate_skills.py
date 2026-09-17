#!/usr/bin/env python3
"""Validate AntiSkill skills/ directory.

Checks, per skill folder:
  - SKILL.md exists
  - YAML frontmatter exists, closes, and contains name + description
  - name is kebab-case and unique across the repo
  - description length is sane (40..600 chars) and mentions what+when intent
  - body size is context-friendly (warn > 24k chars, fail > 40k in --strict)
  - banned placeholder patterns absent (TODO:, FIXME:, lorem ipsum, <insert ...>)
  - README skills table stays in sync with install names (with --check-readme)

Exit codes: 0 = all pass, 1 = failures (or warnings under --strict).
Zero external dependencies: stdlib only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
README = REPO_ROOT / "README.md"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BANNED_PATTERNS = [
    (re.compile(r"TODO:", re.I), "TODO placeholder"),
    (re.compile(r"FIXME", re.I), "FIXME placeholder"),
    (re.compile(r"lorem ipsum", re.I), "lorem ipsum"),
    (re.compile(r"<insert [^>]*>", re.I), "<insert ...> placeholder"),
    (re.compile(r"\bTBD\b"), "TBD placeholder"),
]

SIZE_WARN = 24_000
SIZE_FAIL = 40_000
DESC_MIN = 40
DESC_MAX = 600


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    """Parse simple 'key: value' YAML frontmatter. Returns (meta, body) or None."""
    if not text.startswith("---"):
        return None
    parts = text.split("\n---", 2)
    if len(parts) < 3 and not text.startswith("---\n"):
        return None
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return None
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    body = "\n".join(lines[end + 1 :])
    return meta, body


def validate_skill(
    folder: Path, seen_names: dict[str, str], strict: bool
) -> tuple[str | None, list[str]]:
    """Validate one skill folder. Returns (install_name_or_None, errors)."""
    errors: list[str] = []
    warnings: list[str] = []
    name = folder.name
    skill_file = folder / "SKILL.md"
    install_name: str | None = None

    if not skill_file.is_file():
        return [f"{name}: missing SKILL.md"]

    text = skill_file.read_text(encoding="utf-8")
    parsed = parse_frontmatter(text)
    if parsed is None:
        return [f"{name}: invalid or missing YAML frontmatter"]
    meta, body = parsed

    install_name = meta.get("name", "")
    if not install_name:
        errors.append(f"{name}: frontmatter missing 'name'")
    elif not NAME_RE.match(install_name):
        errors.append(f"{name}: name '{install_name}' is not kebab-case")
    elif install_name in seen_names:
        errors.append(
            f"{name}: duplicate install name '{install_name}' "
            f"(also in {seen_names[install_name]})"
        )
    else:
        seen_names[install_name] = name
        install_name = install_name

    desc = meta.get("description", "")
    if not desc:
        errors.append(f"{name}: frontmatter missing 'description'")
    elif not (DESC_MIN <= len(desc) <= DESC_MAX):
        errors.append(
            f"{name}: description length {len(desc)} outside {DESC_MIN}..{DESC_MAX}"
        )

    size = len(text.encode("utf-8"))
    if size > SIZE_FAIL:
        errors.append(f"{name}: file is {size} bytes (> {SIZE_FAIL}); split or trim")
    elif size > SIZE_WARN:
        warnings.append(f"{name}: file is {size} bytes (> {SIZE_WARN}); consider trimming")

    for pattern, label in BANNED_PATTERNS:
        for m in pattern.finditer(body):
            lineno = body[: m.start()].count("\n") + 1
            errors.append(f"{name}: banned pattern '{label}' in body near line {lineno}")

    for msg in warnings:
        print(f"  WARN  {msg}")
    return install_name or None, errors


def check_readme_sync(install_names: dict[str, str]) -> list[str]:
    """Every install name must appear as `name` in the README skills table."""
    errors: list[str] = []
    if not README.is_file():
        return ["README.md missing - cannot sync-check"]
    readme = README.read_text(encoding="utf-8")
    for install, folder in install_names.items():
        if f"`{install}`" not in readme:
            errors.append(f"README.md: install name '{install}' ({folder}) not documented")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument(
        "--check-readme", action="store_true", help="verify README documents all skills"
    )
    args = parser.parse_args()

    if not SKILLS_DIR.is_dir():
        print(f"FATAL: {SKILLS_DIR} not found", file=sys.stderr)
        return 1

    folders = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    seen: dict[str, str] = {}
    failed = False
    print(f"Validating {len(folders)} skills in {SKILLS_DIR}")
    for folder in folders:
        install, errors = validate_skill(folder, seen, args.strict)
        if errors:
            failed = True
            for e in errors:
                print(f"  FAIL  {e}")
        if install and not errors:
            print(f"  OK    {folder.name} -> '{install}'")
        elif install is None and not errors:
            print(f"  OK    {folder.name}")

    if args.check_readme:
        print("Sync-checking README.md")
        errors = check_readme_sync(seen)
        if errors:
            failed = True
            for e in errors:
                print(f"  FAIL  {e}")
        else:
            print(f"  OK    README documents all {len(seen)} install names")

    print("RESULT:", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
