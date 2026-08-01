"""The regulatory-sourcing rules — the catalogue's highest-stakes invariant.

A wrong clearance claim is the single worst error this project can make, so the
rules are enforced mechanically rather than left to review.
"""
from __future__ import annotations

import pytest

from lib.entries import load_entries
from lib.linkcheck import BOT_HOSTILE_HOSTS, USER_AGENT

FDA_HOSTS = ("accessdata.fda.gov",)
CLINICAL_STATUSES = {
    "fda-510k", "fda-de-novo", "fda-pma", "ce-ivdr", "ukca", "cdsco", "tga", "pmda",
}


@pytest.fixture(scope="module")
def entries(repo_root):
    return load_entries(repo_root / "data" / "entries")


def test_every_clinical_claim_links_a_primary_record(entries):
    """No clearance claim may rest on vendor marketing."""
    offenders = []
    for entry in entries:
        reg = entry.get("regulatory") or {}
        if reg.get("status") in CLINICAL_STATUSES and not reg.get("reference"):
            offenders.append(entry["id"])
    assert not offenders, f"clinical status with no primary reference: {offenders}"


def test_fda_claims_cite_the_fda_not_the_vendor(entries):
    """An FDA claim must link accessdata.fda.gov, not the company's website."""
    offenders = []
    for entry in entries:
        reg = entry.get("regulatory") or {}
        if str(reg.get("status", "")).startswith("fda-"):
            ref = reg.get("reference") or ""
            if not any(host in ref for host in FDA_HOSTS):
                offenders.append(f"{entry['id']} → {ref}")
    assert not offenders, f"FDA claims not citing an FDA record: {offenders}"


def test_every_clinical_claim_is_dated(entries):
    offenders = [
        e["id"] for e in entries
        if (e.get("regulatory") or {}).get("status") in CLINICAL_STATUSES
        and not (e.get("regulatory") or {}).get("verified_on")
    ]
    assert not offenders, f"undated clinical claim: {offenders}"


def test_clinical_entries_carry_a_scope_caveat(entries):
    """Clearance is jurisdiction- and indication-specific; say so on every entry."""
    offenders = []
    for entry in entries:
        reg = entry.get("regulatory") or {}
        if reg.get("status") in CLINICAL_STATUSES:
            text = (entry.get("caveats") or "").lower()
            if "indication" not in text and "jurisdiction" not in text:
                offenders.append(entry["id"])
    assert not offenders, f"cleared device without a scope caveat: {offenders}"


def test_fda_record_host_is_not_bot_hostile_listed():
    """A real 404 on an FDA citation must fail loudly, never be downgraded.

    Adding accessdata.fda.gov to BOT_HOSTILE_HOSTS would silently turn a dead
    regulatory reference into a warning. Explicitly forbidden.
    """
    for host in FDA_HOSTS:
        assert host not in BOT_HOSTILE_HOSTS


def test_user_agent_is_not_the_pattern_fda_rejects():
    """accessdata.fda.gov answers an identifying bot UA with a misleading 404.

    Verified 2026-08-02: a UA containing 'compatible;' plus a '+https://' contact
    URL returns 404 for records that return 200 to an ordinary browser token.
    """
    assert "compatible;" not in USER_AGENT
    assert "+http" not in USER_AGENT
