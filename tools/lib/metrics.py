"""Activity metrics for catalogued projects.

Answers the question a curated list usually cannot: is this thing still alive?
GitHub stars and last-commit date, Hugging Face downloads.

This module is BOT-OWNED. `validate.py` rejects human-authored changes to the
metrics block, so these values only ever arrive through the scheduled job.
Nothing here mutates its arguments — refresh() returns new entry dicts.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable, Mapping, Sequence

from lib.entries import Entry

GITHUB_API = "https://api.github.com/repos/"
HF_API = "https://huggingface.co/api/"
TIMEOUT_S = 25
PER_REQUEST_DELAY_S = 0.25

GITHUB_REPO_RE = re.compile(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/#?]+)")
HF_RE = re.compile(r"^https?://huggingface\.co/(datasets/)?([^/#?]+)/([^/#?]+)")


def github_slug(url: str | None) -> str | None:
    """owner/repo from a GitHub URL, or None. Strips a trailing .git."""
    if not url:
        return None
    match = GITHUB_REPO_RE.match(url)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]
    return f"{owner}/{repo}"


def hf_ref(url: str | None) -> tuple[str, str] | None:
    """(kind, id) for a Hugging Face model or dataset URL.

    kind is 'models' or 'datasets', matching the API path.
    """
    if not url:
        return None
    match = HF_RE.match(url)
    if not match:
        return None
    is_dataset, owner, name = match.groups()
    return ("datasets" if is_dataset else "models", f"{owner}/{name}")


def _get_json(url: str, token: str | None) -> Any | None:
    headers = {
        "User-Agent": "awesome-ai-pathology-metrics/1.0",
        "Accept": "application/vnd.github+json",
    }
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            return json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError):
        return None


def fetch_github(slug: str, token: str | None) -> dict[str, Any]:
    """Stars and last push date. Empty dict when the lookup fails."""
    data = _get_json(GITHUB_API + urllib.parse.quote(slug), token)
    if not isinstance(data, dict) or "stargazers_count" not in data:
        return {}
    pushed = data.get("pushed_at") or ""
    return {
        "github_stars": data.get("stargazers_count"),
        "last_commit": pushed[:10] or None,
    }


def fetch_hf(kind: str, ident: str, token: str | None) -> dict[str, Any]:
    """Monthly download count. Empty dict when the lookup fails."""
    data = _get_json(f"{HF_API}{kind}/{urllib.parse.quote(ident)}", token)
    if not isinstance(data, dict):
        return {}
    downloads = data.get("downloads")
    return {"hf_downloads": downloads} if isinstance(downloads, int) else {}


def refresh(
    entries: Sequence[Entry], today: str, token: str | None = None
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Return new entry dicts with metrics refreshed, plus a summary tally.

    An entry with no resolvable GitHub or Hugging Face URL is returned
    unchanged. A failed lookup leaves the previous value in place rather than
    blanking it — a transient API error must not erase good data.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    out: list[dict[str, Any]] = []
    tally = {"github": 0, "huggingface": 0, "skipped": 0, "failed": 0}

    for entry in entries:
        links = entry.get("links") or {}
        previous = dict(entry.get("metrics") or {})
        fresh: dict[str, Any] = {}

        slug = github_slug(links.get("repo")) or github_slug(links.get("homepage"))
        if slug:
            # Isolated per entry: one unexpected exception must not abort the
            # run and leave the other 100+ entries unrefreshed.
            try:
                got = fetch_github(slug, token)
            except Exception:
                got = {}
            time.sleep(PER_REQUEST_DELAY_S)
            if got:
                fresh.update(got)
                tally["github"] += 1
            else:
                tally["failed"] += 1

        hf = hf_ref(links.get("model")) or hf_ref(links.get("dataset"))
        if hf:
            try:
                got = fetch_hf(hf[0], hf[1], token)
            except Exception:
                got = {}
            time.sleep(PER_REQUEST_DELAY_S)
            if got:
                fresh.update(got)
                tally["huggingface"] += 1
            else:
                tally["failed"] += 1

        if not slug and not hf:
            tally["skipped"] += 1
            out.append(dict(entry))
            continue

        merged = {**previous, **fresh}
        if fresh:
            merged["refreshed_on"] = today
        out.append({**entry, "metrics": merged})

    return out, tally


def write_back(entries: Iterable[Mapping[str, Any]], directory) -> int:
    """Persist only the metrics block, leaving the rest of each file untouched.

    Rewriting whole files would reflow hand-written prose and produce enormous
    diffs, so this edits the metrics mapping in place within the loaded YAML.
    """
    import yaml
    from pathlib import Path

    from lib.entries import SOURCE_KEY, METRIC_FIELDS

    directory = Path(directory)
    changed = 0
    for entry in entries:
        source = entry.get(SOURCE_KEY)
        if not source:
            continue
        path = directory / source
        if not path.is_file():
            continue

        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}

        wanted = {f: (entry.get("metrics") or {}).get(f) for f in METRIC_FIELDS}
        if not any(v is not None for v in wanted.values()):
            continue
        if (raw.get("metrics") or {}) == wanted:
            continue

        raw["metrics"] = wanted
        path.write_text(
            yaml.safe_dump(raw, sort_keys=False, allow_unicode=True, width=100),
            encoding="utf-8",
        )
        changed += 1
    return changed
