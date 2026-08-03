#!/usr/bin/env python3
"""Generate README.md, browse/ facet pages and api/v1/*.json from data/entries.

    python3 tools/generate.py            # write the files
    python3 tools/generate.py --check    # fail if anything is out of date (CI)

Everything this writes is derived. data/entries/*.yaml is the source of truth.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.entries import load_entries  # noqa: E402
from lib.pages import (  # noqa: E402
    api_documents, api_index_html, browse_pages, readme, today_iso,
)
from lib.taxonomy import load_taxonomy  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIRS = ("browse", "api")


def build() -> dict[str, str]:
    """All generated files, keyed by repo-relative path."""
    taxonomy = load_taxonomy(ROOT / "data" / "taxonomy")
    entries = load_entries(ROOT / "data" / "entries")
    if not entries:
        raise SystemExit("no entries found in data/entries")

    today = today_iso()
    files = {
        "README.md": readme(entries, taxonomy, ROOT),
        # Landing page for the Pages host, so its root is not a bare 404.
        "index.html": api_index_html(entries, taxonomy, today),
        # Pages would otherwise run the output through Jekyll, which ignores
        # any path beginning with an underscore and rewrites some files.
        ".nojekyll": "",
    }
    files.update(browse_pages(entries, taxonomy))
    files.update(api_documents(entries, taxonomy, today, ROOT))
    return files


def write(files: dict[str, str]) -> int:
    for directory in GENERATED_DIRS:
        shutil.rmtree(ROOT / directory, ignore_errors=True)

    for relative, content in sorted(files.items()):
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return len(files)


def check(files: dict[str, str]) -> list[str]:
    """Paths whose on-disk content differs from what the generator produces.

    `generated_at` changes every day, so a date-only difference is ignored —
    otherwise CI would fail every midnight on an untouched repo.
    """
    stale = []
    for relative, expected in sorted(files.items()):
        path = ROOT / relative
        if not path.is_file():
            stale.append(f"{relative} (missing)")
            continue
        actual = path.read_text(encoding="utf-8")
        if _strip_timestamps(actual) != _strip_timestamps(expected):
            stale.append(relative)
    return stale


def _strip_timestamps(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines()
        if '"generated_at"' not in line and "generated 2" not in line
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify generated files are current; write nothing")
    args = parser.parse_args()

    files = build()

    if args.check:
        stale = check(files)
        if stale:
            print("generated files are out of date — run tools/generate.py:", file=sys.stderr)
            for path in stale:
                print(f"  ✗ {path}", file=sys.stderr)
            return 1
        print(f"✓ {len(files)} generated files are current")
        return 0

    count = write(files)
    print(f"✓ wrote {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
