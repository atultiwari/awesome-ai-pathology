"""Skill level: how much you need to know before an entry is usable to you.

A pathologist opening this library wants to know, before anything else,
whether a thing is something they can install this afternoon or something that
needs an ML engineer. That is the question this answers.

The level is DERIVED from fields the entry already carries, for the same
reason the resource-tier facets are (PLAN §3): a hand-written label is a
private judgement no reader can check, and it drifts the moment the entry
changes. A rule can be read, disagreed with, and corrected once for everyone.

An entry may still set `skill_level` explicitly when the rule is wrong about
it — the override is the escape hatch, not the norm.
"""
from __future__ import annotations

from typing import Mapping

from lib.entries import Entry

#: Easiest first. Order matters: the bumps below take the maximum.
LEVELS: tuple[str, ...] = ("beginner", "intermediate", "advanced")

_RANK: Mapping[str, int] = {name: i for i, name in enumerate(LEVELS)}

#: What each level means to a reader deciding whether to click. Written for a
#: pathologist, not for an engineer.
SKILL_LABELS: Mapping[str, Mapping[str, str]] = {
    "beginner": {
        "label": "Beginner",
        "description": "Install it and open it, or just read it. No code.",
    },
    "intermediate": {
        "label": "Intermediate",
        "description": "Some setup: a plugin, a config file, a scanner, or a "
                       "graphics card you probably already have.",
    },
    "advanced": {
        "label": "Advanced",
        "description": "You or a collaborator will be writing code and "
                       "handling models, data or a server.",
    },
}

# Install it, open it, or read it. No code, no pipeline.
_READY = frozenset({
    "software-viewer",
    "app",
    "education",
    "prompt-skill",
    "meta",
    "commercial-product",
    "ethics-safety",
    "validation-regulatory",
    "hardware-lowresource",
})

# Usable without writing a model, but there is configuration, a plugin to
# install, a server to point at something, or a format to wire up.
_CONFIGURE = frozenset({
    "qupath-extension",
    "agent-mcp",
    "standard-interop",
    "library-framework",
})

# You will be writing code and handling weights, data, or evaluation.
_BUILD = frozenset({
    "foundation-model",
    "vision-language-model",
    "task-specific-model",
    "spatial-omics",
    "benchmark",
    "dataset",
})


def _baseline(category: str | None) -> str:
    if category in _READY:
        return "beginner"
    if category in _BUILD:
        return "advanced"
    # _CONFIGURE, and anything unrecognised. A category added later must not
    # default to the easiest thing on the site just because nobody has
    # classified it yet.
    return "intermediate"


def skill_level(entry: Entry) -> str:
    """The level a reader needs to get value out of this entry."""
    explicit = entry.get("skill_level")
    if explicit in _RANK:
        return str(explicit)

    level = _baseline(entry.get("category"))

    # Each of these is a FLOOR. None of them can make an entry easier than its
    # category already says it is.
    if entry.get("hardware_floor") == "workstation-gpu":
        level = _at_least(level, "advanced")
    if entry.get("hardware_floor") == "consumer-gpu":
        level = _at_least(level, "intermediate")
    if entry.get("needs_scanner") is True:
        level = _at_least(level, "intermediate")
    if "clinician" not in (entry.get("audience") or []):
        level = _at_least(level, "intermediate")

    return level


def _at_least(current: str, floor: str) -> str:
    return current if _RANK[current] >= _RANK[floor] else floor
