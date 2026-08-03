<!--
Thank you for contributing. CI checks the mechanical things automatically —
schema, vocabulary, links, generated files — so do not worry about getting the
formatting perfect. It will tell you what to fix.
-->

## What does this change?

<!-- One or two sentences. -->

## Type of change

- [ ] Adding an entry
- [ ] Correcting a fact on an existing entry
- [ ] Fixing a broken link
- [ ] Marking something unmaintained or discontinued
- [ ] Tooling or documentation
- [ ] Something else

## Checklist

- [ ] I edited `data/entries/*.yaml` — **not** `README.md`, `browse/` or `api/`, which are generated
- [ ] `python3 tools/validate.py` passes locally *(or I am happy to let CI tell me)*
- [ ] I left the `metrics` block alone — it is maintained by the nightly job

## If this adds or changes a regulatory claim

<!-- Delete this section if it does not apply. -->

- [ ] The `reference` links the **regulator's own record** (e.g. `accessdata.fda.gov`), not a vendor page
- [ ] `verified_on` is the date I actually checked it
- [ ] The entry says nothing about jurisdictions I did not verify

> Regulatory claims are the highest-risk content here. A claim sourced from marketing
> material will be declined, however accurate it may turn out to be.

## If this adds a tool that handles patient images

- [ ] I set `sends_data_offsite` correctly, or left it `null` because I do not know

> This field tells a pathologist whether their slides leave the building. A wrong
> value is worse than a missing one — `null` is always an acceptable answer.

## Disclosure

- [ ] I am affiliated with this product (author, employee, vendor, or paid to promote it)

<!--
Affiliation is welcome — vendors correcting facts about their own products is
useful. It just needs to be stated. Promotional copy will be declined, politely.
-->
