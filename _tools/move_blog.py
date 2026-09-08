#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
move_blog.py — One-time migration script.

Moves the legacy Hexo blog (AhaosBlog) from the repository root into /blog/
and rewrites every root-absolute internal reference so the blog keeps working
when served under the /blog/ prefix:

  /css/        -> /blog/css/
  /js/         -> /blog/js/
  /img/        -> /blog/img/
  /assets/     -> /blog/assets/
  /about/      -> /blog/about/
  /archives/   -> /blog/archives/
  /tags/       -> /blog/tags/
  /categories/ -> /blog/categories/
  /link/       -> /blog/link/
  /search.xml  -> /blog/search.xml
  /2022/       -> /blog/2022/
  /2023/       -> /blog/2023/

Safe guards:
  * Only rewrites root-absolute paths (no full URLs / protocol-relative URLs
    such as https://... or //cdn.jsdelivr.net/... get touched).
  * Never touches .git, CNAME, _tools/ or this script itself.
  * The homepage anchor "/" (used by the blog's "主页" menu item) is kept
    intentionally so it points at the new personal homepage.

Run from anywhere:  python _tools/move_blog.py
It is safe to re-run; already-moved content is skipped.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
TOOLS = ROOT / "_tools"

# Top-level entries that must stay where they are.
KEEP = {".git", "CNAME", "_tools", "blog"}

# Old root-absolute prefix -> new blog-prefixed path.
REWRITE_MAP = [
    ("/css/", "/blog/css/"),
    ("/js/", "/blog/js/"),
    ("/img/", "/blog/img/"),
    ("/assets/", "/blog/assets/"),
    ("/about/", "/blog/about/"),
    ("/archives/", "/blog/archives/"),
    ("/tags/", "/blog/tags/"),
    ("/categories/", "/blog/categories/"),
    ("/link/", "/blog/link/"),
    ("/2022/", "/blog/2022/"),
    ("/2023/", "/blog/2023/"),
    ("/search.xml", "/blog/search.xml"),
]

# File extensions whose content should be rewritten.
TEXT_EXTENSIONS = {".html", ".htm", ".xml", ".js", ".css", ".json", ".txt"}

# Root-absolute refs start right after a quote/paren/space/etc., and must NOT
# follow a word character or '.' (which would make them part of a full URL
# like http://example.com/about/ or a protocol-relative //cdn.../css/ link).
_PRECEDING_BLOCK = re.compile(r"(?<![\w.\-/])")


def _rewrite(content: str) -> str:
    """Rewrite root-absolute blog paths inside text content."""
    for old, new in REWRITE_MAP:
        pattern = _PRECEDING_BLOCK.pattern + re.escape(old)
        content = re.sub(pattern, new, content)
    return content


def _is_text(path: pathlib.Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def move_entries() -> None:
    """Move every keep-out entry from the repo root into /blog."""
    BLOG.mkdir(parents=True, exist_ok=True)
    moved = []
    for entry in sorted(ROOT.iterdir(), key=lambda p: p.name):
        if entry.name in KEEP:
            continue
        target = BLOG / entry.name
        if target.exists():
            print(f"[skip ] {entry.name} -> already inside blog/")
            continue
        shutil.move(str(entry), str(target))
        moved.append(entry.name)
        print(f"[move ] {entry.name} -> blog/{entry.name}")
    if not moved:
        print("[info ] nothing new to move.")


def rewrite_files() -> None:
    """Rewrite internal references in every moved text file under /blog."""
    if not BLOG.exists():
        print("[error] blog/ does not exist; run move_entries() first.")
        sys.exit(1)
    changed = 0
    for path in sorted(BLOG.rglob("*")):
        if not path.is_file() or not _is_text(path):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            # Binary-ish or non-UTF8 text; leave untouched.
            continue
        rewritten = _rewrite(original)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")
            changed += 1
            print(f"[rewr ] {path.relative_to(ROOT)}")
    print(f"[info ] {changed} file(s) rewritten.")


def adjust_blog_home() -> None:
    """Point the AhaosBlog brand back to /blog/ while '主页' keeps pointing at '/'.

    After migration the blog brand link should stay inside the blog, otherwise
    both brand and 主页 would jump to the new personal homepage.
    """
    blog_index = BLOG / "index.html"
    if not blog_index.exists():
        print("[warn ] blog/index.html missing; skip brand fix.")
        return
    original = blog_index.read_text(encoding="utf-8")
    updated = original.replace(
        '<a id="site-name" href="/">AhaosBlog</a>',
        '<a id="site-name" href="/blog/">AhaosBlog</a>',
    )
    if updated != original:
        blog_index.write_text(updated, encoding="utf-8")
        print("[fix  ] blog/index.html brand link -> /blog/")


def verify() -> None:
    """Print a quick summary of the resulting top-level layout."""
    print("\n[verify] repo root now contains:")
    for entry in sorted(ROOT.iterdir(), key=lambda p: p.name):
        kind = "dir " if entry.is_dir() else "file"
        print(f"        {kind}  {entry.name}")
    print(f"[verify] blog/ contains {sum(1 for _ in BLOG.rglob('*'))} entry/entries.")


def main() -> None:
    print(f"repo root : {ROOT}")
    print(f"blog dir  : {BLOG}")
    move_entries()
    rewrite_files()
    adjust_blog_home()
    verify()
    print("\ndone. Now build the new personal homepage files at the repo root.")


if __name__ == "__main__":
    main()
