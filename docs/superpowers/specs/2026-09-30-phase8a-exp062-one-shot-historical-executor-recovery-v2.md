# Phase 8A — EXP-062 One-Shot Historical Executor Recovery V2

**Date:** 2026-09-30  
**Status:** EXPLICIT SECOND FAIL-CLOSED RECOVERY AUTHORIZATION / HISTORICAL RESULT NOT STARTED  
**Decision:** DEC-439  
**Experiment:** EXP-20260927-062  
**Predecessors:** DEC-436, DEC-437, DEC-438

## Failure provenance

DEC-436 recovery run `36707978889` / job `109862691026` ran as exact recovery
run #1 / attempt 1 on head `ed757a631dfe9ec7065cf95db04b446034da45e4`.

It passed:

- exact recovery-run guard;
- failed original-executor provenance check;
- frozen source-identity check.

It then failed at `Require exact DEC-436 recovery authorization` because importing
`fmp.discovery` required `polars`, while the recovery runner had not installed
the pinned planning runtime.

The historical-slot check, historical dispatch, target resolution, receipt write,
and receipt upload were all skipped. Discovery run #2 remains unused.

## DEC-439 recovery

DEC-439 creates a separate manual-only recovery-v2 workflow with its own fresh
run counter.

A valid run must be recovery-v2 run #1 / attempt 1 on current `main`. Before any
historical dispatch it must:

- pin failed original executor run `36702494195`;
- pin failed DEC-436 recovery run `36707978889` / job `109862691026`;
- pin DEC-436 authorization/workflow, original executor, discovery workflow, and
  `requirements/exp061-discovery-run.txt`;
- install the pinned planning runtime from that requirements file;
- re-evaluate exact DEC-439 authorization;
- prove discovery run #2 is still absent.

Only then may it submit exactly
`gh workflow run phase8a-exp062-discovery.yml --ref main` and resolve discovery
run #2 / attempt 1 on the exact same head SHA.

## Authority boundary

DEC-439 authorizes only the single recovery-v2 dispatch path. Generic rerun, retry,
and replacement remain false. General execute mode, reserved 2023-2026 access,
candidate compilation/promotion, Phase 8B, demo, broker/live, real-money, and
trading remain false.

## Next gate

After green CI and merge, manually submit exactly
`phase8a-exp062-one-shot-historical-executor-recovery-v2.yml` once on `main`.
