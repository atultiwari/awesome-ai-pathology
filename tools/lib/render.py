"""Markdown rendering: badges, facet chips and table rows."""
from __future__ import annotations

from typing import Any, Mapping, Sequence
from urllib.parse import quote

from lib.entries import Entry
from lib.facets import derived_facets
from lib.taxonomy import BROWSE_DIR, Taxonomy

SHIELDS = "https://img.shields.io/badge"

# Link-type badges, in the order they appear in a row's resource cluster.
LINK_BADGES: tuple[tuple[str, str, str], ...] = (
    ("repo", "Code", "green"),
    ("paper", "Paper", "1f77b4"),
    ("docs", "Docs", "6A5ACD"),
    ("model", "Model", "orange"),
    ("dataset", "Data", "orange"),
    ("demo", "Demo", "ff69b4"),
    ("homepage", "Site", "ffb6c1"),
)


def shields_escape(text: str) -> str:
    """Escape for a shields.io path segment.

    shields.io reads `-` as a field separator and `_` as a space, so both must
    be doubled before percent-encoding.
    """
    return quote(text.replace("-", "--").replace("_", "__"), safe="")


def badge(label: str, message: str, colour: str, url: str, alt: str | None = None) -> str:
    """A linked shields.io badge."""
    src = f"{SHIELDS}/{shields_escape(label)}-{shields_escape(message)}-{colour}"
    return f"[![{alt or label}]({src})]({url})"


def relative_link(path_from_root: str, depth: int) -> str:
    """Rewrite a repo-root-relative path for a page `depth` directories down.

    Climb `depth` levels back to the repo root, then follow the full path from
    there. depth 0 is README.md, 1 is browse/all.md, 2 is browse/<kind>/<x>.md.
    """
    return ("../" * depth) + path_from_root


def facet_page_path(kind: str, value: str) -> str:
    return f"browse/{BROWSE_DIR[kind]}/{value}.md"


def facet_chip(kind: str, value: str, taxonomy: Taxonomy, depth: int) -> str:
    """A clickable tag linking to its facet page — the 'filter' mechanism."""
    label = taxonomy.label(kind, value) if taxonomy.has(kind, value) else value
    href = relative_link(facet_page_path(kind, value), depth)
    return f"[`{label}`]({href})"


def regulatory_badge(entry: Entry, taxonomy: Taxonomy, depth: int = 0) -> str:
    """Status badge. Gold = permits clinical use somewhere; red = unverified.

    Links to the regulator's primary record when there is one, otherwise to the
    facet page explaining what the status means.
    """
    status = (entry.get("regulatory") or {}).get("status", "unknown")
    if not taxonomy.has("regulatory", status):
        status = "unknown"

    meta = taxonomy.meta("regulatory", status)
    colour = meta.get("badge_colour", "lightgrey")
    short = meta.get("short", status)
    reference = (entry.get("regulatory") or {}).get("reference")
    target = reference or relative_link(facet_page_path("regulatory", status), depth)
    return badge("Status", short, colour, target, alt=meta.get("label", status))


def link_badges(entry: Entry) -> str:
    links = entry.get("links") or {}
    parts = [
        badge(label, "link", colour, links[key])
        for key, label, colour in LINK_BADGES
        if links.get(key)
    ]
    return " ".join(parts)


def escape_cell(text: str) -> str:
    """Make free text safe inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def entry_row(entry: Entry, taxonomy: Taxonomy, depth: int) -> str:
    """One Markdown table row. Always a single line."""
    name = escape_cell(entry.get("name", entry.get("id", "?")))
    home = (entry.get("links") or {}).get("homepage") or (entry.get("links") or {}).get("repo")
    title = f"**[{name}]({home})**" if home else f"**{name}**"

    flags = _flags(entry)
    what = escape_cell(entry.get("tagline", ""))
    chips = " ".join(
        facet_chip("tasks", task, taxonomy, depth) for task in entry.get("tasks", [])[:3]
    )

    cells = (
        title + (f" {flags}" if flags else ""),
        what,
        regulatory_badge(entry, taxonomy, depth),
        _cost_cell(entry),
        chips or "—",
        link_badges(entry) or "—",
    )
    return "| " + " | ".join(cells) + " |"


def table_header() -> str:
    return (
        "| Name | What it does | Status | Cost / Hardware | Tasks | Links |\n"
        "| --- | --- | --- | --- | --- | --- |"
    )


def _flags(entry: Entry) -> str:
    """Inline warning and disclosure markers.

    Dormancy is shown on every row, not only on the Stale Shelf page — the
    reader deciding whether to adopt something should not have to go looking.
    """
    marks: list[str] = []
    if entry.get("showcase"):
        marks.append("`built by the maintainer`")
    if entry.get("sends_data_offsite") is True:
        marks.append("⚠️ `uploads your data`")
    if entry.get("stage") == "deprecated":
        marks.append("`unmaintained`")
    elif "stale-shelf" in derived_facets(entry):
        last = (entry.get("metrics") or {}).get("last_commit")
        marks.append(f"🕯️ `dormant since {last[:7]}`" if last else "🕯️ `dormant`")
    return " ".join(marks)


def _cost_cell(entry: Entry) -> str:
    cost = entry.get("cost", "unknown")
    floor = entry.get("hardware_floor")
    facets = derived_facets(entry)
    bits = [cost.replace("-", " ")]
    if floor:
        bits.append(floor.replace("-", " "))
    if "low-resource" in facets:
        bits.append("🌍")
    return escape_cell(" · ".join(bits))


def render_table(entries: Sequence[Entry], taxonomy: Taxonomy, depth: int) -> str:
    if not entries:
        return "_Nothing here yet._"
    rows = "\n".join(entry_row(e, taxonomy, depth) for e in entries)
    return f"{table_header()}\n{rows}"


def counts_by(entries: Sequence[Entry], key: str) -> Mapping[str, int]:
    tally: dict[str, int] = {}
    for entry in entries:
        value: Any = entry.get(key)
        for item in (value,) if isinstance(value, str) else (value or ()):
            tally[item] = tally.get(item, 0) + 1
    return tally
