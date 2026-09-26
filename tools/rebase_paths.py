"""Rewrite root-absolute "/main/..." asset URLs in the game bundles so they resolve
under the GitHub Pages project subpath (e.g. "/jackbox.tv.dump/main/...").

The bundles were built for https://jackbox.tv/ where "/main/" is at the domain root.
Only occurrences directly after a quote, backtick or "url(" are touched, and the
rewrite is idempotent (already-prefixed paths are left alone).

Usage: python tools/rebase_paths.py [--check]
"""
import pathlib
import re
import sys

PREFIX = "/jackbox.tv.dump"
ROOT = pathlib.Path(__file__).resolve().parent.parent
PATTERN = re.compile(r"""(?<=["'`(])/main/""")


def main():
    check = "--check" in sys.argv
    total = 0
    for path in sorted((ROOT / "main").rglob("*")):
        if path.suffix not in {".js", ".css", ".json", ".html"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        new, n = PATTERN.subn(PREFIX + "/main/", text)
        if n:
            total += n
            print(f"{n:5}  {path.relative_to(ROOT)}")
            if not check:
                path.write_text(new, encoding="utf-8", newline="")
    print(f"{'would rewrite' if check else 'rewrote'} {total} references")


if __name__ == "__main__":
    main()
