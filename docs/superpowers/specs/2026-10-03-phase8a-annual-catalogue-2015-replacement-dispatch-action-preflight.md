# Phase 8A — Final 2015 Replacement Dispatch Action Preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY REPLACEMENT DISPATCH READY  
**Decision:** DEC-499  
**Predecessor:** DEC-498

DEC-499 is the final read-only preflight before the single authorized repaired
2015 replacement annual-catalogue workflow dispatch.

It pins:
- DEC-498 replacement-authorization source blob
  `c63fc9f72ad34fa6fd903f2dde8e85570521c9b9`;
- live replacement runtime blob
  `ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b`;
- repaired annual workflow blob
  `f7e65ee95f472918e390bceedd7cf2f38bbf7e92`.

It requires:
- exact current `main`;
- exactly one prior annual workflow run;
- that run is exactly failed run `37126711695`, #1 / attempt 1;
- annual segment `2015`;
- empty prior-freeze input;
- expected replacement identity #2 / attempt 1;
- DEC-498 replacement read/execution/result authority active.

DEC-499 contains no dispatch command and is plan-only.

Failed-run rerun/retry, run #3+, 2016+, cross-year results, Strategy V1 synthesis,
promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading
remain false.

## Next gate

`EXACT_2015_REPLACEMENT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`
