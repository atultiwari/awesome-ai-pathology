# Contributing

Thank you for wanting to improve this. Suggestions from working pathologists are
especially valuable — you do not need to know git, YAML, or what a pull request
is in order to contribute.

## Right now: suggestions via Issues

**Issues are open. Pull requests are not yet.**

The first ~150 entries set the quality bar and settle the tag vocabulary.
Accepting external changes before that vocabulary is stable produces drift that
is expensive to undo, so the catalogue is being curated by one person for now.
PRs open once the taxonomy has settled.

This is not a brush-off — suggestions are genuinely wanted, and they get added.

👉 **[Suggest an entry](https://github.com/atultiwari/awesome-ai-pathology/issues/new/choose)**

Fill in the form. It asks for a link and a sentence; everything else is optional
and will be researched before the entry goes in.

## What gets included

An entry is admitted if it is:

1. **Specific to pathology**, or clearly applied to it
2. **Publicly accessible** — usable, downloadable, or at minimum properly documented
3. **Identifiable by a stable URL**
4. **Describable in one honest sentence**

## What does not

- Dead links and abandoned projects with no historical importance
- Vapourware — announcements without a released artefact
- Marketing pages that never say what the product actually does
- Anything requiring a sales call before you can learn what it is
- Paper-only entries with no artefact, unless the paper itself is a significant
  contribution

## Rules that are not negotiable

**Regulatory claims come from the regulator.** If you tell us something is
FDA-cleared or CE-marked, include a link to the *primary regulator record* — the
510(k) database entry, the EUDAMED listing. Vendor marketing is not a source. The
build rejects a clearance claim with no primary reference.

**No performance claims** unless they come from the regulatory submission or a
peer-reviewed publication, and always with the citation.

**No rankings, no "best", no affiliate links.** Ever.

**Vendors** may correct facts about their own product. Please say who you are.
Promotional copy will be declined, politely.

## For developers

The catalogue is generated. `data/entries/*.yaml` is the only source of truth —
`README.md`, `browse/**` and `api/v1/**` are all built from it and must never be
edited by hand.

```bash
pip install -r requirements.txt

python3 -m pytest tools/tests      # 76 tests
python3 tools/validate.py          # schema, vocabulary, cross-references
python3 tools/validate.py --check-links
python3 tools/generate.py          # rebuild README, browse/, api/
python3 tools/generate.py --check  # CI: fail if outputs are stale
```

### Adding an entry by hand

Create `data/entries/<id>.yaml`. The `id` must match the filename stem. Copy the
closest existing entry as a template and run `tools/validate.py` — it will tell
you precisely what is wrong.

Tag values are closed vocabularies in `data/taxonomy/*.yaml`. **An unknown tag
fails the build on purpose** — that is what stops the vocabulary fragmenting.
Proposing a new tag is fine; add it to the taxonomy file in the same change and
say why.

### The `metrics` block is bot-owned

`metrics` (stars, last commit, downloads) is filled by a scheduled job. Leave it
null. The validator rejects human-authored changes to it, which is what keeps bot
commits from colliding with your work.

### Two facts that matter more than they look

- **`sends_data_offsite`** — does using this transmit images to a third party?
  For a pathologist evaluating a hosted tool this is the single most important
  field on the page. Get it right, or leave it `null`.
- **`hardware_floor`** — what does it actually need to run? A `null` here means
  "not established" and, correctly, keeps the entry out of the low-resource
  lists. Never guess optimistically.

## Searching the catalogue

GitHub's in-repo code search works well against the YAML. Searching
`tasks: nuclei-segmentation` returns exactly the matching entry files.

## Licence

Content contributions are licensed [CC BY 4.0](LICENSE); code contributions
[MIT](LICENSE-CODE). By contributing you agree to license your contribution on
those terms.
