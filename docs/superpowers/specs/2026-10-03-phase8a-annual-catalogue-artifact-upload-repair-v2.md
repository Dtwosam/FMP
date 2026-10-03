# Phase 8A — Annual Catalogue Artifact Upload Repair V2

**Date:** 2026-10-03  
**Status:** ARTIFACT UPLOAD DISTRIBUTION CORRECTED / REPLACEMENT RUN NOT STARTED  
**Decision:** DEC-502  
**Predecessor:** DEC-501

DEC-502 corrects the hidden-artifact upload repair before the authorized replacement
2015 run is dispatched.

The DEC-496 workflow blob
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92` contained three
`include-hidden-files: true` entries, but all three were attached to the preflight
upload. The cell and annual-freeze upload steps therefore still excluded their
hidden artifact paths.

DEC-502 preserves that workflow as an exact historical fixture and replaces the
live workflow with blob:

`09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`

The corrected workflow contains exactly one hidden-file flag in each upload block:

- preflight: `.preflight`;
- cell product: `.result`;
- annual freeze: `.annual-freeze/annual-freeze.json`.

DEC-496 through DEC-501 remain reproducible against the historical workflow
snapshot. DEC-502 does not dispatch the replacement run.

The existing replacement authorization/runtime chain must be refreshed against this
corrected workflow before execution.

2016+, cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live,
broker mutation, real-money action, and trading remain false.

## Next gate

`REFRESH_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_AGAINST_CORRECTED_WORKFLOW`
