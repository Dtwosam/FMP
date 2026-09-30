# Phase 8A — EXP-062 Runtime-Dependency Recovery

**Date:** 2026-09-30  
**Status:** EXPLICIT FAIL-CLOSED RECOVERY OF DEC-436 / HISTORICAL RESULT NOT STARTED  
**Decision:** DEC-439  
**Experiment:** EXP-20260927-062

## Failure provenance

Two executor paths have failed safely before historical dispatch.

### Original executor

- run: `36702494195`;
- job: `109844958600`;
- head: `59b55d519449e20cf396d70ed9a5722b989d933a`;
- run number / attempt: `2 / 1`;
- conclusion: `failure`;
- historical dispatch: skipped;
- receipt artifact: none.

### DEC-436 recovery

- run: `36707978889`;
- job: `109862691026`;
- head: `ed757a631dfe9ec7065cf95db04b446034da45e4`;
- run number / attempt: `1 / 1`;
- conclusion: `failure`;
- failed step: `Require exact DEC-436 recovery authorization`;
- error: `ModuleNotFoundError: No module named 'polars'`;
- historical slot check: skipped;
- historical dispatch: skipped;
- receipt artifact: none.

The DEC-436 exact-run guard and failed-original provenance checks both succeeded.
The defect was solely that the workflow imported `fmp.discovery` before installing
its pinned planning runtime.

## Recovery design

DEC-439 introduces a new manual-only recovery workflow with its own independent run
counter. The failed original executor and failed DEC-436 recovery are not rerun.

A valid DEC-439 recovery requires exactly workflow run #1 / attempt 1 on current
`main`. It must:

- preserve both failed-run provenances;
- pin the DEC-436 authorization/workflow, original executor workflow, discovery
  workflow, and planning-runtime requirement file;
- install exactly `requirements/exp061-discovery-run.txt`, currently pinning
  `polars==1.44.2` and `polars-runtime-32==1.44.2`;
- evaluate the DEC-439 authorization only after that install;
- prove discovery run #2 is still absent;
- dispatch only `phase8a-exp062-discovery.yml --ref main`;
- resolve exactly discovery run #2 / attempt 1 on the same head SHA;
- write one immutable DEC-439 recovery receipt.

## Authority boundary

DEC-439 authorizes only the separate runtime-dependency recovery workflow run #1 /
attempt 1. It does not authorize rerunning either failed workflow.

`rerun_authorized`, `retry_authorized`, and `replacement_run_authorized`
remain false. General execute mode, reserved 2023-2026 data, candidate
compilation/promotion, Phase 8B, demo orders, broker mutation, live orders, real
money, and trading remain false.

DEC-437/438 remain source-only definitions for the unsuccessful DEC-436 path and do
not constitute successful runtime evidence.

## Next gate

After CI and merge, manually invoke exactly
`phase8a-exp062-one-shot-historical-executor-recovery-runtime-dependency.yml`
once on `main`.
