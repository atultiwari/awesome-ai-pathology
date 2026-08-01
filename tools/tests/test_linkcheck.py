"""Link-result classification.

The network layer is stubbed — what matters is that rot fails the build and
transient trouble does not, because a check that goes red on every busy CDN
gets ignored, which is worse than no check at all.
"""
from __future__ import annotations

import pytest

from lib import linkcheck
from lib.linkcheck import LinkResult, check_urls


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(linkcheck.time, "sleep", lambda _: None)


def _stub(monkeypatch, outcomes):
    """Feed _request a canned response per (url, method) or a flat value."""
    calls = []

    def fake(url, method):
        calls.append((url, method))
        value = outcomes(url, method) if callable(outcomes) else outcomes
        return value

    monkeypatch.setattr(linkcheck, "_request", fake)
    return calls


def test_healthy_link_produces_nothing(monkeypatch):
    _stub(monkeypatch, "ok")
    errors, warnings = check_urls([("a.yaml", "https://example.org/x")])
    assert (errors, warnings) == ([], [])


def test_404_is_an_error(monkeypatch):
    _stub(monkeypatch, 404)
    errors, warnings = check_urls([("a.yaml", "https://example.org/gone")])
    assert len(errors) == 1 and not warnings
    assert "404" in errors[0].detail


def test_429_is_a_warning_not_an_error(monkeypatch):
    _stub(monkeypatch, 429)
    errors, warnings = check_urls([("a.yaml", "https://rtd.example.org/")])
    assert not errors and len(warnings) == 1
    assert "transient" in warnings[0].detail


def test_503_is_a_warning(monkeypatch):
    _stub(monkeypatch, 503)
    errors, warnings = check_urls([("a.yaml", "https://example.org/")])
    assert not errors and warnings


def test_405_retries_with_get_and_passes(monkeypatch):
    calls = _stub(monkeypatch, lambda url, method: 405 if method == "HEAD" else "ok")
    errors, warnings = check_urls([("a.yaml", "https://example.org/x")])
    assert (errors, warnings) == ([], [])
    assert [m for _, m in calls] == ["HEAD", "GET"]


def test_transient_code_is_retried_once_before_warning(monkeypatch):
    calls = _stub(monkeypatch, lambda url, method: 429 if method == "HEAD" else "ok")
    errors, warnings = check_urls([("a.yaml", "https://example.org/x")])
    assert (errors, warnings) == ([], [])
    assert [m for _, m in calls] == ["HEAD", "GET"]


def test_bot_hostile_host_downgrades_404_to_warning(monkeypatch):
    """Kaggle serves 404 to non-browser agents; that is not link rot."""
    _stub(monkeypatch, 404)
    errors, warnings = check_urls([
        ("panda.yaml", "https://www.kaggle.com/competitions/x")
    ])
    assert not errors and len(warnings) == 1
    assert "verify by hand" in warnings[0].detail


def test_404_on_an_ordinary_host_still_fails(monkeypatch):
    _stub(monkeypatch, 404)
    errors, _ = check_urls([("a.yaml", "https://not-hostile.example.org/x")])
    assert errors, "a plain 404 must remain an error"


def test_tls_failure_is_an_error(monkeypatch):
    """The wrong domain must not slip through as a warning."""
    _stub(monkeypatch, "URLError: [SSL] unexpected eof")
    errors, warnings = check_urls([("cytomine.yaml", "https://cytomine.com/")])
    assert len(errors) == 1 and not warnings


def test_timeout_is_a_warning(monkeypatch):
    _stub(monkeypatch, "URLError: timed out")
    errors, warnings = check_urls([("a.yaml", "https://slow.example.org/")])
    assert not errors and len(warnings) == 1


def test_results_are_grouped_per_host_and_sorted(monkeypatch):
    _stub(monkeypatch, 404)
    errors, _ = check_urls([
        ("b.yaml", "https://b.example.org/2"),
        ("a.yaml", "https://a.example.org/1"),
    ])
    assert [e.where for e in errors] == ["a.yaml", "b.yaml"]


def test_link_result_renders_readably():
    result = LinkResult("error", "qupath.yaml", "https://x.test/", "HTTP 404")
    assert str(result) == "qupath.yaml: https://x.test/ → HTTP 404"
