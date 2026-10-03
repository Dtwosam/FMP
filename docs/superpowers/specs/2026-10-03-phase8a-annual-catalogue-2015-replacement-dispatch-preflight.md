# Phase 8A — 2015 Replacement-Run Dispatch Preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY REPLACEMENT PREFLIGHT / AUTHORIZATION LOCKED  
**Decision:** DEC-497  
**Predecessor:** DEC-496

DEC-497 defines the read-only preflight for a possible replacement 2015 annual-pattern-catalogue run after the consumed failed first attempt.

It pins:
- DEC-495 failure-receipt source blob
  `1ae96e83dc5d895dce1c5f981f1c785401de22f5`;
- DEC-496 upload-repair source blob
  `adfa75b352a561667b8c23efbcfb07af804d1131`;
- repaired active annual workflow blob
  `f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

The preflight requires:
- exact current `main`;
- exactly one prior annual-pattern-catalogue workflow run;
- that run is exactly `37126711695`, run #1 / attempt 1;
- that run is a completed failure on the frozen first-run head;
- annual segment remains `2015`;
- no previous annual freeze run;
- expected replacement identity is run #2 / attempt 1.

DEC-497 exposes only a `plan` CLI. It contains no dispatch/run/execute command.

Replacement dispatch, historical artifact reads, catalogue execution/results, 2016+,
cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live,
broker mutation, real-money action, and trading remain false.

## Next gate

`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_REPLACEMENT_RUN_AUTHORIZATION_BEFORE_DISPATCH`
