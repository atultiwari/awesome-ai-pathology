"""The clinical-status pages carry a prominent caution.

These are the highest-stakes pages in the catalogue: a reader could plausibly
mistake them for a procurement shortlist. The notice must appear on every page
listing devices cleared for clinical use, and must not appear on pages where it
would be noise.
"""
from __future__ import annotations

import pytest

from lib.entries import load_entries
from lib.pages import browse_pages
from lib.taxonomy import load_taxonomy

CLINICAL_PAGES = ("browse/regulatory/fda-510k.md", "browse/regulatory/fda-de-novo.md")
NON_CLINICAL_PAGES = ("browse/regulatory/ruo.md", "browse/regulatory/not-applicable.md")


@pytest.fixture(scope="module")
def pages(repo_root):
    taxonomy = load_taxonomy(repo_root / "data" / "taxonomy")
    entries = load_entries(repo_root / "data" / "entries")
    return browse_pages(entries, taxonomy)


def test_clinical_pages_exist(pages):
    for path in CLINICAL_PAGES:
        assert path in pages, f"{path} was not generated"


def test_clinical_pages_carry_the_caution(pages):
    for path in CLINICAL_PAGES:
        assert "[!CAUTION]" in pages[path], f"{path} is missing the caution block"


def test_caution_appears_before_the_table(pages):
    """A warning below the list is a warning nobody reads."""
    for path in CLINICAL_PAGES:
        text = pages[path]
        assert text.index("[!CAUTION]") < text.index("| Name |")


def _flatten(markdown: str) -> str:
    """Strip blockquote prefixes and collapse wrapping, so a phrase that spans
    a line break is still findable."""
    lines = [line.lstrip("> ").strip() for line in markdown.splitlines()]
    return " ".join(" ".join(lines).split()).lower()


@pytest.mark.parametrize("phrase", [
    "not a procurement list",
    "not proof of clinical benefit",
    "indication for use",
    "carries no weight in India",
    "Local validation is still required",
    "not a regulatory authority",
    "substantially equivalent",
    "CDSCO",
])
def test_caution_covers_each_required_point(pages, phrase):
    text = _flatten(pages["browse/regulatory/fda-510k.md"])
    assert phrase.lower() in text, f"missing: {phrase}"


def test_caution_links_a_correction_route(pages):
    assert "issues/new/choose" in pages["browse/regulatory/fda-510k.md"]


def test_non_clinical_pages_do_not_carry_it(pages):
    """Research-use and not-applicable pages would only be diluted by it."""
    for path in NON_CLINICAL_PAGES:
        if path in pages:
            assert "[!CAUTION]" not in pages[path]


def test_ordinary_facet_pages_are_unaffected(pages):
    assert "[!CAUTION]" not in pages["browse/setting/low-resource.md"]
    assert "[!CAUTION]" not in pages["browse/all.md"]
