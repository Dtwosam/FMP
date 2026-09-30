# Phase 8A — EXP-062 One-Shot Historical Executor Recovery

**Date:** 2026-09-30  
**Status:** EXPLICIT FAIL-CLOSED RECOVERY AUTHORIZATION / HISTORICAL RESULT NOT STARTED  
**Decision:** DEC-436  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-435

## Failure provenance

The explicitly submitted original executor run failed before historical dispatch:

- workflow: `phase8a-exp062-one-shot-historical-executor`;
- run: `36702494195`;
- job: `109844958600`;
- head: `59b55d519449e20cf396d70ed9a5722b989d933a`;
- GitHub run number: `2`;
- run attempt: `1`;
- conclusion: `failure`;
- failed step: `Require exact one-shot executor run`;
- historical dispatch step: skipped;
- executor receipt: not created;
- artifacts: none.

The guard failed because the original workflow was authorized for run #1 / attempt 1
but GitHub assigned run #2 / attempt 1. No visible original workflow run #1 is
available in current Actions history, so DEC-436 does not guess or rewrite that
missing provenance.

## Recovery design

DEC-436 preserves the original executor workflow byte-for-byte and introduces a
separate manual-only recovery workflow with its own run counter.

A valid recovery requires exactly recovery workflow run #1 / attempt 1 on current
`main`. Before any dispatch it must:

- pin the failed original executor run/job/head and verify its failure shape;
- prove the failed run never reached the historical dispatch step;
- prove the failed run produced no receipt artifact;
- pin the exact DEC-435 source, original executor workflow, and discovery workflow;
- re-evaluate the DEC-436 recovery authorization;
- verify discovery run #2 does not already exist.

Only then may it submit exactly
`gh workflow run phase8a-exp062-discovery.yml --ref main` and resolve discovery
run #2 / attempt 1.

## Authority boundary

DEC-436 adds only
`explicit_one_shot_executor_recovery_dispatch_authorized=true`.

It does not authorize a rerun of the failed executor, a retry attempt, or generic
replacement execution. `rerun_authorized`, `retry_authorized`, and
`replacement_run_authorized` remain false.

General execute mode, reserved 2023-2026 data, candidate compilation/promotion,
Phase 8B, demo orders, broker mutation, live orders, real money, and trading remain
false.

## Next gate

After this PR is green and merged, the next gate is one manual invocation of
`phase8a-exp062-one-shot-historical-executor-recovery.yml` on `main`.

Do not rerun run `36702494195` and do not trigger the original executor workflow
again.
