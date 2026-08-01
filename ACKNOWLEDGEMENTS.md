# Acknowledgements

This catalogue stands on work done by many others.

## Awesome-Pathology-VLMs

The vision-language model section was seeded from
[**Awesome-Pathology-VLMs**](https://github.com/wenhaozhang0066/Awesome-Pathology-VLMs)
(Apache-2.0), a focused and well-maintained bibliography of pathology VLMs.

Two things were taken from it:

1. **Curation** — which models exist, which paper describes each, and how they group by training
   paradigm (contrastive, generative, reasoning, agent-based, VLM-augmented MIL). Those groupings
   are preserved in the `subcategories` field of each entry.
2. **The granularity convention** — `G1` patch/tile, `G2` region of interest, `G3` whole-slide
   image. It is a genuinely useful axis that we have not seen elsewhere, and it is used verbatim so
   that entries can be cross-referenced between the two projects.

**Summaries were rewritten.** No prose from that repository is reproduced here. Where a fact could
not be independently confirmed, the entry says less rather than guessing.

If you want the academic VLM literature in depth, go there — it covers that ground more thoroughly
than this catalogue intends to.

```bibtex
@misc{awesome_pathology_vlms,
  title   = {Awesome-Pathology-VLMs},
  author  = {{Awesome-Pathology-VLMs Contributors}},
  journal = {Github repository},
  year    = {2026},
  url     = {https://github.com/wenhaozhang0066/Awesome-Pathology-VLMs},
}
```

## openFDA

Every regulatory claim in this catalogue was located through the
[openFDA](https://open.fda.gov/) device APIs and then linked to the FDA's own record on
`accessdata.fda.gov`. No regulatory status here is taken from vendor marketing.

openFDA data carries the agency's own caveat: it is not a substitute for the official record, and
should not be relied upon to make decisions about medical products without independent
verification. Treat every entry here the same way — the link is provided so you can check it
yourself, and you should.

## The projects themselves

Every tool, model, dataset and benchmark listed here represents years of work by researchers,
engineers and clinicians who chose to release it publicly. The licences under which they did so
are recorded per entry; please honour them, and cite the original work rather than this list when
you use something you found through it.

## Corrections

If your work is described inaccurately here, or credited insufficiently,
[please open an issue](https://github.com/atultiwari/awesome-ai-pathology/issues/new/choose).
Corrections take priority over everything else.
