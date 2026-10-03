# Phase 8A — Annual Catalogue Artifact Upload Repair V2

**Date:** 2026-10-03  
**Status:** ARTIFACT UPLOAD DISTRIBUTION CORRECTED / EXECUTION NOT STARTED  
**Decision:** DEC-500  
**Predecessor:** DEC-499

DEC-500 corrects a defect in DEC-496's hidden-artifact upload repair before any
replacement 2015 run is dispatched.

The DEC-496 workflow blob
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92` contained three
`include-hidden-files: true` lines, but all three were attached to the preflight
upload. The cell and annual-freeze upload steps therefore still excluded hidden
paths.

DEC-500 preserves that flawed workflow as an exact fixture and replaces the live
workflow with blob:

`09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`

The corrected workflow has exactly three `actions/upload-artifact@v6` steps and
exactly one `include-hidden-files: true` inside each corresponding upload block:

- preflight: `.preflight`;
- cell product: `.result`;
- annual freeze: `.annual-freeze/annual-freeze.json`.

The correction does not itself authorize a replacement dispatch. Run #2
authorization remains represented by DEC-498, but the final dispatch preflight must
be refreshed against the corrected workflow before execution.

2016+, cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live,
broker mutation, real-money action, and trading remain false.

## Next gate

`REFRESH_2015_REPLACEMENT_DISPATCH_PREFLIGHT_AGAINST_CORRECTED_WORKFLOW`
