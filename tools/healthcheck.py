"""
Integration healthcheck.
Modes:
- stub (default): import checks for local/CI smoke
- live: env validation + lightweight client initialization checks
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
from typing import List, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.env_config import get_google_api_key, load_env, validate_env


def _print_report(mode: str, missing_env: List[str], checks: List[Tuple[str, str, str]], exit_code: int) -> None:
    print(f"MODE: {mode}")
    if missing_env:
        print("ENV: missing")
        for item in missing_env:
            print(f"  - {item}")
    else:
        print("ENV: OK")

    print("CHECKS:")
    for name, status, detail in checks:
        print(f"- {name}: {status} ({detail})")

    print(f"EXIT CODE: {exit_code}")


def run_stub() -> int:
    load_env()
    missing = validate_env("stub")
    checks: List[Tuple[str, str, str]] = []

    if missing:
        checks.append(("env_schema", "FAIL", "missing required keys for stub"))
        _print_report("stub", missing, checks, 1)
        return 1

    try:
        import streamlit  # noqa: F401
        import yfinance  # noqa: F401
        import gspread  # noqa: F401
        import google.generativeai  # noqa: F401
        checks.append(("imports", "OK", "streamlit/yfinance/gspread/google.generativeai"))
        _print_report("stub", [], checks, 0)
        return 0
    except Exception as e:
        checks.append(("imports", "FAIL", str(e)))
        _print_report("stub", [], checks, 1)
        return 1


def run_live() -> int:
    load_env()
    ok = True
    checks: List[Tuple[str, str, str]] = []
    missing = validate_env("live")
    if missing:
        checks.append(("env_schema", "FAIL", "missing required keys for live"))
        ok = False
    else:
        checks.append(("env_schema", "OK", "all live requirements present"))

    try:
        from exa_py import Exa

        if os.getenv("EXA_API_KEY"):
            Exa(api_key=os.getenv("EXA_API_KEY"))
            checks.append(("exa", "OK", "client init"))
        else:
            checks.append(("exa", "SKIP", "EXA_API_KEY missing"))
    except Exception as e:
        checks.append(("exa", "FAIL", str(e)))
        ok = False

    try:
        from tavily import TavilyClient

        if os.getenv("TAVILY_API_KEY"):
            TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            checks.append(("tavily", "OK", "client init"))
        else:
            checks.append(("tavily", "SKIP", "TAVILY_API_KEY missing"))
    except Exception as e:
        checks.append(("tavily", "FAIL", str(e)))
        ok = False

    try:
        import google.generativeai as genai

        gkey = get_google_api_key()
        if gkey:
            genai.configure(api_key=gkey)
            checks.append(("genai", "OK", "configure(api_key=...)"))
        else:
            checks.append(("genai", "SKIP", "GOOGLE_API_KEY/GEMINI_API_KEY missing"))
    except Exception as e:
        checks.append(("genai", "FAIL", str(e)))
        ok = False

    exit_code = 0 if ok else 1
    _print_report("live", missing, checks, exit_code)
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["stub", "live"], default="stub")
    args = parser.parse_args()

    if args.mode == "live":
        return run_live()
    return run_stub()


if __name__ == "__main__":
    sys.exit(main())
