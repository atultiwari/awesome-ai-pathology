"""Page builders: README, browse facet pages, and the JSON API."""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Mapping, Sequence

from lib.entries import Entry, public_view
from lib.facets import DERIVED, derived_facets, derived_index, facet_index
from lib.render import facet_page_path, relative_link, render_table
from lib.skill import LEVELS, SKILL_LABELS, skill_level
from lib.taxonomy import BROWSE_DIR, Taxonomy

SCHEMA_VERSION = "1.0.0"
REPO = "https://github.com/atultiwari/awesome-ai-pathology"
SITE = "https://pathologyai.org"

DISCLAIMER_SHORT = (
    "> **Not medical advice or a substitute for validation.** Inclusion is not endorsement. "
    "Regulatory clearance in one country says nothing about another. "
    "See [DISCLAIMER.md](DISCLAIMER.md)."
)

# Shown at the top of any facet page listing devices cleared for clinical use.
# These are the highest-stakes pages in the catalogue: a reader could plausibly
# treat them as a procurement shortlist, which they are not.
REGULATORY_NOTICE = """> [!CAUTION]
> **Read this before treating anything below as cleared for your use.**
>
> **This page is not a procurement list, an approval list, or a recommendation.**
> It records what a regulator has published, nothing more. The maintainer is not a
> regulatory authority and has no role in any clearance decision.
>
> - **Every status here was transcribed from the regulator's own public record on the
>   date shown, and may since have changed.** Follow the badge on each row to the
>   primary record and confirm it yourself. Do not rely on this page.
> - **Clearance is not proof of clinical benefit.** An FDA 510(k) means the device was
>   found substantially equivalent to an existing one. It is not a finding that the
>   device improves diagnosis, accuracy or patient outcomes.
> - **Clearance is specific to a stated indication for use.** A device cleared for one
>   task, one specimen type or one scanner is not cleared for anything else. The
>   indication is in the linked record; the one-line summary here is not a substitute
>   for reading it.
> - **Clearance is specific to one jurisdiction.** An FDA clearance carries no weight
>   in India, the European Union, the United Kingdom or anywhere else. If you practise
>   outside the United States, **nothing on this page tells you what you may lawfully
>   use** — check CDSCO, the IVDR, UKCA or your own national authority.
> - **Local validation is still required.** Reported performance does not transfer
>   between laboratories; scanner, stain protocol and patient population all shift
>   results. Your institution remains responsible for validating any tool before
>   clinical use, and for every decision made with it.
> - **No performance claims appear here**, and no product on this page is endorsed,
>   ranked or sponsored.
>
> If anything here is inaccurate, [please report it]({report_url}) — corrections take
> priority over everything else."""

REPORT_URL = f"{REPO}/issues/new/choose"

MAINTAINER = {
    "name": "Dr. Atul Tiwari",
    "roles": [
        "Associate Professor, Department of Pathology, Government Medical College, "
        "Chittorgarh, Rajasthan, India",
        "Additional Nodal Officer (AI/ML), Department of Medical Education, "
        "Government of Rajasthan, India",
    ],
    "orcid": "0000-0002-8048-9541",
    "declaration": "No third-party sponsorship, paid placement, or affiliate arrangements. Links to the maintainer's own teaching and research pages are his own.",
    "independence": (
        "This is a personal project. It is not an official publication of Government Medical "
        "College Chittorgarh or the Government of Rajasthan, and inclusion of any product does "
        "not constitute endorsement by any institution."
    ),
}


# ── browse pages ─────────────────────────────────────────────────────────

