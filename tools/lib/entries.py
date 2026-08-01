"""Loading and normalising entry files."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

Entry = Mapping[str, Any]

# Optional fields and the value used when a file omits them. Applied on load so
# downstream code never has to guard against a missing key.
DEFAULTS: Mapping[str, Any] = {
    "subcategories": (),
    "tasks": (),
    "subspecialty": (),
    "organs": (),
    "modality": (),
    "granularity": (),
    "platforms": (),
    "maintainers": (),
    "related": (),
    "licence_notes": None,
    "self_hostable": None,
    "sends_data_offsite": None,
    "offline_capable": None,
    "hardware_floor": None,
    "bandwidth": None,
    "needs_scanner": None,
    "min_ram_gb": None,
    "clinician_note": None,
    "caveats": None,
    "featured": False,
    "showcase": False,
}

METRIC_FIELDS: tuple[str, ...] = (
    "github_stars", "last_commit", "hf_downloads", "refreshed_on",
)

# Key the loader attaches for error messages; stripped before serialisation.
SOURCE_KEY = "_source_file"


def apply_defaults(raw: Entry) -> dict[str, Any]:
    """Return a new dict with defaults filled in. Never mutates `raw`."""
    filled: dict[str, Any] = dict(raw)

    for key, default in DEFAULTS.items():
        if filled.get(key) is None:
            filled[key] = list(default) if isinstance(default, tuple) else default

    metrics = dict(filled.get("metrics") or {})
    filled["metrics"] = {field: metrics.get(field) for field in METRIC_FIELDS}

    # Flattened copy of the nested regulatory status so it can be faceted like
    # any other field. Underscore-prefixed, so public_view() strips it from
    # JSON output and schema validation never sees it.
    filled["_regulatory_status"] = (filled.get("regulatory") or {}).get("status", "unknown")
    return filled


def load_entries(directory: Path) -> tuple[dict[str, Any], ...]:
    """Load every *.yaml in `directory`, sorted by id.

    A malformed file raises with its path attached, so CI failures name the
    offending file rather than a line number in a merged stream.
    """
    directory = Path(directory)
    if not directory.is_dir():
        return ()

    loaded: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            with path.open(encoding="utf-8") as handle:
                raw = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise ValueError(f"{path.name}: invalid YAML — {exc}") from exc

        if not isinstance(raw, dict):
            raise ValueError(f"{path.name}: expected a mapping at the top level")

        entry = apply_defaults(raw)
        entry[SOURCE_KEY] = path.name
        loaded.append(entry)

    return tuple(sorted(loaded, key=lambda e: e.get("id", "")))


def public_view(entry: Entry) -> dict[str, Any]:
    """Entry without loader-internal keys, for JSON output."""
    return {k: v for k, v in entry.items() if not k.startswith("_")}
