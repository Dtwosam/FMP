# Phase 8A — Annual Catalogue Proof-Workflow Dispatch Authorization

**Date:** 2026-10-03  
**Status:** FIRST PROOF DISPATCH AUTHORIZED / RUN NOT STARTED  
**Decision:** DEC-487  
**Predecessor:** DEC-486

DEC-487 records explicit operator authorization for exactly one first invocation of
the installed annual-catalogue install-preflight proof workflow.

It pins:
- DEC-486 dispatch-preflight source blob
  `9f5d4b2abbfdb02280b0011a5d61e189be1d6fed`;
- active proof-workflow blob
  `0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

The authorized scope is exact:
- proof-workflow run count must still be zero before action;
- expected workflow run number is 1;
- expected workflow run attempt is 1;
- rerun, retry, and replacement are forbidden.

DEC-487 authorizes only the first manual proof-workflow dispatch. It does not itself
trigger the workflow.

Repository mutation remains false. Annual-workflow installation/dispatch,
historical artifact reads, annual catalogue execution/result production,
next-segment execution, cross-year result production, Strategy V1 synthesis,
promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading
remain false.

## Next gate

`EXACT_FIRST_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`

The runtime action must recheck current main and zero prior proof runs immediately
before triggering the workflow.
