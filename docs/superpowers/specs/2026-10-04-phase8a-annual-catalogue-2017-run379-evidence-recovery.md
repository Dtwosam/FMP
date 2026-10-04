# Phase 8A — 2017 Run-379 Evidence Recovery

**Date:** 2026-10-04  
**Status:** SOURCE-READY READ-ONLY RECOVERY / RUN 380 LOCKED  
**Decision:** DEC-544 recovery

## Observed state

Annual-catalogue run `37227536041` completed successfully as global run
`379` / attempt `1` on head
`7b4c1ef8573e280c067443b72f1534d9091d5b7f`.

The exact DEC-543 dispatcher run `37227526295` also completed successfully and
produced artifact `11313110298` with digest
`sha256:5a22e2c287e406add84c7709116e413d68e8b17e243abd33ca2b1ab7a2ceb6af`.

Run 379 produced the exact 2017 freeze artifact `11312736203` with digest
`sha256:f276bd11a394688dd894f1f73b93d3c22223b6b0942615e6c3f8f41a314c06f5`.

The installed DEC-544 `workflow_run` reviewer did not start automatically, so
no concrete DEC-544 artifact exists yet.

## Recovery

A separate path-scoped push workflow performs only the missing read-only review.
It:

- requires its own exact first push / attempt 1;
- checks out the exact run-379 head;
- pins the frozen DEC-544 source, dispatcher, annual workflow, installed 2017
  gate, and runtime blobs;
- requires annual history exactly
  `{1 failure, 376 failure, 377 success, 378 success, 379 success}`;
- requires no annual run 380+;
- requires the original DEC-544 reviewer to have zero runs;
- binds the exact DEC-543 receipt artifact and exact run-379 freeze artifact;
- invokes the existing DEC-544 review CLI unchanged;
- uploads only immutable recovered DEC-544 runtime evidence.

## Authority boundary

The recovery workflow has `contents: read` and `actions: read` only. It
contains no annual dispatch, rerun, retry, repository mutation, 2018 execution,
strategy promotion, Phase 8B, broker mutation, order placement, real-money
action, or trading authority.

The next gate remains
`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2018_EXECUTION_PREFLIGHT`.
