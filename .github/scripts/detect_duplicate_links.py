#!/usr/bin/env python3
"""
Detect duplicate URLs in Awesome List resource entries.

Only scans lines that start with "- [" or "* [" (resource entries).
Plain text bullets are ignored.

Fails if the same URL appears multiple times in the same file's resource entries.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

URL_RE = re.compile(r"\[[^\]]+\]\((https?://[^\s)]+)\)")
RESOURCE_LINE_RE = re.compile(r"^[-*]\s+\[")

def iter_md_files(paths: list[str]) -> list[Path]:
    if not paths:
        return [p for p in Path(".").rglob("*.md") if ".git" not in p.parts]
    files: list[Path] = []
    for s in paths:
        p = Path(s)
        if p.is_dir():
            files.extend([x for x in p.rglob("*.md") if ".git" not in x.parts])
        elif p.is_file():
            files.append(p)
    return files

def normalize(url: str) -> str:
    url = url.strip().rstrip(".,;:!?)\"]'")
    if url.endswith("/") and len(url) > 10:
        url = url[:-1]
    return url

def main() -> int:
    files = iter_md_files(sys.argv[1:])
    if not files:
        print("No markdown files found.")
        return 0

    failures = 0
    for f in sorted(set(files)):
        text = f.read_text(encoding="utf-8", errors="ignore")
        urls = []

        for line in text.splitlines():
            if RESOURCE_LINE_RE.match(line):
                m = URL_RE.search(line)
                if m:
                    urls.append(normalize(m.group(1)))

        counts = defaultdict(int)
        for u in urls:
            counts[u] += 1
        dups = {u: c for u, c in counts.items() if c > 1}

        if dups:
            failures += 1
            print(f"Duplicate resource URLs in {f}:")
            for u, c in sorted(dups.items(), key=lambda x: (-x[1], x[0])):
                print(f"  ({c}x) {u}")
            print()

    if failures:
        print(f"Found duplicates in {failures} file(s).")
        return 1

    print("No duplicate resource URLs detected.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
