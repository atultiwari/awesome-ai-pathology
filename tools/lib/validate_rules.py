"""Validation rules. Each returns a list of human-readable error strings.

Rules are pure functions over already-loaded entries so they can be unit tested
without touching the filesystem.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from jsonschema import Draft202012Validator

from lib.entries import METRIC_FIELDS, SOURCE_KEY, Entry, public_view
from lib.taxonomy import FIELD_VOCABULARY, Taxonomy

# Fields validated against a taxonomy, and whether they hold a list.
_LIST_FIELDS = frozenset({"tasks", "subspecialty", "organs", "audience"})


def check_schema(entries: Sequence[Entry], schema_path: Path) -> list[str]:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    errors: list[str] = []
    for entry in entries:
        where = entry.get(SOURCE_KEY, entry.get("id", "<unknown>"))
        for failure in sorted(validator.iter_errors(public_view(entry)), key=str):
            location = ".".join(str(p) for p in failure.absolute_path) or "(root)"
            errors.append(f"{where}: {location}: {failure.message}")
    return errors


def check_id_matches_filename(entries: Sequence[Entry]) -> list[str]:
    errors = []
    for entry in entries:
        source = entry.get(SOURCE_KEY)
        if source is None:
            continue
        expected = source[: -len(".yaml")] if source.endswith(".yaml") else source
        if entry.get("id") != expected:
            errors.append(
                f"{source}: id is {entry.get('id')!r} but the filename implies {expected!r}"
            )
    return errors


def check_duplicate_ids(entries: Sequence[Entry]) -> list[str]:
    seen: dict[str, int] = {}
    for entry in entries:
        key = entry.get("id", "")
        seen[key] = seen.get(key, 0) + 1
    return [f"duplicate id {key!r} used by {count} entries"
            for key, count in seen.items() if count > 1]


def check_vocabularies(entries: Sequence[Entry], taxonomy: Taxonomy) -> list[str]:
    """Unknown tag values fail the build — this is what stops vocabulary drift."""
    errors: list[str] = []
    for entry in entries:
        where = entry.get(SOURCE_KEY, entry.get("id", "<unknown>"))
        for field, kind in FIELD_VOCABULARY.items():
            for value in _as_tuple(entry.get(field), field):
                if not taxonomy.has(kind, value):
                    errors.append(
                        f"{where}: {field}: {value!r} is not in {kind}.yaml"
                    )

        status = (entry.get("regulatory") or {}).get("status")
        if status and not taxonomy.has("regulatory", status):
            errors.append(f"{where}: regulatory.status: {status!r} is not in regulatory.yaml")
    return errors


def check_related_targets_exist(entries: Sequence[Entry]) -> list[str]:
    known = {entry.get("id") for entry in entries}
    errors = []
    for entry in entries:
        where = entry.get(SOURCE_KEY, entry.get("id", "<unknown>"))
        for target in entry.get("related", ()):
            if target not in known:
                errors.append(f"{where}: related: no entry with id {target!r}")
    return errors


def check_bot_owned_metrics(entries: Sequence[Entry], bot_authored: bool) -> list[str]:
    """The metrics block belongs to the nightly job.

    Hand-editing it produces conflicts between bot commits and human PRs, so a
    human-authored change carrying non-null metrics is rejected.
    """
    if bot_authored:
        return []

    errors = []
    for entry in entries:
        metrics = entry.get("metrics") or {}
        populated = [f for f in METRIC_FIELDS if metrics.get(f) is not None]
        if populated:
            where = entry.get(SOURCE_KEY, entry.get("id", "<unknown>"))
            errors.append(
                f"{where}: metrics is bot-owned; leave "
                f"{', '.join(populated)} null (the nightly job fills it)"
            )
    return errors


def check_verification_freshness(
    entries: Sequence[Entry], today: str, max_age_days: int = 365
) -> list[str]:
    """Warn when a regulatory claim has gone stale. Returns warnings, not errors."""
    from datetime import date

    cutoff = date.fromisoformat(today)
    warnings = []
    for entry in entries:
        verified = (entry.get("regulatory") or {}).get("verified_on")
        if not verified:
            continue
        age = (cutoff - date.fromisoformat(verified)).days
        if age > max_age_days:
            where = entry.get(SOURCE_KEY, entry.get("id", "<unknown>"))
            warnings.append(
                f"{where}: regulatory status last verified {age} days ago — re-check"
            )
    return warnings


def _as_tuple(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if field in _LIST_FIELDS or isinstance(value, list):
        return tuple(value)
    return (value,)
