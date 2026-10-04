# Phase 8A — 2017 Runtime Authorization Install Executor

**Date:** 2026-10-04  
**Status:** EXACT TWO-FILE MUTATION / ANNUAL DISPATCH LOCKED  
**Decision:** DEC-539

## Concrete source action

DEC-539 consumes only successful DEC-538 evidence:

- workflow run: `37219170862` / attempt 1;
- workflow head: `7dfcf6cacca63719ac40a88858c69895fc68670b`;
- artifact: `11310165235`;
- artifact digest:
  `sha256:e210042872cbe191f4383fcba4a6ac9305fbdeb96acaed32d46e034acff1681d`.

## Exact mutation

The executor may change exactly two files:

1. create
   `src/fmp/discovery/annual_pattern_catalogue_2017_runtime_authorization.py`
   from blob `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
2. update
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from blob `b564f5a26fdef146fc6080962e7c4762b0b5949a`
   to blob `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`.

The target remains exact to annual segment 2017, workflow run 379 / attempt 1,
and predecessor run ID `37206992367`.

## Live guards

Before mutation the path-scoped installer requires the exact DEC-538 artifact,
current main equal to the installer landing commit, current runtime unchanged,
the 2017 gate absent, annual history exactly `{1, 376, 377, 378}`, run 379
absent, and a clean checkout.

After copying the frozen templates it requires exactly two changed paths, exact
target blobs, successful Python compilation/import, and a successful run-379
gate check. It re-fetches `origin/main` immediately before commit and refuses
to push if main moved.

## Concrete receipt

After the exact push, DEC-539 emits an immutable receipt proving the runtime
authorization is installed and active while annual dispatch, run 380+, 2018+,
strategy, broker/order, real-money, and trading authority remain false.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_PREFLIGHT`
