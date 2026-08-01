"""Taxonomy loading and term lookup."""
from __future__ import annotations

import pytest

from lib.taxonomy import KINDS, load_taxonomy


def test_loads_every_expected_kind(taxonomy):
    for kind in KINDS:
        assert taxonomy.terms(kind), f"{kind} vocabulary is empty"


def test_known_terms_resolve(taxonomy):
    assert taxonomy.has("categories", "qupath-extension")
    assert taxonomy.has("subspecialties", "haematopathology")
    assert taxonomy.has("organs", "breast")
    assert taxonomy.has("regulatory", "cdsco")


def test_unknown_terms_are_rejected(taxonomy):
    assert not taxonomy.has("categories", "not-a-real-category")
    assert not taxonomy.has("organs", "spleen-of-doom")


def test_labels_are_human_readable(taxonomy):
    assert taxonomy.label("categories", "qupath-extension") == "QuPath Extensions & Scripts"
    assert taxonomy.label("organs", "lymph-node") == "Lymph Node"


def test_label_of_unknown_term_raises(taxonomy):
    with pytest.raises(KeyError):
        taxonomy.label("organs", "nonexistent")


def test_categories_are_ordered_without_collisions(taxonomy):
    orders = [t["order"] for t in taxonomy.terms("categories").values()]
    assert len(orders) == len(set(orders)), "two categories share an order value"


def test_regulatory_marks_clinical_statuses(taxonomy):
    reg = taxonomy.terms("regulatory")
    assert reg["fda-510k"]["clinical"] is True
    assert reg["ruo"]["clinical"] is False
    assert reg["unknown"]["clinical"] is False


def test_missing_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_taxonomy(tmp_path / "nope")