def browse_pages(
    entries: Sequence[Entry], taxonomy: Taxonomy
) -> dict[str, str]:
    """Every facet page, keyed by repo-relative path."""
    pages: dict[str, str] = {}

    for kind, field in (
        ("categories", "category"), ("tasks", "tasks"),
        ("subspecialties", "subspecialty"), ("organs", "organs"),
        ("audience", "audience"), ("stage", "stage"),
    ):
        for value, group in facet_index(entries, field).items():
            if not taxonomy.has(kind, value):
                continue
            pages[facet_page_path(kind, value)] = _facet_page(
                taxonomy.label(kind, value),
                taxonomy.meta(kind, value).get("description")
                or taxonomy.meta(kind, value).get("blurb"),
                group, taxonomy, depth=2,
            )

    for value, group in facet_index(entries, "_regulatory_status").items():
        if taxonomy.has("regulatory", value):
            meta = taxonomy.meta("regulatory", value)
            pages[facet_page_path("regulatory", value)] = _facet_page(
                meta.get("label", value), meta.get("explanation"), group, taxonomy, depth=2,
                # Devices cleared for clinical use somewhere get the full notice.
                notice=REGULATORY_NOTICE.format(report_url=REPORT_URL)
                if meta.get("clinical") else None,
            )

    declared = taxonomy.settings_facets()
    for value, group in derived_index(entries).items():
        meta = declared.get(value, {})
        pages[facet_page_path("settings", value)] = _facet_page(
            meta.get("label", value), meta.get("blurb"), group, taxonomy, depth=2
        )

    # browse/all.md sits one level down, not two.
    pages["browse/all.md"] = _facet_page(
        "Everything", f"All {len(entries)} entries, alphabetically.",
        entries, taxonomy, depth=1,
    )
    return pages


def _facet_page(
    title: str, blurb: str | None, group: Sequence[Entry],
    taxonomy: Taxonomy, depth: int, notice: str | None = None,
) -> str:
    parts = [
        f"# {title}",
        "",
        f"[← Back to the index]({relative_link('README.md', depth)})",
        "",
    ]
    if notice:
        parts += [notice, ""]
    if blurb:
        parts += [_clean(blurb), ""]
    parts += [f"**{len(group)}** {'entry' if len(group) == 1 else 'entries'}.", ""]
    parts += [
        render_table(group, taxonomy, depth=depth),
        "", "---", "",
        DISCLAIMER_SHORT.replace(
            "(DISCLAIMER.md)", f"({relative_link('DISCLAIMER.md', depth)})"
        ),
        "",
    ]
    return "\n".join(parts)


# ── README ───────────────────────────────────────────────────────────────

def readme(entries: Sequence[Entry], taxonomy: Taxonomy, root=None) -> str:
    parts: list[str] = []
    parts += _header(entries)

    digest = latest_digest(root) if root else None
    if digest:
        path, title = digest
        parts += [
            f"## [{title}]({path})",
            "",
            "Assembled automatically every week so the week's work reaches you while it is "
            "still the week's work. Reading happens after — each issue is labelled "
            "**reviewed** or **awaiting review**, and back issues get marked as they are "
            "read. [All issues](digest/).",
            "",
            "---",
            "",
        ]

    parts += _browse_matrix(entries, taxonomy)
    parts += _sections(entries, taxonomy)
    parts += _about()
    return "\n".join(parts)


def latest_digest(root) -> tuple[str, str] | None:
    """(path, title) of the most recent digest, or None.

    Digests are hand-written editorial, not generated — the generator only
    discovers and links the newest one so the README never goes stale.
    """
    from pathlib import Path

    directory = Path(root) / "digest"
    if not directory.is_dir():
        return None
    issues = sorted(
        (p for p in directory.glob("*.md") if not p.stem.endswith("-full")),
        reverse=True,
    )
    if not issues:
        return None

    newest = issues[0]
    title = newest.stem
    for line in newest.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            break
    return f"digest/{newest.name}", title


def _header(entries: Sequence[Entry]) -> list[str]:
    return [
        "# Awesome AI in Pathology",
        "",
        "> **Envisioned by a pathologist, for fellow pathologists.**  ",
        "> Discovery runs continuously; judgement is applied by one person, as time allows. "
        "Everything is labelled with which stage it has reached — so you always know whether "
        "you are reading something checked, or something merely found.",
        "",
        "<p align='center'>",
        "  <a href='https://github.com/sindresorhus/awesome'>"
        "<img src='https://awesome.re/badge.svg' alt='Awesome'></a>",
        f"  <img src='https://img.shields.io/badge/entries-{len(entries)}-blue.svg' alt='entries'>",
        "  <a href='LICENSE'>"
        "<img src='https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey.svg' alt='content licence'></a>",
        "  <a href='LICENSE-CODE'>"
        "<img src='https://img.shields.io/badge/code-MIT-lightgrey.svg' alt='code licence'></a>",
        "</p>",
        "",
        "**Everything in AI for pathology — from the paper to the plugin to the product — "
        "with an honest note on whether you are allowed to use it on a patient.**",
        "",
        "Built for **pathologists and researchers alike**. Every entry records what it costs, "
        "what hardware it needs, whether it works offline, whether it uploads your slides, and "
        "where it stands with regulators.",
        "",
        DISCLAIMER_SHORT,
        "",
        "---",
        "",
    ]


