#!/usr/bin/env python3
"""Lightweight lint for Awesome List-style repos.

Designed to be generic and low-assumption, while still preventing:
- malformed list bullets (e.g., missing markdown link)
- section drift (missing Contributing / License blocks)
- accidental tab characters
- trailing whitespace on list lines (common in copy/paste)

Rules (README.md-focused):
1) README.md must exist.
2) Must include a Contributing section header containing 'Contributing'.
3) Must include a License section header containing 'License'.
4) List items in markdown (lines starting with '- ' or '* ') should contain at least one markdown link: [text](url)
   (We skip code blocks.)
5) Warn on duplicate section headings.
6) Error on TAB characters in README.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import Counter

MD_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^\s)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

def strip_code_blocks(lines: list[str]) -> list[tuple[int, str]]:
    in_code = False
    out = []
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append((i, line))
            continue
        if not in_code:
            out.append((i, line))
    return out

def main() -> int:
    readme = Path("README.md")
    if not readme.exists():
        print("ERROR: README.md not found.")
        return 1

    text = readme.read_text(encoding="utf-8", errors="ignore")
    if "\t" in text:
        print("ERROR: README.md contains TAB characters. Replace tabs with spaces.")
        return 1

    lines = text.splitlines()
    noncode = strip_code_blocks(lines)

    # headings
    headings = []
    for ln, line in noncode:
        m = HEADING_RE.match(line)
        if m:
            headings.append(m.group(2).strip())

    # required sections (case-insensitive match)
    lower = [h.lower() for h in headings]
    if not any("contributing" in h for h in lower):
        print("ERROR: Missing a 'Contributing' section heading in README.md.")
        return 1
    if not any("license" in h for h in lower):
        print("ERROR: Missing a 'License' section heading in README.md.")
        return 1

    # duplicate headings warning
    c = Counter([h.lower() for h in headings])
    dups = [h for h, n in c.items() if n > 1]
    if dups:
        print("WARNING: Duplicate section headings detected:")
        for h in sorted(dups):
            print(f"  - {h}")
        print()

    # list item checks
    errors = 0
    for ln, line in noncode:
        s = line.rstrip("\n")
        if s.startswith("- ") or s.startswith("* "):
            # ignore horizontal rules like "- - -" (rare) or empty bullets
            if s.strip() in ("-","*"):
                continue
            # trailing whitespace warning (but fail only for list lines with trailing spaces)
            if s != s.rstrip():
                print(f"ERROR: Trailing whitespace on list line {ln}.")
                errors += 1

            # If it's a list item, require at least one markdown link.
            # This is a strong Awesome List convention and prevents malformed bullets.
            if not MD_LINK_RE.search(s):
                # Allow list items that are clearly section/meta (e.g., "- **License:** ...")
                if not re.search(r"\*\*.+\*\*", s):
                    print(f"ERROR: List item on line {ln} missing a markdown link [text](url).")
                    print(f"  {s}")
                    errors += 1

    if errors:
        print(f"Found {errors} lint error(s).")
        return 1

    print("Awesome list lint: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
