#!/usr/bin/env python3
"""Mirror the editor's workshop schedule into api/v1/workshops.json.

    python3 tools/refresh_workshops.py

The digest's closing page names who compiles it and where he teaches the
hands-on part. That listing must be current every week without anyone editing
it, so it is read from the workshops site and republished here as JSON — which
is what the website and the digest actually consume. Nothing else in this
repository depends on it, and a failure here never blocks an issue.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.workshops import WorkshopsError, document, fetch, parse  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "api" / "v1" / "workshops.json"


def main() -> int:
    try:
        workshops = parse(fetch())
    except WorkshopsError as error:
        # Loudly. A silent failure would leave last week's dates in print,
        # which is worse than a red build.
        print(f"✗ {error}", file=sys.stderr)
        return 1

    payload = document(workshops, date.today().isoformat())
    if TARGET.exists() and TARGET.read_text(encoding="utf-8") == payload:
        print(f"✓ {len(workshops)} workshops, unchanged")
        return 0

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(payload, encoding="utf-8")
    print(f"✓ {len(workshops)} workshops written to {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
