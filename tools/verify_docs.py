"""
Verify docs/config consistency.
Checks:
1) keys in .env.example vs keys referenced in Python code via env accessors
2) keys in ENV_SCHEMA exist in .env.example
3) README command references include make check/test/smoke
"""

from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
CODE_DIRS = ["app.py", "core", "skills", "agents", "pages", "scripts"]
IGNORE_PARTS = {"venv", ".venv", ".git", "__pycache__", ".pytest_cache"}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.env_config import ENV_SCHEMA


def parse_env_keys(path: pathlib.Path) -> set[str]:
    keys: set[str] = set()
    if not path.exists():
        return keys
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k = s.split("=", 1)[0].strip()
        if k:
            keys.add(k)
    return keys


def iter_python_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for entry in CODE_DIRS:
        p = ROOT / entry
        if p.is_file() and p.suffix == ".py":
            files.append(p)
            continue
        if not p.exists():
            continue
        for fp in p.rglob("*.py"):
            if any(part in IGNORE_PARTS for part in fp.parts):
                continue
            files.append(fp)
    return files


def parse_code_env_refs() -> set[str]:
    patterns = [
        re.compile(r'os\.getenv\(\s*["\']([A-Z0-9_]+)["\']'),
        re.compile(r'os\.environ\.get\(\s*["\']([A-Z0-9_]+)["\']'),
        re.compile(r'os\.environ\[\s*["\']([A-Z0-9_]+)["\']\s*\]'),
        re.compile(r'get_env\(\s*["\']([A-Z0-9_]+)["\']'),
        re.compile(r'get_env_required\(\s*["\']([A-Z0-9_]+)["\']'),
    ]
    refs: set[str] = set()
    for fp in iter_python_files():
        txt = fp.read_text(encoding="utf-8", errors="ignore")
        for pat in patterns:
            refs.update(pat.findall(txt))
    return refs


def parse_schema_refs() -> set[str]:
    refs: set[str] = set()
    for rule in ENV_SCHEMA.values():
        refs.update(rule["required_all"])
        for group in rule["required_any"]:
            refs.update(group)
    return refs


def check_readme_commands(readme: pathlib.Path) -> list[str]:
    missing: list[str] = []
    text = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else ""
    for cmd in ("make check", "make test", "make smoke"):
        if cmd not in text:
            missing.append(cmd)
    return missing


def main() -> int:
    env_example = ROOT / ".env.example"
    readme = ROOT / "README.md"

    env_keys = parse_env_keys(env_example)
    code_keys = parse_code_env_refs()
    schema_keys = parse_schema_refs()

    missing_in_example = sorted(k for k in code_keys if k not in env_keys)
    missing_schema_in_example = sorted(k for k in schema_keys if k not in env_keys)
    missing_readme_cmds = check_readme_commands(readme)

    failed = False

    if not env_example.exists():
        print("FAIL: .env.example is missing")
        failed = True

    if missing_in_example:
        print("FAIL: .env.example missing keys referenced in code:")
        for k in missing_in_example:
            print(f"  - {k}")
        failed = True

    if missing_schema_in_example:
        print("FAIL: .env.example missing keys required by ENV_SCHEMA:")
        for k in missing_schema_in_example:
            print(f"  - {k}")
        failed = True

    if missing_readme_cmds:
        print("FAIL: README.md missing command references:")
        for cmd in missing_readme_cmds:
            print(f"  - {cmd}")
        failed = True

    if failed:
        return 1

    print("OK: docs/env checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