def _browse_matrix(entries: Sequence[Entry], taxonomy: Taxonomy) -> list[str]:
    lines = ["## Browse by", ""]

    lines.append("**I am a…**  " + " · ".join(
        f"[{taxonomy.meta('audience', key).get('emoji','')} "
        f"{taxonomy.label('audience', key)}]({facet_page_path('audience', key)})".strip()
        for key, _ in taxonomy.ordered("audience")
        if facet_index(entries, "audience").get(key)
    ))
    lines.append("")

    clinician_tasks = [
        (key, meta) for key, meta in taxonomy.terms("tasks").items()
        if meta.get("clinician_facing") and facet_index(entries, "tasks").get(key)
    ]
    lines.append("**I want to…**  " + " · ".join(
        f"[{meta['label']}]({facet_page_path('tasks', key)})" for key, meta in clinician_tasks[:10]
    ))
    lines.append("")

    derived = derived_index(entries)
    declared = taxonomy.settings_facets()

    # The Stale Shelf is an honesty signal, not a constraint — it gets its own
    # line rather than sitting beside "runs on a laptop".
    constraint_keys = [k for k in DERIVED if k != "stale-shelf" and derived.get(k)]
    lines.append("**Constraints**  " + " · ".join(
        f"[{declared.get(key, {}).get('emoji','')} "
        f"{declared.get(key, {}).get('label', key)}]({facet_page_path('settings', key)})".strip()
        for key in constraint_keys
    ))
    lines.append("")

    if derived.get("stale-shelf"):
        count = len(derived["stale-shelf"])
        lines += [
            f"**Freshness**  [🕯️ The Stale Shelf]({facet_page_path('settings', 'stale-shelf')}) "
            f"— {count} listed projects whose upstream has gone quiet. Shown rather than "
            "quietly dropped, because a list that hides dead projects implies everything "
            "else is alive.",
            "",
        ]

    reg = facet_index(entries, "_regulatory_status")
    lines.append("**Regulatory status**  " + " · ".join(
        f"[{taxonomy.label('regulatory', key)}]({facet_page_path('regulatory', key)})"
        for key, _ in sorted(reg.items()) if taxonomy.has("regulatory", key)
    ))
    lines += ["", f"[**See everything →**](browse/all.md)", "", "---", ""]
    return lines


def _sections(entries: Sequence[Entry], taxonomy: Taxonomy) -> list[str]:
    by_category = facet_index(entries, "category")
    lines: list[str] = ["## Contents", ""]

    ordered = [(key, meta) for key, meta in taxonomy.ordered("categories") if by_category.get(key)]
    for key, meta in ordered:
        lines.append(f"- [{meta['label']}](#{_anchor(meta['label'])}) ({len(by_category[key])})")
    lines += ["", "---", ""]

    for key, meta in ordered:
        group = by_category[key]
        # Emoji stay OUT of headings: GitHub strips them when building an
        # anchor but leaves the separating space, so "## 🧠 Foundation Models"
        # anchors as "#-foundation-models" and every ToC link breaks.
        lines += [
            f"## {meta['label']}",
            "",
            f"{meta.get('emoji', '')} {_clean(meta.get('description', ''))}".strip(),
            "",
            render_table(group, taxonomy, depth=0),
            "",
            f"[Browse all {meta['label']} →]({facet_page_path('categories', key)})",
            "",
        ]
    return lines


