"""Shared fixtures. Adds tools/ to sys.path so `lib.*` imports resolve."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def taxonomy():
    from lib.taxonomy import load_taxonomy

    return load_taxonomy(REPO_ROOT / "data" / "taxonomy")


@pytest.fixture
def make_entry():
    """Factory producing a minimal valid entry, overridable per test.

    Returns a fresh dict each call so tests can never contaminate each other.
    """

    def _make(**overrides):
        base = {
            "id": "example-tool",
            "name": "Example Tool",
            "tagline": "An example.",
            "category": "software-viewer",
            "audience": ["researcher"],
            "tasks": [],
            "subspecialty": ["any"],
            "organs": ["any"],
            "stage": "production",
            "regulatory": {"status": "ruo", "verified_on": "2026-08-01"},
            "licence": "MIT",
            "cost": "free",
            "links": {"homepage": "https://example.org"},
            "origin": "academic",
            "summary": "A sufficiently long summary for the schema minimum.",
            "added_on": "2026-08-01",
            "last_verified": "2026-08-01",
            "offline_capable": True,
            "hardware_floor": "cpu",
            "needs_scanner": False,
            "sends_data_offsite": False,
        }
        return {**base, **overrides}

    return _make
