"""Every internal link in the generated output must resolve.

Broken relative links and broken anchors are the classic failure of a generated
awesome list — they render fine locally and 404 on GitHub. These tests build the
site in memory and check every link against it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from lib.entries import load_entries
from lib.pages import api_documents, browse_pages, readme, today_iso
from lib.taxonomy import load_taxonomy

# A plain link, and the OUTER target of a badge — [![alt](img-src)](target).
# Matching only the plain form misses every badge link, which is how a
# non-relativised regulatory badge slipped through once already.
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BADGE_LINK = re.compile(r"\[!\[[^\]]*\]\([^)]*\)\]\(([^)\s]+)\)")

# Files that exist in the repo but are not produced by the generator.
STATIC_FILES = {
    "README.md", "CONTRIBUTING.md", "DISCLAIMER.md", "LICENSE", "LICENSE-CODE",
    "ACKNOWLEDGEMENTS.md",
}


@pytest.fixture(scope="module")
def site(repo_root: Path) -> dict[str, str]:
    taxonomy = load_taxonomy(repo_root / "data" / "taxonomy")
    entries = load_entries(repo_root / "data" / "entries")
    pages = {"README.md": readme(entries, taxonomy)}
    pages.update(browse_pages(entries, taxonomy))
    pages.update(api_documents(entries, taxonomy, today_iso()))
    return pages


def _internal_links(markdown: str) -> list[str]:
    targets = MARKDOWN_LINK.findall(markdown) + BADGE_LINK.findall(markdown)
    return [
        target for target in targets
        if not target.startswith(("http://", "https://", "mailto:"))
    ]


def _github_anchor(heading: str) -> str:
    """Reproduce GitHub's heading-to-anchor transformation."""
    text = heading.strip().lstrip("#").strip().lower()
    kept = "".join(c for c in text if c.isalnum() or c in " -_")
    return kept.replace(" ", "-")


def _resolve(from_page: str, target: str) -> str:
    """Resolve a relative link the way a browser would, collapsing '..'."""
    import posixpath

    return posixpath.normpath(posixpath.join(posixpath.dirname(from_page), target))


def test_readme_toc_anchors_match_its_headings(site):
    readme_text = site["README.md"]
    headings = {
        _github_anchor(line)
        for line in readme_text.splitlines() if line.startswith("## ")
    }
    anchors = [t[1:] for t in _internal_links(readme_text) if t.startswith("#")]

    assert anchors, "README has no table-of-contents anchors"
    missing = [a for a in anchors if a not in headings]
    assert not missing, f"ToC anchors with no matching heading: {missing}"


def test_no_heading_starts_with_an_emoji(site):
    """Emoji in a heading shift GitHub's anchor and silently break the ToC."""
    for page, text in site.items():
        if not page.endswith(".md"):
            continue
        for line in text.splitlines():
            if line.startswith("#"):
                body = line.lstrip("#").strip()
                assert body[:1].isalnum() or body[:1] in "(", (
                    f"{page}: heading must start with a word, got {line!r}"
                )


def test_every_relative_link_resolves(site):
    known = set(site) | STATIC_FILES
    broken: list[str] = []

    for page, text in site.items():
        if not page.endswith(".md"):
            continue
        for target in _internal_links(text):
            if target.startswith("#"):
                continue
            path = _resolve(page, target.split("#")[0])
            if path not in known:
                broken.append(f"{page} → {target} (resolved to {path})")

    assert not broken, "unresolved relative links:\n" + "\n".join(broken)


def test_facet_chips_point_at_pages_that_exist(site):
    """Every tag chip is a link — the whole 'filtering' mechanism depends on it."""
    browse_targets = {p for p in site if p.startswith("browse/")}
    assert browse_targets, "no browse pages generated"

    readme_links = {
        t for t in _internal_links(site["README.md"]) if t.startswith("browse/")
    }
    assert readme_links <= browse_targets, (
        f"README links to missing browse pages: {readme_links - browse_targets}"
    )


def test_api_documents_are_valid_json(site):
    import json

    for page, text in site.items():
        if page.endswith(".json"):
            json.loads(text)


def test_api_entries_carry_no_internal_keys(site):
    import json

    payload = json.loads(site["api/v1/entries.json"])
    for entry in payload["entries"]:
        leaked = [k for k in entry if k.startswith("_")]
        assert not leaked, f"{entry['id']}: internal keys leaked into the API: {leaked}"
