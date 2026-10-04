# Phase 8A — 2018 Runtime Authorization Install Executor

**Date:** 2026-10-04  
**Status:** EXACT TWO-FILE MUTATION / ANNUAL DISPATCH LOCKED  
**Decision:** DEC-550

## Concrete source action

DEC-550 consumes only successful DEC-549 evidence:

- workflow run: `37232388248` / attempt 1;
- workflow head: `3cfd1b38217c97bbd590214394f171075d2d0f54`;
- artifact: `11313752760`;
- artifact digest:
  `sha256:94c9ce6e08f013cb9ff8f662c78b3fafc0ba902fa590e5b27e89751ddd9069a3`.

## Exact mutation

The executor may change exactly two files:

1. create
   `src/fmp/discovery/annual_pattern_catalogue_2018_runtime_authorization.py`
   from blob `cd50f50156cf74c34cd97d69d24291dc373b390f`;
2. update
   `src/fmp/discovery/annual_pattern_catalogue_runtime.py`
   from blob `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`
   to blob `410180c34a9e3500bbbb42310a5253b993ac7785`.

The target remains exact to annual segment 2018, workflow run 380 / attempt 1,
and predecessor run ID `37227536041`.

## Live guards

Before mutation the path-scoped installer requires the exact DEC-549 artifact,
current main equal to the installer landing commit, current runtime unchanged,
the 2018 gate absent, annual history exactly
`{1, 376, 377, 378, 379}`, run 380 absent, and a clean checkout.

After copying the frozen templates it requires exactly two changed paths, exact
target blobs, successful Python compilation/import, a successful run-380 gate
check, preservation of the run-379 2017 gate, and rejection of run 381. It
re-fetches `origin/main` immediately before commit and refuses to push if main
moved.

## Concrete receipt

After the exact push, DEC-550 emits an immutable receipt proving the 2018
runtime authorization is installed and active while annual dispatch, run 381+,
2019+, strategy/promotion, broker/order, real-money, and trading authority
remain false.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_DISPATCH_PREFLIGHT`