def _about() -> list[str]:
    return [
        "---",
        "",
        "## About",
        "",
        f"**Curated by {MAINTAINER['name']}**  ",
        "  \n".join(MAINTAINER["roles"]),
        "  ",
        f"ORCID: [{MAINTAINER['orcid']}](https://orcid.org/{MAINTAINER['orcid']})",
        "",
        f"*{MAINTAINER['declaration']}*",
        "",
        f"> {MAINTAINER['independence']}",
        "",
        "## Contributing",
        "",
        f"**[Suggest an entry]({REPO}/issues/new/choose)** — a short form, no git needed. "
        f"Or **[send a pull request]({REPO}/pulls)** if you prefer to edit the data directly. "
        "Both are open. See [CONTRIBUTING.md](CONTRIBUTING.md) for what gets included, and "
        "for the rule that regulatory claims must cite the regulator rather than the vendor.",
        "",
        "## Acknowledgements",
        "",
        "The vision-language section was seeded from "
        "[Awesome-Pathology-VLMs](https://github.com/wenhaozhang0066/Awesome-Pathology-VLMs), "
        "whose patch/ROI/slide granularity convention is used here too. Regulatory claims are "
        "sourced through [openFDA](https://open.fda.gov/) and linked to the FDA's own records. "
        "Full credits in [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md).",
        "",
        "## Licence",
        "",
        "Content [CC BY 4.0](LICENSE) · code [MIT](LICENSE-CODE).",
        "",
        "<sub>README, browse pages and the JSON API are generated from `data/entries/*.yaml`. "
        "Do not edit them by hand.</sub>",
        "",
    ]


# ── JSON API ─────────────────────────────────────────────────────────────

def api_documents(
    entries: Sequence[Entry], taxonomy: Taxonomy, today: str, root=None
) -> dict[str, str]:
    # skill_level and facets are derived, so they are computed here rather
    # than stored: the website should never have to re-implement the rule, and
    # a stored copy could contradict the entry it describes.
    payload = [
        {**public_view(e), "skill_level": skill_level(e), "facets": list(derived_facets(e))}
        for e in entries
    ]

    entries_doc = {
        "generated_at": today,
        "schema_version": SCHEMA_VERSION,
        "count": len(payload),
        "entries": payload,
    }

    taxonomy_doc = {
        "generated_at": today,
        "schema_version": SCHEMA_VERSION,
        "vocabularies": {
            kind: dict(taxonomy.terms(kind))
            for kind in ("categories", "tasks", "subspecialties", "organs",
                         "regulatory", "audience", "stage")
        },
        "derived_facets": dict(taxonomy.settings_facets()),
        "skill_levels": dict(SKILL_LABELS),
        "browse_directories": dict(BROWSE_DIR),
    }

    search_doc = {
        "generated_at": today,
        "entries": [
            {
                "id": e["id"], "name": e["name"], "tagline": e["tagline"],
                "category": e["category"], "tasks": list(e.get("tasks", [])),
                "subspecialty": list(e.get("subspecialty", [])),
                "organs": list(e.get("organs", [])),
                "skill_level": skill_level(e),
            }
            for e in entries
        ],
    }

    stats_doc = {
        "generated_at": today,
        "total_entries": len(entries),
        "by_category": _tally(entries, "category"),
        "by_regulatory_status": _tally(entries, "_regulatory_status"),
        "by_stage": _tally(entries, "stage"),
        "by_skill_level": {
            level: sum(1 for e in entries if skill_level(e) == level)
            for level in LEVELS
        },
        "derived_facets": {k: len(v) for k, v in derived_index(entries).items()},
        "maintainer": MAINTAINER,
        "repo": REPO,
        "site": SITE,
    }

    # Digests are editorial markdown; this exposes them as structured data so
    # the website can render an issue without shipping a markdown parser, and
    # without needing a rebuild when an issue is published.
    from lib.digest import collect

    issues = collect(root) if root else []
    digest_doc = {
        "generated_at": today,
        "schema_version": SCHEMA_VERSION,
        "count": len(issues),
        "latest": issues[0]["id"] if issues else None,
        "pending_review": sum(1 for i in issues if not i["reviewed"]),
        "issues": issues,
    }

    return {
        "api/v1/entries.json": _dump(entries_doc),
        "api/v1/taxonomy.json": _dump(taxonomy_doc),
        "api/v1/search-index.json": _dump(search_doc),
        "api/v1/stats.json": _dump(stats_doc),
        "api/v1/digest.json": _dump(digest_doc),
    }


