"""Generated output must be stable across days.

A generated file that embeds the current date changes every night regardless of
content, so the nightly regenerate job commits a no-op every day. Worse, it
makes `generate.py --check` unreliable as a signal that content is current.

Only api/v1/*.json may carry a timestamp — those are data, and `--check`
strips the field before comparing.
"""
from __future__ import annotations

import re

import pytest

from lib.entries import load_entries
from lib.pages import api_index_html, browse_pages, readme
from lib.taxonomy import load_taxonomy

ISO_DATE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")


@pytest.fixture(scope="module")
def built(repo_root):
    taxonomy = load_taxonomy(repo_root / "data" / "taxonomy")
    entries = load_entries(repo_root / "data" / "entries")
    return taxonomy, entries


def test_api_index_is_identical_on_different_days(built):
    taxonomy, entries = built
    a = api_index_html(entries, taxonomy, "2026-08-02")
    b = api_index_html(entries, taxonomy, "2027-01-15")
    assert a == b, "the API landing page must not vary with the build date"


def test_api_index_embeds_no_build_date(built):
    taxonomy, entries = built
    html = api_index_html(entries, taxonomy, "2026-08-02")
    assert "2026-08-02" not in html


def test_readme_carries_no_build_date(built):
    """Entry dates come from the data; the README must add none of its own."""
    taxonomy, entries = built
    text = readme(entries, taxonomy)
    assert "generated on" not in text.lower()


def test_browse_pages_are_deterministic(built):
    taxonomy, entries = built
    first = browse_pages(entries, taxonomy)
    second = browse_pages(entries, taxonomy)
    assert first == second


def test_regenerating_twice_produces_identical_output(built):
    taxonomy, entries = built
    assert readme(entries, taxonomy) == readme(entries, taxonomy)
