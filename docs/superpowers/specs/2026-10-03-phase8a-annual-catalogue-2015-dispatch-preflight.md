# Phase 8A — First 2015 Annual Catalogue Dispatch Preflight

**Date:** 2026-10-03  
**Status:** READ-ONLY FIRST DISPATCH PREFLIGHT  
**Decision:** DEC-494  
**Predecessor:** DEC-493

DEC-494 defines the final read-only preflight before the explicitly authorized
first 2015 annual-pattern-catalogue workflow dispatch.

It pins:
- DEC-493 authorization source blob
  `b5f394f7921d78f73636e28892575cbf4b64a95c`;
- DEC-493 runtime source blob
  `4f23996b90b4253af06774d0330003179264c8ee`;
- active annual workflow blob
  `31633e87b79551f5b7dfa6b0deb76a82eb070129`.

The preflight requires:
- exact current `main` identity;
- annual workflow run inventory exactly empty;
- annual segment `2015`;
- empty `previous_annual_freeze_run_id`;
- expected workflow run #1 / attempt 1;
- the DEC-493 authorization for dispatch, historical reads, 2015 execution, and
  2015 result production.

DEC-494 exposes only a `plan` CLI. It contains no dispatch/run/execute command
and no `gh workflow run` invocation.

Rerun, retry, replacement, 2016+, next-segment execution, cross-year results,
Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation,
real-money action, and trading remain false.

## Next gate

`EXACT_FIRST_2015_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN`
