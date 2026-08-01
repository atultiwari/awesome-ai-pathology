"""Entry loading, normalisation and the validation rules."""
from __future__ import annotations

import pytest
import yaml

from lib.entries import apply_defaults, load_entries
from lib.validate_rules import (
    check_bot_owned_metrics,
    check_duplicate_ids,
    check_id_matches_filename,
    check_related_targets_exist,
    check_vocabularies,
)


def _write(dir_, entry):
    path = dir_ / f"{entry['id']}.yaml"
    path.write_text(yaml.safe_dump(entry, sort_keys=False), encoding="utf-8")
    return path


# ── normalisation ────────────────────────────────────────────────────────

def test_defaults_are_applied_for_absent_optional_fields(make_entry):
    raw = make_entry()
    raw.pop("tasks", None)
    filled = apply_defaults(raw)
    assert filled["tasks"] == []
    assert filled["featured"] is False
    assert filled["showcase"] is False
    assert filled["metrics"]["github_stars"] is None


def test_apply_defaults_returns_a_new_object(make_entry):
    raw = make_entry()
    filled = apply_defaults(raw)
    assert filled is not raw
    assert "metrics" not in raw, "input was mutated"


# ── loading ──────────────────────────────────────────────────────────────

def test_loads_entries_sorted_by_id(tmp_path, make_entry):
    _write(tmp_path, make_entry(id="zebra"))
    _write(tmp_path, make_entry(id="alpha"))
    assert [e["id"] for e in load_entries(tmp_path)] == ["alpha", "zebra"]


def test_empty_directory_loads_cleanly(tmp_path):
    assert load_entries(tmp_path) == ()


# ── rules ────────────────────────────────────────────────────────────────

def test_id_must_match_filename(tmp_path, make_entry):
    path = tmp_path / "wrong-name.yaml"
    path.write_text(yaml.safe_dump(make_entry(id="right-name")), encoding="utf-8")
    errors = check_id_matches_filename(load_entries(tmp_path))
    assert any("wrong-name" in e for e in errors)


def test_matching_filename_passes(tmp_path, make_entry):
    _write(tmp_path, make_entry(id="right-name"))
    assert check_id_matches_filename(load_entries(tmp_path)) == []


def test_duplicate_ids_are_reported(make_entry):
    entries = (make_entry(id="dup"), make_entry(id="dup"), make_entry(id="fine"))
    errors = check_duplicate_ids(entries)
    assert len(errors) == 1 and "dup" in errors[0]


def test_unknown_vocabulary_term_is_reported(taxonomy, make_entry):
    bad = make_entry(id="bad", organs=["spleen-of-doom"])
    errors = check_vocabularies((bad,), taxonomy)
    assert any("spleen-of-doom" in e for e in errors)


def test_known_vocabulary_terms_pass(taxonomy, make_entry):
    good = make_entry(
        category="qupath-extension",
        tasks=["annotation"],
        subspecialty=["histopathology"],
        organs=["breast"],
        audience=["clinician"],
    )
    assert check_vocabularies((good,), taxonomy) == []


def test_related_must_point_at_existing_entries(make_entry):
    entries = (make_entry(id="a", related=["b"]), make_entry(id="b"))
    assert check_related_targets_exist(entries) == []

    dangling = (make_entry(id="a", related=["ghost"]),)
    assert any("ghost" in e for e in check_related_targets_exist(dangling))


# ── the bot-owned metrics block ──────────────────────────────────────────

def test_human_written_metrics_are_rejected(make_entry):
    tampered = make_entry(metrics={"github_stars": 9999, "last_commit": None,
                                   "hf_downloads": None, "refreshed_on": None})
    errors = check_bot_owned_metrics((tampered,), bot_authored=False)
    assert any("metrics" in e for e in errors)


def test_bot_written_metrics_are_allowed(make_entry):
    written = make_entry(metrics={"github_stars": 9999, "last_commit": None,
                                  "hf_downloads": None, "refreshed_on": None})
    assert check_bot_owned_metrics((written,), bot_authored=True) == []


def test_absent_metrics_block_is_always_fine(make_entry):
    assert check_bot_owned_metrics((make_entry(),), bot_authored=False) == []


def test_null_only_metrics_block_is_fine(make_entry):
    empty = make_entry(metrics={"github_stars": None, "last_commit": None,
                                "hf_downloads": None, "refreshed_on": None})
    assert check_bot_owned_metrics((empty,), bot_authored=False) == []


# ── schema integration ───────────────────────────────────────────────────

def test_real_entries_all_satisfy_the_schema(repo_root):
    from lib.validate_rules import check_schema

    entries = load_entries(repo_root / "data" / "entries")
    assert entries, "no seed entries found"
    assert check_schema(entries, repo_root / "schema" / "entry.schema.json") == []


def test_clinical_regulatory_status_requires_a_reference(repo_root, make_entry):
    from lib.validate_rules import check_schema

    claim = make_entry(
        regulatory={"status": "fda-510k", "verified_on": "2026-08-01"}
    )
    errors = check_schema((claim,), repo_root / "schema" / "entry.schema.json")
    assert errors, "an FDA claim without a primary reference must fail"


def test_non_unknown_status_requires_verified_on(repo_root, make_entry):
    from lib.validate_rules import check_schema

    undated = make_entry(regulatory={"status": "ruo"})
    errors = check_schema((undated,), repo_root / "schema" / "entry.schema.json")
    assert errors, "a dated claim is required whenever status is not 'unknown'"
