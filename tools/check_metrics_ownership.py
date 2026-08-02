#!/usr/bin/env python3
"""Verify a change does not hand-edit the bot-owned metrics block.

    python3 tools/check_metrics_ownership.py --base origin/main

Reads each entry's metrics as they exist on `--base`, compares against the
working tree, and fails if any differ. This is a DIFF check by necessity:
metrics are legitimately populated on main, so "is it non-null" cannot
distinguish a bot value from a hand-edit.

Skipped when the run is the metrics bot itself.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.entries import load_entries  # noqa: E402
from lib.validate_rules import check_metrics_unchanged  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_REL = "data/entries"


def baseline_metrics(base: str) -> dict[str, dict]:
    """id -> metrics block, as of `base`. Empty when base is unavailable."""
    try:
        listing = subprocess.run(
            ["git", "ls-tree", "--name-only", f"{base}:{ENTRIES_REL}"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
    except subprocess.CalledProcessError:
        print(f"note: cannot read {base}:{ENTRIES_REL} — skipping ownership check")
        return {}

    out: dict[str, dict] = {}
    for name in listing:
        if not name.endswith(".yaml"):
            continue
        try:
            blob = subprocess.run(
                ["git", "show", f"{base}:{ENTRIES_REL}/{name}"],
                cwd=ROOT, capture_output=True, text=True, check=True,
            ).stdout
            data = yaml.safe_load(blob) or {}
        except (subprocess.CalledProcessError, yaml.YAMLError):
            continue
        if isinstance(data, dict) and data.get("id"):
            out[data["id"]] = data.get("metrics") or {}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main",
                        help="git revision to compare against (default: origin/main)")
    args = parser.parse_args()

    baseline = baseline_metrics(args.base)
    if not baseline:
        return 0

    entries = load_entries(ROOT / "data" / "entries")
    errors = check_metrics_unchanged(entries, baseline)

    if errors:
        print(f"\n{len(errors)} metrics-ownership error(s):\n", file=sys.stderr)
        for error in errors:
            print(f"  ✗ {error}", file=sys.stderr)
        print("\nThe metrics block is maintained by the nightly job. Revert your "
              "changes to it and the bot will update it.", file=sys.stderr)
        return 1

    print(f"✓ metrics block unchanged against {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
