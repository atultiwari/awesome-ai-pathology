"""Regulatory-claim staleness.

A stale regulatory claim is worse than no claim, so verified_on is mandatory
and the age of every claim is surfaced (PLAN §12).
"""
from __future__ import annotations

from lib.validate_rules import check_verification_freshness


def test_recent_claim_produces_no_warning(make_entry):
    entry = make_entry(regulatory={"status": "ruo", "verified_on": "2026-07-01"})
    assert check_verification_freshness((entry,), today="2026-08-01") == []


def test_claim_older_than_a_year_warns(make_entry):
    entry = make_entry(regulatory={"status": "ruo", "verified_on": "2025-01-01"})
    warnings = check_verification_freshness((entry,), today="2026-08-01")
    assert len(warnings) == 1 and "re-check" in warnings[0]


def test_boundary_at_exactly_the_limit_does_not_warn(make_entry):
    entry = make_entry(regulatory={"status": "ruo", "verified_on": "2025-08-01"})
    assert check_verification_freshness((entry,), today="2026-08-01") == []


def test_one_day_past_the_limit_warns(make_entry):
    entry = make_entry(regulatory={"status": "ruo", "verified_on": "2025-07-31"})
    assert check_verification_freshness((entry,), today="2026-08-01")


def test_missing_verified_on_is_skipped_here(make_entry):
    """Absence is the schema's job to reject, not this rule's."""
    entry = make_entry(regulatory={"status": "unknown"})
    assert check_verification_freshness((entry,), today="2026-08-01") == []


def test_custom_max_age_is_honoured(make_entry):
    entry = make_entry(regulatory={"status": "ruo", "verified_on": "2026-06-01"})
    assert check_verification_freshness((entry,), today="2026-08-01", max_age_days=30)
    assert check_verification_freshness((entry,), today="2026-08-01", max_age_days=365) == []


def test_seed_entries_are_all_currently_fresh(repo_root):
    from lib.entries import load_entries

    entries = load_entries(repo_root / "data" / "entries")
    assert check_verification_freshness(entries, today="2026-08-01") == []
