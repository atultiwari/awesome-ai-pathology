"""Metrics refresh: URL parsing, failure handling, and immutability.

The critical invariant: a failed API call must never blank a good value. A
transient outage that silently emptied the metrics block would make live
projects look abandoned — the exact opposite of what this feature is for.
"""
from __future__ import annotations

import pytest

from lib import metrics
from lib.metrics import github_slug, hf_ref, refresh


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(metrics.time, "sleep", lambda _: None)


# ── URL parsing ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("url,expected", [
    ("https://github.com/qupath/qupath", "qupath/qupath"),
    ("https://www.github.com/qupath/qupath", "qupath/qupath"),
    ("http://github.com/owner/repo.git", "owner/repo"),
    ("https://github.com/owner/repo/tree/main/sub", "owner/repo"),
    ("https://github.com/owner/repo#readme", "owner/repo"),
    ("https://gitlab.com/owner/repo", None),
    ("https://example.org/", None),
    (None, None),
])
def test_github_slug(url, expected):
    assert github_slug(url) == expected


@pytest.mark.parametrize("url,expected", [
    ("https://huggingface.co/MahmoodLab/UNI", ("models", "MahmoodLab/UNI")),
    ("https://huggingface.co/datasets/MahmoodLab/hest", ("datasets", "MahmoodLab/hest")),
    ("https://huggingface.co/owner/name?library=true", ("models", "owner/name")),
    ("https://example.org/x", None),
    (None, None),
])
def test_hf_ref(url, expected):
    assert hf_ref(url) == expected


# ── refresh behaviour ────────────────────────────────────────────────────

def test_populates_stars_and_last_commit(monkeypatch, make_entry):
    monkeypatch.setattr(metrics, "fetch_github",
                        lambda slug, token: {"github_stars": 1234, "last_commit": "2026-07-30"})
    entry = make_entry(links={"repo": "https://github.com/qupath/qupath"})
    out, tally = refresh([entry], today="2026-08-03")
    assert out[0]["metrics"]["github_stars"] == 1234
    assert out[0]["metrics"]["last_commit"] == "2026-07-30"
    assert out[0]["metrics"]["refreshed_on"] == "2026-08-03"
    assert tally["github"] == 1


def test_failed_lookup_preserves_the_previous_value(monkeypatch, make_entry):
    """A transient API failure must not blank good data."""
    monkeypatch.setattr(metrics, "fetch_github", lambda slug, token: {})
    entry = make_entry(
        links={"repo": "https://github.com/qupath/qupath"},
        metrics={"github_stars": 999, "last_commit": "2026-01-01",
                 "hf_downloads": None, "refreshed_on": "2026-01-02"},
    )
    out, tally = refresh([entry], today="2026-08-03")
    assert out[0]["metrics"]["github_stars"] == 999
    assert out[0]["metrics"]["last_commit"] == "2026-01-01"
    assert out[0]["metrics"]["refreshed_on"] == "2026-01-02", "stale date must not advance"
    assert tally["failed"] == 1


def test_entry_with_no_resolvable_url_is_untouched(monkeypatch, make_entry):
    monkeypatch.setattr(metrics, "fetch_github", lambda slug, token: {"github_stars": 1})
    entry = make_entry(links={"homepage": "https://example.org/"})
    out, tally = refresh([entry], today="2026-08-03")
    assert (out[0].get("metrics") or {}).get("github_stars") is None
    assert tally["skipped"] == 1


def test_huggingface_downloads_are_collected(monkeypatch, make_entry):
    monkeypatch.setattr(metrics, "fetch_hf", lambda kind, ident, token: {"hf_downloads": 4242})
    entry = make_entry(links={"model": "https://huggingface.co/MahmoodLab/UNI"})
    out, tally = refresh([entry], today="2026-08-03")
    assert out[0]["metrics"]["hf_downloads"] == 4242
    assert tally["huggingface"] == 1


def test_both_sources_merge_on_one_entry(monkeypatch, make_entry):
    monkeypatch.setattr(metrics, "fetch_github", lambda s, t: {"github_stars": 10, "last_commit": "2026-07-01"})
    monkeypatch.setattr(metrics, "fetch_hf", lambda k, i, t: {"hf_downloads": 20})
    entry = make_entry(links={"repo": "https://github.com/a/b",
                              "model": "https://huggingface.co/c/d"})
    out, _ = refresh([entry], today="2026-08-03")
    assert out[0]["metrics"]["github_stars"] == 10
    assert out[0]["metrics"]["hf_downloads"] == 20


def test_refresh_does_not_mutate_its_input(monkeypatch, make_entry):
    monkeypatch.setattr(metrics, "fetch_github", lambda s, t: {"github_stars": 77})
    entry = make_entry(links={"repo": "https://github.com/a/b"})
    before = dict(entry.get("metrics") or {})
    refresh([entry], today="2026-08-03")
    assert dict(entry.get("metrics") or {}) == before


def test_homepage_is_used_when_repo_is_absent(monkeypatch, make_entry):
    monkeypatch.setattr(metrics, "fetch_github", lambda s, t: {"github_stars": 5})
    entry = make_entry(links={"homepage": "https://github.com/owner/repo"})
    out, tally = refresh([entry], today="2026-08-03")
    assert out[0]["metrics"]["github_stars"] == 5
    assert tally["github"] == 1


def test_network_errors_are_swallowed_not_raised(monkeypatch, make_entry):
    def boom(url, token):
        raise OSError("network down")
    monkeypatch.setattr(metrics, "_get_json", boom)
    entry = make_entry(links={"repo": "https://github.com/a/b"})
    out, _ = refresh([entry], today="2026-08-03")   # must not raise
    assert out
