"""Derived resource-tier facets — the headline differentiator (PLAN §3).

These are computed, never hand-tagged, so they cannot drift from the facts.
"""
from __future__ import annotations

from lib.facets import DERIVED, derived_facets, facet_index


def test_cpu_only_tool_runs_on_laptop(make_entry):
    assert "runs-on-laptop" in derived_facets(make_entry(hardware_floor="cpu"))


def test_cluster_tool_does_not_run_on_laptop(make_entry):
    assert "runs-on-laptop" not in derived_facets(make_entry(hardware_floor="cluster"))


def test_offline_requires_not_sending_data_offsite(make_entry):
    offsite = make_entry(offline_capable=True, sends_data_offsite=True)
    assert "works-offline" not in derived_facets(offsite)


def test_offline_tool_that_keeps_data_local_qualifies(make_entry):
    local = make_entry(offline_capable=True, sends_data_offsite=False)
    assert "works-offline" in derived_facets(local)


def test_scanner_requirement_excludes_no_scanner_facet(make_entry):
    assert "no-scanner-needed" not in derived_facets(make_entry(needs_scanner=True))


def test_low_resource_requires_all_four_conditions(make_entry):
    assert "low-resource" in derived_facets(make_entry())

    assert "low-resource" not in derived_facets(make_entry(cost="paid"))
    assert "low-resource" not in derived_facets(make_entry(hardware_floor="cluster"))
    assert "low-resource" not in derived_facets(make_entry(offline_capable=False))
    assert "low-resource" not in derived_facets(make_entry(needs_scanner=True))


def test_unknown_fields_never_qualify(make_entry):
    """A null field means 'not established', which must not be read as a yes."""
    blank = make_entry(
        hardware_floor=None, offline_capable=None, needs_scanner=None,
        sends_data_offsite=None,
    )
    assert derived_facets(blank) == ()


def test_every_declared_facet_has_a_predicate():
    from lib.taxonomy import load_taxonomy
    from pathlib import Path

    declared = load_taxonomy(
        Path(__file__).resolve().parents[2] / "data" / "taxonomy"
    ).settings_facets()
    assert set(declared) == set(DERIVED), "settings.yaml and facets.py disagree"


def test_facet_index_groups_entries_by_value(make_entry):
    entries = (
        make_entry(id="a", tasks=["annotation"]),
        make_entry(id="b", tasks=["annotation", "grading"]),
        make_entry(id="c", tasks=[]),
    )
    index = facet_index(entries, "tasks")
    assert [e["id"] for e in index["annotation"]] == ["a", "b"]
    assert [e["id"] for e in index["grading"]] == ["b"]
    assert "c" not in {e["id"] for group in index.values() for e in group}


def test_facet_index_does_not_mutate_input(make_entry):
    entries = (make_entry(id="a", tasks=["annotation"]),)
    before = entries[0]["tasks"].copy()
    facet_index(entries, "tasks")
    assert entries[0]["tasks"] == before
