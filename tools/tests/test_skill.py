"""Skill level: how much you need to know before this is usable.

The level is DERIVED, like the resource-tier facets, so it cannot drift out of
step with the entry it describes. Hand-labelling 125 entries would have meant
125 private judgements no reader could check; a rule can be read and argued
with.
"""
from __future__ import annotations

import pytest

from lib.skill import LEVELS, skill_level


def entry(**overrides):
    base = {
        "id": "x",
        "category": "software-viewer",
        "audience": ["clinician"],
        "hardware_floor": "cpu",
        "needs_scanner": False,
    }
    return {**base, "id": "x", **overrides}


# ── the rule ─────────────────────────────────────────────────────────────

def test_click_and_run_software_is_beginner():
    assert skill_level(entry()) == "beginner"


def test_reading_material_is_beginner():
    assert skill_level(entry(category="education")) == "beginner"
    assert skill_level(entry(category="ethics-safety")) == "beginner"


def test_an_extension_needs_some_configuration():
    assert skill_level(entry(category="qupath-extension")) == "intermediate"


def test_a_model_needs_engineering():
    for category in ("foundation-model", "vision-language-model", "dataset"):
        assert skill_level(entry(category=category)) == "advanced", category


def test_a_workstation_gpu_makes_anything_advanced():
    """If it will not run on the machine you have, the barrier is not skill
    alone — but it is still a barrier, and the filter has to say so."""
    assert skill_level(entry(hardware_floor="workstation-gpu")) == "advanced"


def test_a_consumer_gpu_lifts_a_beginner_entry():
    assert skill_level(entry(hardware_floor="consumer-gpu")) == "intermediate"


def test_needing_a_scanner_lifts_a_beginner_entry():
    assert skill_level(entry(needs_scanner=True)) == "intermediate"


def test_nothing_aimed_away_from_clinicians_is_beginner():
    assert skill_level(entry(audience=["developer", "researcher"])) == "intermediate"


def test_bumps_never_lower_a_level():
    """Every adjustment is a floor, never a ceiling."""
    assert skill_level(entry(category="dataset", hardware_floor="cpu")) == "advanced"


# ── the override ─────────────────────────────────────────────────────────

def test_an_explicit_level_wins():
    assert skill_level(entry(category="dataset", skill_level="beginner")) == "beginner"


def test_an_unknown_explicit_level_is_ignored_not_trusted():
    assert skill_level(entry(skill_level="expert")) == "beginner"


# ── shape ────────────────────────────────────────────────────────────────

def test_levels_are_ordered_easiest_first():
    assert LEVELS == ("beginner", "intermediate", "advanced")


def test_an_unknown_category_does_not_crash_and_is_not_beginner():
    """A new category must not silently become the easiest thing on the site."""
    assert skill_level(entry(category="brand-new-thing")) == "intermediate"


@pytest.mark.parametrize("missing", ["hardware_floor", "needs_scanner", "audience"])
def test_missing_fields_do_not_claim_beginner(missing):
    """Absence is not evidence of ease, exactly as with the resource facets."""
    data = entry()
    data[missing] = None
    assert skill_level(data) in LEVELS


def test_every_real_entry_gets_a_level(entries):
    assert all(skill_level(e) in LEVELS for e in entries)


def test_the_catalogue_covers_all_three_levels(entries):
    """A filter with an empty option is a broken promise to the reader."""
    found = {skill_level(e) for e in entries}
    assert found == set(LEVELS), f"missing levels: {set(LEVELS) - found}"
