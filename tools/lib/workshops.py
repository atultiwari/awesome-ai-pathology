"""The editor's teaching schedule, mirrored for the digest's closing page.

Every issue closes by saying who compiles it and where he teaches the hands-on
part. That listing has to be current without anyone editing it weekly, so it
is read from the workshops site itself.

That site keeps its content in one authored JavaScript file rather than a
feed. This module parses the few fields the digest needs out of it WITHOUT
executing it. Evaluating JavaScript fetched over the network inside CI would
mean that anyone who ever compromised that host could run code in this
repository's pipeline — a bad trade for the convenience of `eval`.

Parsing is deliberately tolerant: unknown fields, comments and syntax it does
not understand are skipped rather than fatal. But a fetch that yields NO
workshops raises, because silently publishing an empty teaching section would
look like the series had ended.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

SOURCE_URL = "https://workshops.vedantresearchlabs.com/workshops.js"

#: The site is a browser-facing page; a plain script user-agent gets a
#: different response from some CDNs than a browser does.
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

#: Statuses worth printing. 'members' and 'planning' are excluded: a reader
#: cannot act on either, and a list of things they cannot attend is an
#: advertisement rather than a service.
PUBLISHABLE = ("open", "soon", "youtube")

#: A placeholder the source file marks with TODO must never reach print.
_TODO = re.compile(r"//\s*TODO", re.IGNORECASE)


class WorkshopsError(RuntimeError):
    """Raised when the schedule cannot be read. Never swallowed."""


def fetch(url: str = SOURCE_URL, timeout: int = 20) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError) as error:
        raise WorkshopsError(f"could not fetch {url}: {error}") from error


def _blocks(source: str) -> list[str]:
    """Top-level `{...}` objects inside the WORKSHOPS array.

    Brace counting rather than a regex, because the objects nest and a regex
    cannot balance brackets. String contents are skipped so a brace inside
    prose ("{ like this }") cannot throw the count off.
    """
    start = source.find("const WORKSHOPS")
    if start == -1:
        raise WorkshopsError("no WORKSHOPS array in the source file")
    open_bracket = source.find("[", start)
    if open_bracket == -1:
        raise WorkshopsError("WORKSHOPS is not an array")

    found: list[str] = []
    depth = 0
    begin = 0
    quote = None
    index = open_bracket
    while index < len(source):
        char = source[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "'\"`":
            quote = char
        elif char == "{":
            if depth == 0:
                begin = index
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                found.append(source[begin:index + 1])
        elif char == "]" and depth == 0:
            break
        index += 1
    return found


def _string(block: str, key: str) -> str | None:
    """A string value for `key`, or None when absent, empty or a placeholder."""
    pattern = re.compile(
        rf"(?<![\w.]){re.escape(key)}\s*:\s*(?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\")"
    )
    match = pattern.search(block)
    if not match:
        return None
    line_end = block.find("\n", match.end())
    trailing = block[match.end():line_end if line_end != -1 else len(block)]
    if _TODO.search(trailing):
        return None
    raw = match.group(1) if match.group(1) is not None else match.group(2)
    value = re.sub(r"\\(['\"\\])", r"\1", raw).strip()
    return value or None


def _nested(block: str, outer: str, key: str) -> str | None:
    match = re.search(rf"(?<![\w.]){re.escape(outer)}\s*:\s*\{{", block)
    if not match:
        return None
    depth = 1
    index = match.end()
    while index < len(block) and depth:
        if block[index] == "{":
            depth += 1
        elif block[index] == "}":
            depth -= 1
        index += 1
    return _string(block[match.end():index], key)


def parse(source: str) -> list[dict[str, Any]]:
    """Every publishable workshop, in the order the site lists them."""
    workshops = []
    for block in _blocks(source):
        status = _string(block, "status")
        title = _string(block, "title")
        if not title or status not in PUBLISHABLE:
            continue
        workshops.append({
            "id": _string(block, "id") or "",
            "title": title,
            "tagline": _string(block, "tagline"),
            "status": status,
            "level": _string(block, "level"),
            "format": _string(block, "format"),
            "for_whom": _string(block, "forWhom"),
            "when": _nested(block, "schedule", "label"),
            "starts_at": _nested(block, "schedule", "startISO"),
            "url": _nested(block, "cta", "href"),
        })
    if not workshops:
        raise WorkshopsError(
            "parsed no publishable workshops — the source format has probably "
            "changed, and printing an empty teaching section would read as the "
            "series having ended"
        )
    return workshops


def document(workshops: list[dict[str, Any]], generated_at: str) -> str:
    return json.dumps({
        "generated_at": generated_at,
        "source": SOURCE_URL,
        "count": len(workshops),
        "workshops": workshops,
    }, indent=2, ensure_ascii=False) + "\n"
