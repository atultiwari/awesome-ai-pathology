"""Facet computation.

Resource-tier facets are DERIVED from entry fields rather than hand-tagged, so
they can never contradict the underlying data (PLAN §3). A null field means
"not established" and must never satisfy a predicate — absence is not a yes.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Mapping, Sequence

from lib.entries import Entry

LAPTOP_HARDWARE = frozenset({"cpu", "consumer-gpu"})
FREE_COSTS = frozenset({"free", "free-for-academic"})

# An upstream repository silent for this long is treated as dormant. Long
# enough that a stable, finished tool is not wrongly shamed; short enough that
# genuinely abandoned work is visible.
STALE_AFTER_DAYS = 550


def _runs_on_laptop(entry: Entry) -> bool:
    return entry.get("hardware_floor") in LAPTOP_HARDWARE


def _works_offline(entry: Entry) -> bool:
    return entry.get("offline_capable") is True and entry.get("sends_data_offsite") is False


def _no_scanner_needed(entry: Entry) -> bool:
    return entry.get("needs_scanner") is False


def _low_resource(entry: Entry) -> bool:
    return (
        entry.get("cost") in FREE_COSTS
        and _runs_on_laptop(entry)
        and entry.get("offline_capable") is True
        and _no_scanner_needed(entry)
    )


def _stale(entry: Entry) -> bool:
    """Marked deprecated, or upstream has been quiet for a long time.

    Being honest about dead projects is the point — an awesome list that hides
    them is worse than useless, because the reader assumes everything listed is
    alive. An entry with no last_commit is NOT stale: absence of evidence is not
    evidence of abandonment.
    """
    if entry.get("stage") == "deprecated":
        return True

    last_commit = (entry.get("metrics") or {}).get("last_commit")
    if not last_commit:
        return False
    return _days_since(last_commit) > STALE_AFTER_DAYS


def _days_since(iso_date: str) -> float:
    from datetime import date

    try:
        then = date.fromisoformat(str(iso_date)[:10])
    except ValueError:
        return 0.0
    return (date.today() - then).days


DERIVED: Mapping[str, Callable[[Entry], bool]] = {
    "runs-on-laptop": _runs_on_laptop,
    "works-offline": _works_offline,
    "no-scanner-needed": _no_scanner_needed,
    "low-resource": _low_resource,
    "stale-shelf": _stale,
}


def derived_facets(entry: Entry) -> tuple[str, ...]:
    """Resource-tier facet names this entry qualifies for."""
    return tuple(name for name, predicate in DERIVED.items() if predicate(entry))


def facet_index(
    entries: Sequence[Entry], field: str
) -> dict[str, tuple[dict[str, Any], ...]]:
    """Group entries by each value of a list- or scalar-valued field.

    Entries with no value for the field appear in no group. Order within a
    group follows the input order, which the loader has already sorted by id.
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        for value in _values_of(entry, field):
            grouped[value].append(dict(entry))
    return {key: tuple(items) for key, items in grouped.items()}


def derived_index(
    entries: Sequence[Entry],
) -> dict[str, tuple[dict[str, Any], ...]]:
    """Group entries by derived resource-tier facet."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        for name in derived_facets(entry):
            grouped[name].append(dict(entry))
    return {key: tuple(items) for key, items in grouped.items()}


def _values_of(entry: Entry, field: str) -> tuple[str, ...]:
    value = entry.get(field)
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(value)
