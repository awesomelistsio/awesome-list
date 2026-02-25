#!/usr/bin/env python3
"""Detect duplicate URLs in Markdown files.

Fails if the same URL appears multiple times *within the same file*.
This helps catch accidental duplicates in curated lists.

Usage:
  detect_duplicate_links.py [path ...]
If no paths are provided, scans all *.md in the repo.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s\)\]">]+")  # basic URL extraction

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
    # normalize common trailing slash differences
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
        urls = [normalize(u) for u in URL_RE.findall(text)]
        counts = defaultdict(int)
        for u in urls:
            counts[u] += 1
        dups = {u: c for u, c in counts.items() if c > 1}
        if dups:
            failures += 1
            print(f"Duplicate URLs in {f}:")
            for u, c in sorted(dups.items(), key=lambda x: (-x[1], x[0])):
                print(f"  ({c}x) {u}")
            print()
    if failures:
        print(f"Found duplicates in {failures} file(s).")
        return 1
    print("No duplicate URLs detected.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