def api_index_html(entries: Sequence[Entry], taxonomy: Taxonomy, today: str) -> str:
    """Landing page for the API host, so its root is not a bare 404.

    Self-contained: no external CSS, fonts or scripts. Adapts to light and dark.

    Deliberately carries NO build date. Embedding one made the file change every
    day regardless of content, which produced a daily no-op commit from the
    generate workflow. The timestamp lives in stats.json, which is data.
    """
    _ = today  # retained for signature symmetry with api_documents()
    counts = _tally(entries, "category")
    rows = "\n".join(
        f"      <tr><td>{taxonomy.label('categories', key)}</td><td>{value}</td></tr>"
        for key, value in sorted(counts.items(), key=lambda kv: -kv[1])
        if taxonomy.has("categories", key)
    )
    endpoints = "\n".join(
        f'      <li><a href="{path}"><code>/{path}</code></a> — {blurb}</li>'
        for path, blurb in (
            ("api/v1/entries.json", "every entry, in full"),
            ("api/v1/taxonomy.json", "vocabularies, labels and facet definitions"),
            ("api/v1/search-index.json", "lightweight index for client-side search"),
            ("api/v1/stats.json", "counts, facet tallies and maintainer details"),
        )
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pathology AI Library — API</title>
<meta name="description" content="JSON API for the Awesome AI in Pathology catalogue.">
<style>
  :root {{ color-scheme: light dark; --fg:#111; --muted:#555; --bg:#fff;
           --line:#e3e3e3; --accent:#0b5fff; --code:#f5f5f7; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fg:#e8e8ea; --muted:#a0a0a8; --bg:#131316;
             --line:#2a2a30; --accent:#7aa2ff; --code:#1c1c21; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:2.5rem 1.25rem; background:var(--bg); color:var(--fg);
          font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
  main {{ max-width: 44rem; margin: 0 auto; }}
  h1 {{ font-size:1.6rem; margin:0 0 .25rem; letter-spacing:-.01em; }}
  h2 {{ font-size:1.05rem; margin:2rem 0 .5rem; }}
  p.lede {{ color:var(--muted); margin:0 0 1.5rem; }}
  a {{ color:var(--accent); }}
  code {{ background:var(--code); padding:.15em .4em; border-radius:4px;
          font-size:.9em; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
  ul {{ padding-left:1.1rem; }} li {{ margin:.4rem 0; }}
  table {{ border-collapse:collapse; width:100%; margin-top:.5rem; }}
  td {{ padding:.35rem .5rem; border-bottom:1px solid var(--line); }}
  td:last-child {{ text-align:right; color:var(--muted); font-variant-numeric:tabular-nums; }}
  footer {{ margin-top:2.5rem; padding-top:1rem; border-top:1px solid var(--line);
            color:var(--muted); font-size:.875rem; }}
  .wrap {{ overflow-x:auto; }}
</style>
</head>
<body>
<main>
  <h1>Pathology AI Library — API</h1>
  <p class="lede">Machine-readable data behind
    <a href="{REPO}">Awesome AI in Pathology</a>.
    {len(entries)} entries, regenerated on every change. Served as static JSON with
    <code>access-control-allow-origin: *</code>, so it can be fetched from anywhere.</p>

  <h2>Endpoints</h2>
  <ul>
{endpoints}
  </ul>

  <h2>Catalogue</h2>
  <div class="wrap"><table>
{rows}
  </table></div>

  <h2>Use</h2>
  <p>Content is licensed <a href="{REPO}/blob/main/LICENSE">CC BY 4.0</a> — reuse it freely
     with attribution. The third-party tools and models it describes each carry their own
     licence, recorded per entry.</p>

  <footer>
    <p><strong>Not medical advice.</strong> Inclusion is not endorsement. Regulatory clearance
       in one country says nothing about another.
       <a href="{REPO}/blob/main/DISCLAIMER.md">Read the disclaimer</a>.</p>
    <p>Curated by {MAINTAINER['name']} ·
       <a href="https://orcid.org/{MAINTAINER['orcid']}">ORCID</a> ·
       last generated shown in
       <a href="api/v1/stats.json"><code>stats.json</code></a></p>
  </footer>
</main>
</body>
</html>
"""


def _dump(doc: Mapping[str, Any]) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def _tally(entries: Sequence[Entry], field: str) -> dict[str, int]:
    return {key: len(group) for key, group in sorted(facet_index(entries, field).items())}


def _anchor(heading: str) -> str:
    keep = [c for c in heading.lower() if c.isalnum() or c in " -"]
    return "".join(keep).strip().replace(" ", "-")


def _clean(text: str) -> str:
    return " ".join(text.split())


def today_iso() -> str:
    return date.today().isoformat()
