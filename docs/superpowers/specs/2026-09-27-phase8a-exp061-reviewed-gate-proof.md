# Phase 8A — EXP-061 Reviewed Gate-Proof Freeze

**Date:** 2026-09-27  
**Status:** REVIEWED / EXPECTED FAIL-CLOSED PROOF / HISTORICAL RUN STILL LOCKED  
**Decision:** DEC-280  
**Experiment:** EXP-20260927-061  
**Predecessors:** DEC-277, DEC-278, DEC-279

## Purpose

DEC-280 freezes the exact terminal evidence from the single DEC-279-authorized EXP-061 proof-only dispatch.

The proof is not a historical discovery result. Its only purpose was to prove that the installed workflow stops at the DEC-275 execution gate before any historical discovery cell or aggregate result can execute.

## One-shot executor evidence

The DEC-279 executor is frozen as:

- run id: `36319870713`;
- workflow: `phase8a-exp061-proof-one-shot-execute`;
- event: `push`;
- branch: `main`;
- head SHA: `041b7b2f5aac8821156fab346df8ab30f4be2a7b`;
- run attempt: `1`;
- conclusion: `success`;
- dispatch-evidence artifact id: `10931792980`;
- artifact digest: `sha256:a7a0ea04de1b5f67a7eaa64419b6be15ddddee049a0fc53021920eb2308f540f`.

Its immutable executor evidence records two identical fresh DEC-278 plans, zero prior matching manual-main EXP-061 runs, exactly the frozen proof command, and one submitted proof dispatch. Historical-result dispatch/execution, discovery-result production, rerun/retry/replacement, reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remained false.

## Proof run identity

The sole proof run is:

- run id: `36319888985`;
- workflow: `phase8a-exp061-discovery`;
- path: `.github/workflows/phase8a-exp061-discovery.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head SHA: `041b7b2f5aac8821156fab346df8ab30f4be2a7b`;
- run attempt: `1`;
- terminal conclusion: `failure`.

The failure is the expected proof outcome.

## Terminal job evidence

GitHub materialized exactly three jobs:

1. `exp061-preflight`, job `108621570094`: **failure**;
2. `exp061-cell-${{ matrix.dataset.symbol }}-${{ matrix.dataset.timeframe }}-${{ matrix.dataset.horizon }}m`, job `108621636801`: **skipped**;
3. `exp061-aggregate`, job `108621637326`: **skipped**.

The preflight failed only at `Require separately authorized EXP-061 execution` after checkout, runtime setup, exact accepted EXP-044 source retrieval, and source validation succeeded.

No discovery cell executed and no aggregate result executed.

## DEC-277 reviewer compatibility note

DEC-277 correctly predeclared that every materialized downstream job must be skipped and allowed GitHub to elide skipped matrix children.

The completed run exposed one GitHub API shape DEC-277 did not enumerate: because the matrix dependency never expanded after the failed preflight, GitHub materialized a single skipped matrix placeholder using the literal job-name expression rather than one of the 18 concrete DEC-274 cell names.

DEC-280 does not rewrite DEC-277 after seeing the result and does not rerun the proof. It freezes the exact immutable run/job identities above and requires the placeholder itself to remain skipped. Any executed downstream job would invalidate DEC-280.

This is a terminal-review compatibility issue only. It does not weaken the execution boundary.

## Preflight artifact

Exactly one proof artifact exists:

- artifact id: `10932485842`;
- name: `phase8a-exp061-preflight-041b7b2f5aac8821156fab346df8ab30f4be2a7b`;
- digest: `sha256:0dfbf4c76874bb2b056a835ff0d7fdf2199ddda279e40a60924128a7ff29573d`;
- expired: `false`.

There are zero cell-result artifacts and zero aggregate-result artifacts.

The preflight JSON binds:

- DEC-275 source/version;
- exact proof head;
- accepted EXP-044 feature run `35867307338`;
- accepted EXP-044 outcome run `35876715434`;
- exact feature/outcome aggregate evidence artifacts;
- nine verified pair/timeframe source pairs;
- `source_ready=true`;
- exact deterministic DEC-275 workflow-source payload;
- source fingerprint `800b5779e6fab2b48862e4ea56b027c95cb7ff83d97b47f6c1a0227d896f6855`;
- every historical/result/trading authorization false.

## Frozen conclusion

DEC-280 records:

- proof outcome: `EXPECTED_FAIL_CLOSED_EXECUTION_GATE`;
- fail-closed semantics verified: **true**;
- historical-result slot consumed: **false**;
- historical discovery execution occurred: **false**;
- cell-result artifacts: **0**;
- aggregate-result artifacts: **0**;
- proof rerun/retry/replacement: **false**;
- historical-result dispatch: **false**;
- historical discovery execution: **false**;
- discovery result production: **false**;
- reserved 2023-2026 access: **false**;
- candidate compilation: **false**;
- Phase 8B: **false**;
- demo orders: **false**;
- broker mutation: **false**;
- live orders: **false**;
- real-money action: **false**;
- trading: **false**.

The proof slot is finished. It does not consume or open the historical-result slot.

## Frozen implementation

- reviewed-proof source: `src/fmp/discovery/proof_result_decision.py`;
- focused tests: `tests/test_phase8a_exp061_reviewed_gate_proof.py`.

The source binds the exact immutable executor/proof/job/artifact identities above and revalidates the DEC-275 preflight source fingerprint and deterministic workflow-source payload.

## Next gate

After DEC-280 merges green, the next safe gate is a separate source-only historical-run authorization contract for EXP-061.

That later decision may define the conditions for at most one bounded 2015-2022 discovery-result attempt, but DEC-280 itself authorizes no historical dispatch or execution. Reserved 2023-2026 data, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remain locked.
