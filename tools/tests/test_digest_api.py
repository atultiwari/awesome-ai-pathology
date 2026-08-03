"""Digest parsing for the API.

The converter handles only the markdown these issues use. What matters is that
unrecognised input degrades to escaped text rather than injecting markup — the
issues are hand-edited, and a stray construct must not become a script tag.
"""
from __future__ import annotations

import pytest

from lib.digest import collect, inline, parse_issue, to_html


# ── inline conversion ────────────────────────────────────────────────────

def test_link_converts():
    assert inline("see [QuPath](https://qupath.github.io/)") == (
        'see <a href="https://qupath.github.io/">QuPath</a>'
    )


def test_bold_and_italic():
    assert inline("**loud** and *soft*") == "<strong>loud</strong> and <em>soft</em>"


def test_code_span():
    assert inline("run `tools/validate.py`") == "run <code>tools/validate.py</code>"


def test_html_in_source_is_escaped():
    """Editorial is hand-written; a stray tag must never become live markup."""
    out = inline('<script>alert(1)</script>')
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_link_url_is_attribute_escaped():
    out = inline('[x](https://e.org/?a="b")')
    assert '"b"' not in out.split('href="')[1].split('"')[0] or "&quot;" in out


def test_bold_inside_a_link_label_survives():
    out = inline("[**Name**](https://e.org)")
    assert 'href="https://e.org"' in out and "<strong>Name</strong>" in out


# ── block conversion ─────────────────────────────────────────────────────

def test_paragraphs_split_on_blank_lines():
    assert to_html("one\n\ntwo") == "<p>one</p><p>two</p>"


def test_wrapped_lines_join_into_one_paragraph():
    assert to_html("one\ntwo") == "<p>one two</p>"


def test_list_becomes_ul():
    assert to_html("- a\n- b") == "<ul><li>a</li><li>b</li></ul>"


def test_blockquote_strips_the_callout_marker():
    out = to_html("> [!NOTE]\n> careful")
    assert "<blockquote>" in out and "[!NOTE]" not in out


def test_horizontal_rule_is_dropped():
    assert "---" not in to_html("a\n\n---\n\nb")


def test_state_marker_comment_is_dropped():
    assert to_html("<!-- review-state: pending -->\ntext") == "<p>text</p>"


# ── whole issues ─────────────────────────────────────────────────────────

def test_parses_the_published_issue(repo_root):
    issue = parse_issue(repo_root / "digest" / "2026-W32.md")
    assert issue is not None
    assert issue["id"] == "2026-W32"
    assert issue["year"] == 2026 and issue["week"] == 32
    assert issue["reviewed"] is True
    assert issue["sections"], "issue should split into sections"


def test_title_drops_the_review_suffix(tmp_path):
    path = tmp_path / "2026-W33.md"
    path.write_text(
        "<!-- review-state: pending -->\n"
        "# This Week in AI Pathology — 2026, week 33  ·  *awaiting review*\n\n"
        "## Regulatory\n\nNothing.\n",
        encoding="utf-8",
    )
    issue = parse_issue(path)
    assert "awaiting review" not in issue["title"]
    assert issue["reviewed"] is False


def test_pending_issue_has_no_review_date(tmp_path):
    path = tmp_path / "2026-W34.md"
    path.write_text("<!-- review-state: pending -->\n# Week 34\n\n## A\n\nx\n", encoding="utf-8")
    assert parse_issue(path)["reviewed_on"] is None


def test_companion_full_listing_is_not_an_issue(tmp_path):
    path = tmp_path / "2026-W32-full.md"
    path.write_text("# Full list\n", encoding="utf-8")
    assert parse_issue(path) is None


def test_collect_returns_newest_first(repo_root):
    issues = collect(repo_root)
    assert issues, "no issues collected"
    ids = [i["id"] for i in issues]
    assert ids == sorted(ids, reverse=True)


def test_collect_excludes_full_listings(repo_root):
    assert all(not i["id"].endswith("-full") for i in collect(repo_root))
