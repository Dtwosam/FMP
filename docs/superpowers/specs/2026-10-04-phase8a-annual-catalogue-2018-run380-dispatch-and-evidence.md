# Phase 8A — 2018 Run-380 Dispatch and Evidence Binding

**Date:** 2026-10-04  
**Status:** ATOMIC DISPATCH + READ-ONLY REVIEW  
**Decisions:** DEC-554 / DEC-555

## Concrete source

DEC-553 completed successfully as workflow run `37235949110` on
`67b8baa1f6a5770c2add27189f86f65f46a263d6`.

Its immutable artifact is:

- artifact ID: `11315522989`
- digest: `sha256:e4d9b6c8661442c1a1debebac843f2dabf07bca6e36054dc7d2ed43a74f1375e`
- preflight fingerprint:
  `ba609f06481c1b08e10d16dc772290cd0f3988de9ba32eaa56c13b5561ab86c2`

DEC-553 freezes only:

- ref `main`;
- annual segment `2018`;
- predecessor annual freeze run ID `37227536041`;
- expected annual workflow run `380` / attempt `1`.

## DEC-554 exact dispatcher

The dispatcher is a path-scoped one-shot main-push workflow with
`contents: read` and `actions: write`.

Before dispatch it requires:

- exact first dispatcher run / attempt 1;
- exact DEC-553 run, artifact, digest, and fingerprint;
- exact installed 2018 gate/runtime blobs;
- exact annual history
  `{1 failure, 376 failure, 377 success, 378 success, 379 success}`;
- no annual run `380+`;
- current main equal to the atomic DEC-554/555 landing;
- the landing diff contain exactly the dispatcher, reviewer, tests, CI hooks, and
  these documentation updates.

It may submit exactly:

`annual_segment_label=2018`

with:

`previous_annual_freeze_run_id=37227536041`

and then resolve exactly run `380` / attempt `1` on the same main head.

The DEC-554 receipt claims submission only. It grants no rerun, retry,
replacement, run 381+, 2019+, strategy promotion, broker mutation, order
placement, real-money action, or trading authority.

## DEC-555 evidence reviewer

The reviewer is installed atomically before DEC-554 can dispatch. It has only
`contents: read` and `actions: read`.

For successful run 380 it requires:

- exact DEC-554 dispatch receipt;
- exact successful annual run 380 / attempt 1;
- exact 20-job / 20-artifact 2018 inventory;
- digest-verified annual freeze ZIP;
- a valid DEC-477 annual freeze for segment 2018 on the run-380 head.

It emits one immutable concrete 2018 runtime binding and keeps all 2019+,
cross-year synthesis, Strategy V1, promotion, Phase 8B, broker/order,
real-money, and trading authority false.

A manual reviewer input path exists only to recover a missed GitHub
`workflow_run` successor event. It never reruns or redispatches annual research.

## Next gate

After concrete DEC-555 evidence:

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2019_EXECUTION_PREFLIGHT`
