"""Controlled vocabularies loaded from data/taxonomy/*.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import yaml

# Vocabulary files, keyed by the name used in lookups. `settings` is handled
# separately because it holds both derived-facet metadata and field enums.
KINDS: tuple[str, ...] = (
    "categories",
    "tasks",
    "subspecialties",
    "organs",
    "regulatory",
    "audience",
    "stage",
)

# Maps an entry field to the vocabulary that governs it, and to the browse/
# subdirectory its facet pages are written into.
FIELD_VOCABULARY: Mapping[str, str] = MappingProxyType({
    "category": "categories",
    "tasks": "tasks",
    "subspecialty": "subspecialties",
    "organs": "organs",
    "audience": "audience",
    "stage": "stage",
})

BROWSE_DIR: Mapping[str, str] = MappingProxyType({
    "categories": "category",
    "tasks": "task",
    "subspecialties": "subspecialty",
    "organs": "organ",
    "audience": "audience",
    "regulatory": "regulatory",
    "stage": "stage",
    "settings": "setting",
})


@dataclass(frozen=True)
class Taxonomy:
    """Immutable view over the loaded vocabularies."""

    _kinds: Mapping[str, Mapping[str, Any]]
    _settings: Mapping[str, Any]

    def terms(self, kind: str) -> Mapping[str, Any]:
        try:
            return self._kinds[kind]
        except KeyError as exc:
            raise KeyError(f"unknown vocabulary {kind!r}") from exc

    def has(self, kind: str, term: str) -> bool:
        return term in self.terms(kind)

    def label(self, kind: str, term: str) -> str:
        entry = self.terms(kind)[term]
        return entry.get("label", term)

    def meta(self, kind: str, term: str) -> Mapping[str, Any]:
        return self.terms(kind)[term]

    def settings_facets(self) -> Mapping[str, Any]:
        """Derived resource-tier facet definitions from settings.yaml."""
        return self._settings.get("facets", {})

    def field_enum(self, field: str) -> Mapping[str, Any]:
        """Vocabulary for a scalar field declared in settings.yaml."""
        return self._settings.get(field, {})

    def ordered(self, kind: str) -> tuple[tuple[str, Mapping[str, Any]], ...]:
        """Terms sorted by their `order`, then alphabetically by key."""
        items = self.terms(kind).items()
        return tuple(sorted(items, key=lambda kv: (kv[1].get("order", 9999), kv[0])))


def load_taxonomy(directory: Path) -> Taxonomy:
    """Read every vocabulary file. Raises if the directory or a file is absent."""
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError(f"taxonomy directory not found: {directory}")

    kinds: dict[str, Mapping[str, Any]] = {}
    for kind in KINDS:
        path = directory / f"{kind}.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"missing vocabulary file: {path}")
        kinds[kind] = MappingProxyType(_read_yaml(path))

    settings = _read_yaml(directory / "settings.yaml")
    return Taxonomy(MappingProxyType(kinds), MappingProxyType(settings))


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
