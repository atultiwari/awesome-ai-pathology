#!/usr/bin/env python3
"""Refresh the bot-owned metrics block on every entry.

    python3 tools/refresh_metrics.py            # write updated metrics
    python3 tools/refresh_metrics.py --dry-run  # report only, change nothing

Set GITHUB_TOKEN to raise the API rate limit from 60 to 5,000 requests/hour.
A failed lookup leaves the previous value in place — a transient outage must
never make a live project look abandoned.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.entries import load_entries  # noqa: E402
from lib.metrics import refresh, write_back  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args()

    entries_dir = ROOT / "data" / "entries"
    entries = load_entries(entries_dir)
    if not entries:
        print("no entries found", file=sys.stderr)
        return 1

    print(f"refreshing metrics for {len(entries)} entries…")
    updated, tally = refresh(entries, today=date.today().isoformat())

    print(f"  github lookups ok: {tally['github']}")
    print(f"  hugging face ok:   {tally['huggingface']}")
    print(f"  no source url:     {tally['skipped']}")
    print(f"  failed:            {tally['failed']}")

    if args.dry_run:
        print("\ndry run — nothing written")
        return 0

    changed = write_back(updated, entries_dir)
    print(f"\n✓ {changed} entr{'y' if changed == 1 else 'ies'} updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
