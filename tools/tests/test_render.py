"""Markdown rendering: badges, chips, rows, and link hygiene."""
from __future__ import annotations

import pytest

from lib.render import (
    badge,
    entry_row,
    facet_chip,
    regulatory_badge,
    relative_link,
)


def test_badge_url_encodes_spaces(taxonomy):
    out = badge("Paper", "Nat Med 2023", "1f77b4", "https://example.org")
    assert "Nat%20Med%202023" in out
    assert out.startswith("[!["), "badge must be a linked image"


def test_badge_escapes_dashes(taxonomy):
    """shields.io treats a single dash as a separator; it must be doubled."""
    assert "state--of--the--art" in badge("x", "state-of-the-art", "blue", "https://e.org")


def test_regulatory_badge_is_gold_for_cleared_devices(taxonomy, make_entry):
    entry = make_entry(regulatory={
        "status": "fda-510k", "verified_on": "2026-08-01",
        "reference": "https://example.org/510k",
    })
    out = regulatory_badge(entry, taxonomy)
    assert "gold" in out
    assert "FDA" in out


def test_regulatory_badge_is_grey_for_research_use(taxonomy, make_entry):
    out = regulatory_badge(make_entry(), taxonomy)
    assert "grey" in out.lower()
    assert "RUO" in out


def test_regulatory_badge_target_is_relative_to_the_page(taxonomy, make_entry):
    """A badge on a nested browse page must climb back to the repo root."""
    assert "(browse/regulatory/ruo.md)" in regulatory_badge(make_entry(), taxonomy, depth=0)
    assert "(../../browse/regulatory/ruo.md)" in regulatory_badge(
        make_entry(), taxonomy, depth=2
    )


def test_regulatory_badge_prefers_the_primary_regulator_record(taxonomy, make_entry):
    entry = make_entry(regulatory={
        "status": "fda-510k", "verified_on": "2026-08-01",
        "reference": "https://accessdata.fda.gov/K123456",
    })
    assert "https://accessdata.fda.gov/K123456" in regulatory_badge(entry, taxonomy, depth=2)


def test_unverified_status_renders_red(taxonomy, make_entry):
    entry = make_entry(regulatory={"status": "unknown"})
    assert "red" in regulatory_badge(entry, taxonomy).lower()


def test_facet_chip_links_to_the_browse_page(taxonomy):
    chip = facet_chip("organs", "breast", taxonomy, depth=0)
    assert "browse/organ/breast.md" in chip
    assert "Breast" in chip


def test_facet_chip_from_nested_page_uses_relative_path(taxonomy):
    chip = facet_chip("organs", "breast", taxonomy, depth=2)
    assert "../../browse/organ/breast.md" in chip


def test_relative_link_from_repo_root():
    assert relative_link("browse/organ/breast.md", depth=0) == "browse/organ/breast.md"


@pytest.mark.parametrize("depth,expected", [
    (0, "browse/organ/breast.md"),
    (1, "../browse/organ/breast.md"),
    (2, "../../browse/organ/breast.md"),
])
def test_relative_link_climbs_to_root_then_descends(depth, expected):
    assert relative_link("browse/organ/breast.md", depth) == expected


def test_relative_link_round_trips_to_the_target(tmp_path):
    """The computed path must actually resolve back to the target file."""
    from pathlib import PurePosixPath

    target = "browse/organ/breast.md"
    for page, depth in (("README.md", 0), ("browse/all.md", 1),
                        ("browse/category/dataset.md", 2)):
        link = relative_link(target, depth)
        resolved = PurePosixPath(
            __import__("posixpath").normpath(
                str(PurePosixPath(page).parent / link)
            )
        )
        assert str(resolved) == target, f"from {page}: {link} → {resolved}"


def test_entry_row_is_a_single_line(taxonomy, make_entry):
    row = entry_row(make_entry(), taxonomy, depth=0)
    assert "\n" not in row, "a table row must not contain newlines"
    assert row.startswith("|") and row.endswith("|")


def test_entry_row_escapes_pipes_in_free_text(taxonomy, make_entry):
    row = entry_row(make_entry(tagline="a | b"), taxonomy, depth=0)
    assert "a \\| b" in row


def test_showcase_entries_carry_a_disclosure_badge(taxonomy, make_entry):
    row = entry_row(make_entry(showcase=True), taxonomy, depth=0)
    assert "maintainer" in row.lower()


def test_privacy_flag_is_surfaced_when_data_leaves(taxonomy, make_entry):
    row = entry_row(make_entry(sends_data_offsite=True), taxonomy, depth=0)
    assert "uploads" in row.lower() or "offsite" in row.lower()
