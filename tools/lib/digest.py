"""Parse published digest issues into structured data for the API.

The issues themselves stay markdown — they are editorial, hand-edited, and must
remain readable and diffable on GitHub. This turns them into JSON so the website
can render an issue as a paginated reader without re-implementing a parser in
the browser, and without the site needing a rebuild when an issue is published.

The markdown converter deliberately handles only the subset these issues use.
Anything it does not recognise is escaped and passed through as text, so a
surprise construct degrades to plain prose rather than injecting markup.
"""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

STATE_RE = re.compile(r"<!--\s*review-state:\s*(\w+)\s*-->")
ISSUE_RE = re.compile(r"^(\d{4})-W(\d{2})$")
REVIEWED_ON_RE = re.compile(r"Reviewed by [^.]*? on (\d{4}-\d{2}-\d{2})")

# Inline markdown, applied in this order. Links first so their text is not
# mangled by the emphasis rules.
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_CODE = re.compile(r"`([^`]+)`")


def inline(text: str) -> str:
    """Convert inline markdown to HTML, escaping everything else."""
    out = html.escape(text, quote=False)
    out = _CODE.sub(lambda m: f"<code>{m.group(1)}</code>", out)
    out = _LINK.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', out
    )
    out = _BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", out)
    out = _ITALIC.sub(lambda m: f"<em>{m.group(1)}</em>", out)
    return out


def to_html(markdown: str) -> str:
    """Block-level conversion for the subset the digests use."""
    blocks: list[str] = []
    buffer: list[str] = []
    mode: str | None = None

    def flush() -> None:
        nonlocal buffer, mode
        if not buffer:
            mode = None
            return
        if mode == "ul":
            items = "".join(f"<li>{inline(line)}</li>" for line in buffer)
            blocks.append(f"<ul>{items}</ul>")
        elif mode == "quote":
            body = " ".join(buffer)
            blocks.append(f"<blockquote><p>{inline(body)}</p></blockquote>")
        else:
            body = " ".join(buffer)
            blocks.append(f"<p>{inline(body)}</p>")
        buffer = []
        mode = None

    for raw in markdown.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush()
            continue
        if stripped.startswith("<!--"):
            continue
        if stripped.startswith("---"):
            flush()
            continue
        if stripped.startswith("### "):
            flush()
            blocks.append(f"<h4>{inline(stripped[4:])}</h4>")
            continue
        if stripped.startswith("> "):
            if mode != "quote":
                flush()
                mode = "quote"
            buffer.append(re.sub(r"^\[!\w+\]\s*", "", stripped[2:]))
            continue
        if stripped.startswith("- "):
            if mode != "ul":
                flush()
                mode = "ul"
            buffer.append(stripped[2:])
            continue

        if mode in ("ul", "quote"):
            flush()
        mode = mode or "p"
        buffer.append(stripped)

    flush()
    return "".join(blocks)


def parse_issue(path: Path) -> dict[str, Any] | None:
    """One issue as structured data, split into sections for paginated reading."""
    match = ISSUE_RE.match(path.stem)
    if not match:
        return None

    text = path.read_text(encoding="utf-8")
    state = STATE_RE.search(text)
    reviewed = (state.group(1) if state else "reviewed") == "reviewed"
    reviewed_on = None
    if reviewed:
        found = REVIEWED_ON_RE.search(text)
        reviewed_on = found.group(1) if found else None

    lines = text.splitlines()
    title = next((l.lstrip("# ").strip() for l in lines if l.startswith("# ")), path.stem)
    title = title.split("·")[0].strip()

    # Everything before the first "## " is the issue's opening.
    body = text.split("\n# ", 1)[-1]
    body = body.split("\n", 1)[-1] if "\n" in body else ""
    parts = re.split(r"\n##\s+", body)

    intro_html = to_html(parts[0]) if parts else ""
    sections = []
    for part in parts[1:]:
        head, _, rest = part.partition("\n")
        sections.append({
            "heading": head.strip(),
            "html": to_html(rest),
        })

    return {
        "id": path.stem,
        "year": int(match.group(1)),
        "week": int(match.group(2)),
        "title": title,
        "reviewed": reviewed,
        "reviewed_on": reviewed_on,
        "intro_html": intro_html,
        "sections": sections,
        "source": (
            "https://github.com/atultiwari/awesome-ai-pathology/blob/main/"
            f"digest/{path.name}"
        ),
    }


def collect(root: Path) -> list[dict[str, Any]]:
    """Every published issue, newest first. Companion -full listings excluded."""
    directory = Path(root) / "digest"
    if not directory.is_dir():
        return []
    issues = [
        parse_issue(path)
        for path in sorted(directory.glob("*.md"), reverse=True)
        if not path.stem.endswith("-full")
    ]
    return [issue for issue in issues if issue]
