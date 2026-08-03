#!/usr/bin/env python3
"""List digest issues and their review state, and mark one reviewed.

    python3 tools/review_digest.py                    # what is still pending
    python3 tools/review_digest.py --mark 2026-W32    # mark one reviewed
    python3 tools/review_digest.py --mark all         # mark every pending one

Issues are published as soon as they are assembled, so the week's material is
current. Reading happens afterwards, in whatever order suits — including back
issues. Marking an issue reviewed swaps its banner and clears it from the
pending list.

Edit the issue itself first if anything needs cutting or rewriting; this only
changes the label.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIGEST_DIR = ROOT / "digest"

STATE_RE = re.compile(r"<!--\s*review-state:\s*(\w+)\s*-->")
TITLE_RE = re.compile(r"^# (.+)$", re.MULTILINE)

PENDING_SUFFIX = "  ·  *awaiting review*"

REVIEWED_BANNER = (
    "> **Reviewed by Dr. Atul Tiwari on {when}.** Candidates are discovered "
    "automatically; what appears here was read and selected. Inclusion is still not "
    "endorsement, and nothing below has been validated for clinical use."
)


def issues() -> list[tuple[Path, str, str]]:
    """(path, state, title) for every issue, newest first. Excludes -full listings."""
    if not DIGEST_DIR.is_dir():
        return []
    out = []
    for path in sorted(DIGEST_DIR.glob("*.md"), reverse=True):
        if path.stem.endswith("-full") or path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        state = (STATE_RE.search(text).group(1) if STATE_RE.search(text) else "reviewed")
        title = TITLE_RE.search(text).group(1) if TITLE_RE.search(text) else path.stem
        out.append((path, state, title))
    return out


def mark_reviewed(path: Path, when: str) -> bool:
    """Swap an issue from pending to reviewed. Returns False if already reviewed."""
    text = path.read_text(encoding="utf-8")
    if "review-state: pending" not in text:
        return False

    text = text.replace("<!-- review-state: pending -->", "<!-- review-state: reviewed -->")
    text = text.replace(PENDING_SUFFIX, "")

    # Replace the whole awaiting-review blockquote with the reviewed one-liner.
    lines = text.splitlines()
    out, skipping = [], False
    for line in lines:
        if line.startswith("> [!NOTE]"):
            skipping = True
            out.append(REVIEWED_BANNER.format(when=when))
            continue
        if skipping:
            if line.startswith(">"):
                continue
            skipping = False
        out.append(line)

    path.write_text("\n".join(out), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mark", metavar="WEEK",
                        help="issue to mark reviewed, e.g. 2026-W32, or 'all'")
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="review date to record (default: today)")
    args = parser.parse_args()

    found = issues()
    if not found:
        print("no digest issues yet")
        return 0

    if not args.mark:
        pending = [i for i in found if i[1] == "pending"]
        for path, state, title in found:
            flag = "⏳ pending " if state == "pending" else "✅ reviewed"
            print(f"  {flag}  {path.name:20}  {title[:60]}")
        print(f"\n{len(pending)} of {len(found)} awaiting review.")
        if pending:
            print(f"Mark one:  python3 tools/review_digest.py --mark {pending[0][0].stem}")
        return 0

    targets = ([i for i in found if i[1] == "pending"] if args.mark == "all"
               else [i for i in found if i[0].stem == args.mark])
    if not targets:
        print(f"no pending issue matching {args.mark!r}", file=sys.stderr)
        return 1

    for path, _, title in targets:
        if mark_reviewed(path, args.date):
            print(f"✓ marked reviewed: {path.name}")
        else:
            print(f"  already reviewed: {path.name}")

    print("\nRun tools/generate.py to refresh the README.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
