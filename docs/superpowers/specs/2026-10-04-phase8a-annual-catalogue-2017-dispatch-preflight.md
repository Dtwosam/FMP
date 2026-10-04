# Phase 8A — 2017 Annual Dispatch Preflight

**Date:** 2026-10-04  
**Status:** READ-ONLY CONCRETE PREFLIGHT / DISPATCH LOCKED  
**Decision:** DEC-540

## Concrete installed source

DEC-540 consumes only the successful DEC-539 runtime-install evidence:

- installer workflow run: `37219929487` / attempt 1;
- installer workflow head: `9c3e2e6042b5a00109ee1f07ad6fd24c9ac33308`;
- install artifact: `11309927463`;
- artifact digest:
  `sha256:6672b0642a763424541d971d84b273f8c2fde5089fcd736e6152fe8dc9a7e32e`;
- exact install commit:
  `dcdf7210b0039077efa3a23c65c2ed8fa41e2427`.

The installed runtime is exact:

- 2017 gate blob:
  `c1853eeec55ee98b3155a6054f07cf360793ba9b`;
- annual runtime blob:
  `e9cbc76dc9e6866e80088d223498fbcc3b870fd1`.

## Exact annual history

The preflight accepts only this completed manual-dispatch inventory:

- run 1: failure;
- run 376: failure;
- run 377: success (2015);
- run 378: success (2016).

No run 379 or later may exist.

## Frozen future dispatch

DEC-540 freezes only:

- ref: `main`;
- annual segment: `2017`;
- expected workflow run: `379`;
- expected attempt: `1`;
- previous annual freeze run ID: `37206992367`.

The repository-hosted builder is path-scoped and read-only. It downloads and
digest-verifies the exact DEC-539 receipt, rechecks current main, installed
runtime blobs, and the annual inventory, then emits one immutable DEC-540
preflight artifact.

## Authority boundary

DEC-540 does not authorize annual workflow dispatch, historical reads,
historical catalogue execution, result production, repository mutation, rerun,
retry, run 380+, 2018+, cross-year synthesis, Strategy V1 promotion, Phase 8B,
broker mutation, demo/live orders, real-money action, or trading.

## Next gate

`ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_AUTHORIZATION_BEFORE_RUN`
