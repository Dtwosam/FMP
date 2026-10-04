# Phase 8A — 2018 Annual Dispatch Preflight

**Date:** 2026-10-04  
**Status:** READ-ONLY CONCRETE PREFLIGHT / DISPATCH LOCKED  
**Decision:** DEC-551

## Concrete installed source

DEC-551 consumes only the successful DEC-550 runtime-install evidence:

- installer workflow run: `37233054691` / attempt 1;
- installer workflow head: `11048bd278bbf8f3697571aaff40c27656449a6c`;
- install artifact: `11314488545`;
- artifact digest:
  `sha256:8b9732b24a5ef6163d8ab54f34d058eecd9e1c4ce1a68c79a88306178933df2d`;
- exact install commit:
  `1fc73dfc1e102996cecd5b9ffcb75d3ab4fa3ade`.

The installed runtime is exact:

- 2018 gate blob:
  `cd50f50156cf74c34cd97d69d24291dc373b390f`;
- annual runtime blob:
  `410180c34a9e3500bbbb42310a5253b993ac7785`.

## Exact annual history

The preflight accepts only this completed manual-dispatch inventory:

- run 1: failure;
- run 376: failure;
- run 377: success (2015);
- run 378: success (2016);
- run 379: success (2017).

No run 380 or later may exist.

## Frozen future dispatch

DEC-551 freezes only:

- ref: `main`;
- annual segment: `2018`;
- expected workflow run: `380`;
- expected attempt: `1`;
- previous annual freeze run ID: `37227536041`.

The repository-hosted builder is path-scoped and read-only. It downloads and
digest-verifies the exact DEC-550 receipt, requires the concrete install commit
as an ancestor of its landing commit, rechecks current main, installed runtime
blobs, and the exact annual inventory, then emits one immutable DEC-551
preflight artifact.

## Authority boundary

DEC-551 does not authorize annual workflow dispatch, historical reads,
historical catalogue execution, result production, repository mutation, rerun,
retry, run 381+, 2019+, cross-year synthesis, Strategy V1 promotion, Phase 8B,
broker mutation, demo/live orders, real-money action, or trading.

## Next gate

`ANNUAL_PATTERN_CATALOGUE_2018_DISPATCH_AUTHORIZATION_BEFORE_RUN`
