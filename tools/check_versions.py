#!/usr/bin/env python3
"""Compare the versions pinned in preamble.tex against the current PyPI releases.

The book pins versions on purpose: a listing that was run against langchain
1.3.14 is only honest about langchain 1.3.14. But the LangChain ecosystem
releases faster than this book does, and a pin that has silently gone stale is
worse than one that is visibly stale. So this runs on every build and prints a
table, and it never fails the build.

Emits GitHub-flavoured Markdown on stdout.

    python3 tools/check_versions.py
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# LaTeX macro in preamble.tex -> distribution name on PyPI.
PINS: dict[str, str] = {
    "lcver": "langchain",
    "lccorever": "langchain-core",
    "lgver": "langgraph",
    "lgpgver": "langgraph-checkpoint-postgres",
    "lcclassicver": "langchain-classic",
    "lcanthropicver": "langchain-anthropic",
    "lsver": "langsmith",
    "mcpadapterver": "langchain-mcp-adapters",
    "deepagentsver": "deepagents",
}

PREAMBLE = Path(__file__).resolve().parent.parent / "preamble.tex"
TIMEOUT = 20


def pinned_versions(text: str) -> dict[str, str]:
    """Pull \\newcommand{\\name}{value} pairs out of the preamble."""
    found = {}
    for macro in PINS:
        m = re.search(
            r"\\newcommand\{\\" + re.escape(macro) + r"\}\{([^}]*)\}", text
        )
        if m:
            found[macro] = m.group(1).strip()
    return found


def latest_on_pypi(dist: str) -> str | None:
    url = f"https://pypi.org/pypi/{dist}/json"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            return json.load(resp)["info"]["version"]
    except (urllib.error.URLError, KeyError, TimeoutError, json.JSONDecodeError):
        return None


def main() -> int:
    if not PREAMBLE.exists():
        print(f"preamble.tex not found at {PREAMBLE}", file=sys.stderr)
        return 1

    pinned = pinned_versions(PREAMBLE.read_text(encoding="utf-8"))
    missing = sorted(set(PINS) - set(pinned))

    rows, drifted, unreachable = [], 0, 0
    for macro, dist in PINS.items():
        pin = pinned.get(macro)
        if pin is None:
            continue
        latest = latest_on_pypi(dist)
        if latest is None:
            state, unreachable = "unreachable", unreachable + 1
        elif latest == pin:
            state = "current"
        else:
            state, drifted = f"**behind** ({latest})", drifted + 1
        rows.append((dist, macro, pin, state))

    print("## Pinned versions\n")
    print("| Package | Macro | Pinned | PyPI |")
    print("|---|---|---|---|")
    for dist, macro, pin, state in rows:
        print(f"| `{dist}` | `\\{macro}` | `{pin}` | {state} |")
    print()

    if missing:
        print(
            "Macros declared here but absent from `preamble.tex`: "
            + ", ".join(f"`\\{m}`" for m in missing)
            + "\n"
        )
    if unreachable:
        print(f"_{unreachable} package(s) could not be checked._\n")
    if drifted:
        print(
            f"**{drifted} pin(s) are behind the current release.** That is not "
            "automatically a problem — the book pins what it ran against. It is "
            "a problem once a pin is old enough that the listings no longer "
            "describe what a reader will install.\n"
        )
    else:
        print("_All reachable pins match the current release._\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
