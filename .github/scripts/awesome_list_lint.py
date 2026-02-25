#!/usr/bin/env python3
"""
Awesome List lint (practical, low-noise)

Errors:
- README.md missing
- Missing "Contributing" heading
- Missing "License" heading
- TAB characters in README.md
- Trailing whitespace on resource-entry list lines
- Resource entry bullets must match: - [Name](URL) — Description

Resource entry bullet = a list line that starts with "- [" or "* ["
(Plain bullets in Contributing/Notes are ignored.)
"""
from __future__ import annotations

import re
from pathlib import Path
from collections import Counter

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
RESOURCE_BULLET_RE = re.compile(r"^[-*]\s+\[[^\]]+\]\((https?://[^\s)]+)\)\s*(—|-)\s+.+")
CODE_FENCE_RE = re.compile(r"^\s*```")

def strip_code_blocks(lines: list[str]) -> list[tuple[int, str]]:
    in_code = False
    out = []
    for i, line in enumerate(lines, start=1):
        if CODE_FENCE_RE.match(line):
            in_code = not in_code
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

    headings = []
    for ln, line in noncode:
        m = HEADING_RE.match(line)
        if m:
            headings.append(m.group(2).strip())

    lower = [h.lower() for h in headings]
    if not any("contributing" in h for h in lower):
        print("ERROR: Missing a 'Contributing' section heading in README.md.")
        return 1
    if not any("license" in h for h in lower):
        print("ERROR: Missing a 'License' section heading in README.md.")
        return 1

    # duplicate headings warning (non-fatal)
    c = Counter([h.lower() for h in headings])
    dups = [h for h, n in c.items() if n > 1]
    if dups:
        print("WARNING: Duplicate section headings detected:")
        for h in sorted(dups):
            print(f"  - {h}")
        print()

    errors = 0
    for ln, line in noncode:
        s = line.rstrip("\n")

        # Only lint “resource entry” bullets: "- [" or "* ["
        if s.startswith("- [") or s.startswith("* ["):
            if s != s.rstrip():
                print(f"ERROR: Trailing whitespace on resource entry line {ln}.")
                errors += 1

            if not RESOURCE_BULLET_RE.match(s):
                print(f"ERROR: Resource entry bullet malformed on line {ln}. Expected:")
                print("  - [Name](https://example.com) — Short, neutral description.")
                print(f"  {s}")
                errors += 1

    if errors:
        print(f"Found {errors} lint error(s).")
        return 1

    print("Awesome list lint: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
