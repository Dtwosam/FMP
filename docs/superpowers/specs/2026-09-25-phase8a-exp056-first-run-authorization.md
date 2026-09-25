# Phase 8A — EXP-056 First-Run Authorization Gate

**Date:** 2026-09-25
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED
**Decision:** DEC-214
**Experiment:** EXP-20260925-056

## Zero-prior-run proof

Before DEC-214 source was opened, the latest 100 repository GitHub Actions runs were queried.

That set contained:

- manual-main workflow-dispatch runs: `1`
- exact EXP-056 workflow matches: `0`

The exact identity checked was:

- workflow name: `phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training`
- workflow path: `.github/workflows/phase8a-exp056-fit-temporal-residual-lower-tail-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`

No EXP-056 historical model-result attempt had consumed the first-run slot.

## Frozen predecessor bindings

DEC-214 binds:

- DEC-212 merge: `3da30377a5d358471e79a32466f93fd80cf3a02f`
- DEC-212 workflow blob: `83e5434c065167294b854b58308fec6d39d800db`
- DEC-212 CLI blob: `30e79ef7ef20d12d75fc97103b9411b7b467ecef`
- DEC-212 execution-gate blob: `a81f746c8b19abc63f1bb83da0c32f1023644b94`
- DEC-213 merge: `af6083303e1fac29265c7ffc59eb355a313d892d`
- DEC-213 terminal-review blob: `0bfc50d39d04d82e95c731b7284c7be143191efd`

The DEC-209/210/211 protocol, training-core, and artifact-contract identities remain frozen and their internal result-execution/model-fit authorization constants remain false.

## First-run guard

DEC-214 hardens the exact EXP-056 manual-main workflow with a first-run rejection guard before the execution authorization step.

At runtime the guard:

1. fetches the current run by `GITHUB_RUN_ID`;
2. verifies exact run id, workflow name/path, `workflow_dispatch` event, and `main` branch;
3. lists manual-main runs for the exact EXP-056 workflow;
4. excludes the current run id;
5. fails closed if any prior exact manual-main EXP-056 run exists.

Guarded workflow blob:

`cf9585ebdfea689c7b0e3ca82ac4c43488559b2a`

No retry, rerun, or replacement semantics are introduced.

## Bounded outer historical-result slot

DEC-214 opens only the outer exact-source gate for at most one historical attempt.

After merge, the gate may expose true for:

- model-run dispatch authorization;
- authoritative historical result execution;
- model-protocol result production;
- model fitting for that bounded attempt.

The underlying protocol, training-core, and artifact-contract execution constants remain false. DEC-214 is the sole outer source authorization.

Execution-gate blob:

`ad3c5f8cc176952c8c8a2fcf2a626c30a5be307c`

## One-attempt semantics

DEC-214 does not dispatch the workflow.

A later separately frozen operator/executor may submit at most the first exact manual-main EXP-056 workflow attempt.

That first attempt consumes the slot regardless of terminal outcome:

- success;
- failure;
- cancellation;
- timeout.

Every terminal outcome must route through DEC-213.

No second attempt, retry, rerun, or replacement is authorized.

## Downstream locks

DEC-214 keeps false:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Focused tests

Focused tests:

`tests/test_phase8a_exp056_model_workflow.py`

Git blob:

`1c47614e30be29f5f1d14d0ce58dae7aa69c4674`

They verify exact DEC-212/213 bindings, guarded workflow identity, current-run exclusion, one-slot outer authorization, exact source blobs, pinned runtime/matrix, execution-before-artifact-loading order, and continued downstream locks.

## Next gate

After DEC-214 is green and merged, the next safe gate is a separate clean-main, double-plan, one-way EXP-056 operator.

DEC-214 itself does not dispatch a model run.
