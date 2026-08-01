#!/usr/bin/env python3
"""Validate data/entries against the schema, the taxonomy and the house rules.

    python3 tools/validate.py                 # structural checks
    python3 tools/validate.py --check-links   # also verify every URL resolves
    python3 tools/validate.py --bot           # allow the metrics block to be set

Exit code 1 on any error. Warnings never fail the build.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.entries import SOURCE_KEY, load_entries  # noqa: E402
from lib.linkcheck import check_urls  # noqa: E402
from lib.taxonomy import load_taxonomy  # noqa: E402
from lib.validate_rules import (  # noqa: E402
    check_bot_owned_metrics,
    check_duplicate_ids,
    check_id_matches_filename,
    check_related_targets_exist,
    check_schema,
    check_verification_freshness,
    check_vocabularies,
)

ROOT = Path(__file__).resolve().parent.parent


def collect_urls(entries) -> list[tuple[str, str]]:
    """(source file, url) for every link on every entry, deduplicated by url."""
    seen: dict[str, str] = {}
    for entry in entries:
        where = entry.get(SOURCE_KEY, entry.get("id", "?"))
        for url in (entry.get("links") or {}).values():
            if url and url not in seen:
                seen[url] = where
        reference = (entry.get("regulatory") or {}).get("reference")
        if reference and reference not in seen:
            seen[reference] = where
    return [(where, url) for url, where in seen.items()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-links", action="store_true", help="verify every URL resolves")
    parser.add_argument("--bot", action="store_true", help="permit a populated metrics block")
    args = parser.parse_args()

    taxonomy = load_taxonomy(ROOT / "data" / "taxonomy")
    entries = load_entries(ROOT / "data" / "entries")

    if not entries:
        print("no entries found in data/entries", file=sys.stderr)
        return 1

    errors: list[str] = []
    errors += check_schema(entries, ROOT / "schema" / "entry.schema.json")
    errors += check_id_matches_filename(entries)
    errors += check_duplicate_ids(entries)
    errors += check_vocabularies(entries, taxonomy)
    errors += check_related_targets_exist(entries)
    errors += check_bot_owned_metrics(entries, bot_authored=args.bot)

    warnings = check_verification_freshness(entries, today=date.today().isoformat())

    if args.check_links:
        link_errors, link_warnings = check_urls(collect_urls(entries))
        errors += [str(r) for r in link_errors]
        warnings += [str(r) for r in link_warnings]

    for warning in warnings:
        print(f"warning: {warning}")

    if errors:
        print(f"\n{len(errors)} error(s):\n", file=sys.stderr)
        for error in errors:
            print(f"  ✗ {error}", file=sys.stderr)
        return 1

    print(f"✓ {len(entries)} entries valid"
          + (f" · {len(warnings)} warning(s)" if warnings else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
