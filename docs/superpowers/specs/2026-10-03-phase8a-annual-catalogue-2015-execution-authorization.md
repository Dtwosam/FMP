# Phase 8A — 2015 Annual Catalogue Execution Authorization

**Date:** 2026-10-03  
**Status:** FIRST 2015 RUN AUTHORIZED / NOT STARTED  
**Decision:** DEC-493  
**Predecessor:** DEC-492

DEC-493 records explicit operator authorization for exactly the first 2015
annual-pattern-catalogue workflow run.

It pins:
- DEC-492 execution-preflight source blob
  `d36343a6f2c69ccc2f942e537f5599cbc92b263b`;
- DEC-491 install-receipt source blob
  `970ab466dfa5f87c6955ad65da4653a993e9d6fd`;
- active annual workflow blob
  `31633e87b79551f5b7dfa6b0deb76a82eb070129`.

Authorized scope:
- annual segment: `2015` only;
- workflow run number: `1` only;
- workflow run attempt: `1` only;
- no predecessor freeze run;
- annual workflow dispatch: authorized for that exact first run;
- historical artifact reads: authorized for that exact 2015 run;
- annual catalogue execution: authorized for that exact 2015 run;
- annual result production: authorized for that exact 2015 run.

The DEC-475 default gate remains hard-closed when no exact 2015 run identity is
present. Runtime authorization is resolved from the workflow-dispatch event segment
plus `GITHUB_RUN_NUMBER` and `GITHUB_RUN_ATTEMPT`. A later segment, run #2, or
attempt #2 fails closed.

Rerun, retry, replacement run, 2016+, next-segment execution, cross-year result
production, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation,
real-money action, and trading remain false.

## Next gate

`EXACT_FIRST_2015_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`
