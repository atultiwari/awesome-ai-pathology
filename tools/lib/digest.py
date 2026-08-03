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


# Formatting-only tags the issues legitimately use. Everything else is escaped,
# so hand-written editorial can never inject markup. Without this the literal
# text "<sub>" appeared throughout the published magazine.
_SAFE_INLINE = re.compile(r"&lt;(/?)(sub|sup|small|br)\s*/?&gt;")


def inline(text: str) -> str:
    """Convert inline markdown to HTML, escaping everything else."""
    out = html.escape(text, quote=False)
    out = _SAFE_INLINE.sub(lambda m: f"<{m.group(1)}{m.group(2)}>", out)
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


# An item block looks like:
#   **[Title](url)**
#   *Source*
#   Commentary, possibly wrapped over several lines.
# An optional leading "[8] " marks an editorial relevance score.
# Trailing text after the closing ** is allowed and kept as meta: the first
# published issue used "**[CORAL](url)** — ★55", which a stricter pattern
# silently dropped to prose. Parse the format that is actually written.
_ITEM_HEAD = re.compile(r"^\*\*\[([^\]]+)\]\(([^)\s]+)\)\*\*\s*(.*)$")
_SCORE = re.compile(r"^\[(\d{1,2})\]\s*")
_SOURCE = re.compile(r"^\*([^*]+)\*\s*$")


def domain_of(url: str) -> str:
    """Bare host, the way a newspaper prints a source. Empty for relative links."""
    match = re.match(r"^https?://(?:www\.)?([^/]+)", url or "")
    return match.group(1) if match else ""


def parse_blocks(markdown: str) -> list[dict[str, Any]]:
    """Split a section into structured items and surrounding prose.

    Magazine layout needs each item as data — headline, source, relevance,
    commentary — not one HTML blob. Prose that is not an item is kept as-is so
    editorial asides survive untouched.
    """
    blocks: list[dict[str, Any]] = []
    for chunk in re.split(r"\n\s*\n", markdown.strip()):
        lines = [l.strip() for l in chunk.splitlines() if l.strip()]
        if not lines:
            continue

        score = None
        head = lines[0]
        found = _SCORE.match(head)
        if found:
            score = int(found.group(1))
            head = _SCORE.sub("", head)

        item = _ITEM_HEAD.match(head)
        if not item:
            blocks.append({"kind": "prose", "html": to_html(chunk)})
            continue

        rest = lines[1:]
        source = (item.group(3) or "").strip().lstrip("—–-").strip()
        if rest and _SOURCE.match(rest[0]):
            source = _SOURCE.match(rest[0]).group(1).strip()
            rest = rest[1:]

        blocks.append({
            "kind": "item",
            "title": item.group(1),
            "url": item.group(2),
            "domain": domain_of(item.group(2)),
            "source": source,
            "score": score,
            "note_html": to_html(" ".join(rest)) if rest else "",
        })
    return blocks


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
        blocks = parse_blocks(rest)
        sections.append({
            "heading": head.strip(),
            "html": to_html(rest),
            "blocks": blocks,
            # Lets the renderer put substance first and fold the rest together:
            # a "nothing happened this week" note should not own a whole page.
            "item_count": sum(1 for b in blocks if b["kind"] == "item"),
        })

    return {
        "id": path.stem,
        "year": int(match.group(1)),
        "week": int(match.group(2)),
        "title": title,
        "reviewed": reviewed,
        "reviewed_on": reviewed_on,
        "intro_html": intro_html,
        "intro_blocks": parse_blocks(parts[0]) if parts else [],
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
