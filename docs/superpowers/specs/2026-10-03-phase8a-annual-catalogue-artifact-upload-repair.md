# Phase 8A — Annual Catalogue Hidden-Artifact Upload Repair

**Date:** 2026-10-03  
**Status:** UPLOAD PACKAGING REPAIRED / REPLACEMENT EXECUTION LOCKED  
**Decision:** DEC-496  
**Predecessor:** DEC-495

DEC-496 repairs only the GitHub Actions artifact-packaging defect that terminated
the first 2015 run before cell execution.

The active annual workflow now sets `include-hidden-files: true` on exactly three
`actions/upload-artifact@v6` steps:

- `.preflight`;
- `.result`;
- `.annual-freeze/annual-freeze.json`.

The pre-repair workflow is preserved as an exact test fixture with blob
`31633e87b79551f5b7dfa6b0deb76a82eb070129`. The repaired active workflow blob is
`f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

No execution scope is broadened. The failed first-run authorization remains
consumed, and rerun/retry/replacement authority remains false.

## Next gate

`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_REPLACEMENT_RUN_AUTHORIZATION_BEFORE_DISPATCH`
