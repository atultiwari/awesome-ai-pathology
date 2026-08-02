"""The Stale Shelf.

An awesome list that hides dead projects is worse than useless — the reader
assumes everything listed is alive. But wrongly shaming a finished, stable tool
is also a failure, so the threshold is deliberately generous and missing data
never counts as abandonment.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from lib.facets import STALE_AFTER_DAYS, derived_facets


def _days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


def _metrics(last_commit=None):
    return {"github_stars": None, "last_commit": last_commit,
            "hf_downloads": None, "refreshed_on": None}


def test_deprecated_stage_is_always_stale(make_entry):
    assert "stale-shelf" in derived_facets(make_entry(stage="deprecated"))


def test_long_silent_repository_is_stale(make_entry):
    entry = make_entry(metrics=_metrics(_days_ago(STALE_AFTER_DAYS + 30)))
    assert "stale-shelf" in derived_facets(entry)


def test_recently_active_repository_is_not_stale(make_entry):
    entry = make_entry(metrics=_metrics(_days_ago(30)))
    assert "stale-shelf" not in derived_facets(entry)


def test_just_inside_the_threshold_is_not_stale(make_entry):
    entry = make_entry(metrics=_metrics(_days_ago(STALE_AFTER_DAYS - 5)))
    assert "stale-shelf" not in derived_facets(entry)


def test_missing_commit_data_is_never_stale(make_entry):
    """Absence of evidence is not evidence of abandonment."""
    assert "stale-shelf" not in derived_facets(make_entry(metrics=_metrics(None)))
    assert "stale-shelf" not in derived_facets(make_entry())


def test_malformed_date_does_not_crash_or_flag(make_entry):
    entry = make_entry(metrics=_metrics("not-a-date"))
    assert "stale-shelf" not in derived_facets(entry)


def test_threshold_is_generous_enough_for_finished_tools():
    """A stable tool untouched for a year must not be shamed."""
    assert STALE_AFTER_DAYS > 365


def test_stale_facet_is_declared_in_the_taxonomy(taxonomy):
    assert "stale-shelf" in taxonomy.settings_facets()


def test_a_stale_entry_can_still_be_low_resource(make_entry):
    """The facets are independent — being dormant does not change the hardware."""
    entry = make_entry(stage="deprecated")
    facets = derived_facets(entry)
    assert "stale-shelf" in facets and "low-resource" in facets
