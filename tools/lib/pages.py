"""Page builders: README, browse facet pages, and the JSON API."""
from __future__ import annotations

import json
from datetime import date
from typing import Any, Mapping, Sequence

from lib.entries import Entry, public_view
from lib.facets import DERIVED, derived_index, facet_index
from lib.render import facet_page_path, relative_link, render_table
from lib.taxonomy import BROWSE_DIR, Taxonomy

SCHEMA_VERSION = "1.0.0"
REPO = "https://github.com/atultiwari/awesome-ai-pathology"
SITE = "https://pathologyai.org"

DISCLAIMER_SHORT = (
    "> **Not medical advice or a substitute for validation.** Inclusion is not endorsement. "
    "Regulatory clearance in one country says nothing about another. "
    "See [DISCLAIMER.md](DISCLAIMER.md)."
)

MAINTAINER = {
    "name": "Dr. Atul Tiwari",
    "roles": [
        "Associate Professor, Department of Pathology, Government Medical College, "
        "Chittorgarh, Rajasthan, India",
        "Additional Nodal Officer (AI/ML), Department of Medical Education, "
        "Government of Rajasthan, India",
    ],
    "orcid": "0000-0002-8048-9541",
    "declaration": "No commercial affiliations. No sponsored placements. No affiliate links.",
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
                meta.get("label", value), meta.get("explanation"), group, taxonomy, depth=2
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
    taxonomy: Taxonomy, depth: int,
) -> str:
    parts = [
        f"# {title}",
        "",
        f"[← Back to the index]({relative_link('README.md', depth)})",
        "",
    ]
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

def readme(entries: Sequence[Entry], taxonomy: Taxonomy) -> str:
    parts: list[str] = []
    parts += _header(entries)
    parts += _browse_matrix(entries, taxonomy)
    parts += _sections(entries, taxonomy)
    parts += _about()
    return "\n".join(parts)


def _header(entries: Sequence[Entry]) -> list[str]:
    return [
        "# Awesome AI in Pathology",
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
        "Curated by a practising pathologist, for **pathologists and researchers alike**. "
        "Every entry records what it costs, what hardware it needs, whether it works offline, "
        "whether it uploads your slides, and where it stands with regulators.",
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
    lines.append("**Constraints**  " + " · ".join(
        f"[{declared.get(key, {}).get('emoji','')} "
        f"{declared.get(key, {}).get('label', key)}]({facet_page_path('settings', key)})".strip()
        for key in DERIVED if derived.get(key)
    ))
    lines.append("")

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
        "Suggestions are very welcome via "
        f"[Issues]({REPO}/issues/new/choose). Pull requests open once the taxonomy settles — "
        "see [CONTRIBUTING.md](CONTRIBUTING.md).",
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

def api_documents(entries: Sequence[Entry], taxonomy: Taxonomy, today: str) -> dict[str, str]:
    payload = [public_view(e) for e in entries]

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
        "derived_facets": {k: len(v) for k, v in derived_index(entries).items()},
        "maintainer": MAINTAINER,
        "repo": REPO,
        "site": SITE,
    }

    return {
        "api/v1/entries.json": _dump(entries_doc),
        "api/v1/taxonomy.json": _dump(taxonomy_doc),
        "api/v1/search-index.json": _dump(search_doc),
        "api/v1/stats.json": _dump(stats_doc),
    }


def api_index_html(entries: Sequence[Entry], taxonomy: Taxonomy, today: str) -> str:
    """Landing page for the API host, so its root is not a bare 404.

    Self-contained: no external CSS, fonts or scripts. Adapts to light and dark.
    """
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
       generated {today}</p>
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
