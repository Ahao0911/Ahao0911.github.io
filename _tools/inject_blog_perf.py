#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_blog_perf.py — One-time script that injects resource-hints + the
ahaos-perf.js loader into every blog/*.html file right before </head>.

Injected block (idempotent: files already containing the script marker are
skipped, so re-running never duplicates):
    <link rel="preconnect" href="https://cdn.jsdelivr.net">
    <link rel="preconnect" href="https://npm.elemecdn.com">
    <script src="/blog/js/ahaos-perf.js" defer></script>
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"

MARKER = '<script src="/blog/js/ahaos-perf.js"'
BLOCK = (
    '  <link rel="preconnect" href="https://cdn.jsdelivr.net">\n'
    '  <link rel="preconnect" href="https://npm.elemecdn.com">\n'
    '  <script src="/blog/js/ahaos-perf.js" defer></script>\n'
)


def main() -> None:
    html_files = sorted(BLOG.rglob("*.html"))
    injected = 0
    skipped = 0

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            skipped += 1
            continue
        idx = text.rfind("</head>")
        if idx == -1:
            print(f"[warn ] no </head> in {path.relative_to(ROOT)}")
            continue
        updated = text[:idx] + BLOCK + text[idx:]
        path.write_text(updated, encoding="utf-8")
        injected += 1
        print(f"[inject] {path.relative_to(ROOT)}")

    print(f"[done ] {injected} injected, {skipped} already had marker (total {len(html_files)} html).")


if __name__ == "__main__":
    main()
