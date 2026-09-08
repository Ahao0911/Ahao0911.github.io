#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_links.py — Static link audit for the Ahao0911.github.io homepage.

Scans every *.html file under the repository root, extracts href/src
attributes that point at root-absolute internal paths (e.g. /blog/..., /css/...),
and verifies each target exists (or returns HTTP 200 through a local server).

Run:  python _tools/check_links.py
"""
from __future__ import annotations

import functools
import http.server
import pathlib
import re
import socketserver
import sys
import threading
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8765

ATTR_RE = re.compile(r'(?:href|src|data-original)\s*=\s*"([^"]+)"', re.IGNORECASE)
ROOT_PATH_RE = re.compile(r"^/[^/].*$")


def iter_html_files():
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        yield path


def strip_url(url: str) -> str:
    """Remove fragment/query and percent-decode a root-relative URL."""
    url = url.split("#", 1)[0].split("?", 1)[0]
    return urllib.parse.unquote(url)


def resolve_local(url: str) -> pathlib.Path | None:
    """Map a root-relative URL like /blog/foo/ to a local file path."""
    stripped = strip_url(url)
    if stripped == "/":
        candidate = ROOT / "index.html"
        return candidate if candidate.is_file() else None
    if stripped.endswith("/"):
        stripped += "index.html"
    rel = stripped.lstrip("/")
    candidate = ROOT / rel
    return candidate if candidate.is_file() else None


def main() -> int:
    broken: list[str] = []
    external = 0
    checked = 0
    unique_internal: dict[str, str] = {}  # url -> first file referencing it

    for html_file in iter_html_files():
        try:
            text = html_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for url in ATTR_RE.findall(text):
            url = url.strip()
            if not url or url.startswith(("#", "//", "mailto:", "tel:", "data:", "javascript:")):
                continue
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme in ("http", "https"):
                external += 1
                continue
            if url == "/" or ROOT_PATH_RE.match(url):
                checked += 1
                key = url.split("#", 1)[0]
                unique_internal.setdefault(key, str(html_file.relative_to(ROOT)))
                if resolve_local(url) is None:
                    broken.append(f"{url}   (referenced by {html_file.relative_to(ROOT)})")
                continue
            # relative URL (not starting with /) — flag for manual review
            print(f"[rel? ] {html_file.relative_to(ROOT)} -> {url}")
            continue

    print(f"\nScanned internal root-absolute links : {checked} (external skipped: {external})")
    print(f"Unique internal URLs                : {len(unique_internal)}")
    if broken:
        print(f"\n[FAIL] Broken internal links: {len(broken)}")
        for item in broken:
            print("   -", item)
        return 1

    # ---- live HTTP verification over python http.server ----
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    handler = functools.partial(QuietHandler, directory=str(ROOT))

    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        http_fail = []
        try:
            for url in sorted(unique_internal):
                req_url = "http://127.0.0.1:%d%s" % (PORT, url.split("#", 1)[0])
                try:
                    with urllib.request.urlopen(req_url, timeout=10) as resp:
                        if resp.status != 200:
                            http_fail.append(f"{url} -> HTTP {resp.status}")
                except Exception as exc:  # noqa: BLE001
                    http_fail.append(f"{url} -> {exc}")
        finally:
            httpd.shutdown()
            httpd.server_close()

    if http_fail:
        print(f"\n[FAIL] HTTP check failed for {len(http_fail)} URL(s):")
        for item in http_fail[:40]:
            print("   -", item)
        if len(http_fail) > 40:
            print(f"   ... and {len(http_fail) - 40} more")
        return 1

    print("[PASS] All internal links exist and return HTTP 200.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
