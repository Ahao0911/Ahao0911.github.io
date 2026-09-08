#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
retune_blog_colors.py — One-time retune of Butterfly blog theme colors to match
the new personal homepage palette.

Mappings (case-insensitive, 6-digit hex only; structure untouched):
  #49b1f5  (theme default blue)  -> #2563eb
  #ff7242  (hover orange-red)    -> #0f766e
  #00c4b6  (theme cyan)          -> #0f766e

Creates blog/css/index.css.bak before the first write. Idempotent: on re-run it
does nothing if the original colors are no longer present.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "blog" / "css" / "index.css"
BAK = CSS.with_suffix(".css.bak")

REPLACEMENTS = [
    (re.compile(r"#49b1f5", re.IGNORECASE), "#2563eb"),
    (re.compile(r"#ff7242", re.IGNORECASE), "#0f766e"),
    (re.compile(r"#00c4b6", re.IGNORECASE), "#0f766e"),
]


def main() -> None:
    if not CSS.exists():
        raise SystemExit(f"css not found: {CSS}")

    if not BAK.exists():
        BAK.write_bytes(CSS.read_bytes())
        print(f"[bak  ] {BAK.relative_to(ROOT)}")

    text = CSS.read_text(encoding="utf-8")
    total = 0
    for pattern, new in REPLACEMENTS:
        count = len(pattern.findall(text))
        text, n = pattern.subn(new, text)
        total += n
        print(f"[hex  ] {pattern.pattern} -> {new}: {n} replaced (found {count})")

    if total:
        CSS.write_text(text, encoding="utf-8")
        print(f"[done ] wrote {CSS.relative_to(ROOT)} ({total} replacement(s)).")
    else:
        print("[info ] no original colors remain; file untouched.")


if __name__ == "__main__":
    main()
