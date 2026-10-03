# Phase 8A — Annual Catalogue Proof-Workflow Dispatch Preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY CURRENT-MAIN DISPATCH PREFLIGHT / NO RUN  
**Decision:** DEC-486  
**Predecessor:** DEC-485

DEC-486 verifies the installed annual-catalogue install-preflight proof workflow
before any dispatch authorization can exist.

It pins:
- DEC-485 install-receipt source blob
  `638c988524ccf8ada27067c2b0bdb3403823a6f5`;
- active proof-workflow blob
  `0d6c93e2af04501f9ac2589fd24d6672b2b41910`.

A valid preflight requires:
- exact current `main` metadata and expected head SHA;
- active proof workflow present with the exact frozen blob;
- DEC-485 installed / available state;
- proof-workflow dispatch authority still false;
- zero proof-workflow runs.

The CLI exposes only `plan`. It has no dispatch, execute, run, install, or
advance surface.

Proof-workflow dispatch remains unauthorized. Annual-workflow installation and
dispatch, historical artifact reads, annual catalogue execution/result production,
next-segment execution, cross-year result production, Strategy V1 synthesis,
promotion, Phase 8B, demo/live, broker mutation, real-money action, and trading
remain false.

## Next gate

`EXPLICIT_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_BEFORE_RUN`

A separate operator authorization is required before the first proof-workflow run.
