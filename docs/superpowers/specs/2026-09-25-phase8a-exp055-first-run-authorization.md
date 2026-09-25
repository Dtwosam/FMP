# Phase 8A — EXP-055 First-Run Authorization Gate

**Date:** 2026-09-25
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED
**Decision:** DEC-203
**Experiment:** EXP-20260925-055

## Zero-prior-run proof

Before DEC-203 source was opened, repository-wide GitHub Actions history was queried across the latest 100 runs.

The repository reported:

- manual-main workflow-dispatch runs in that set: `1`
- exact EXP-055 workflow matches: `0`

The exact workflow identity checked was:

- name: `phase8a-exp055-fit-temporal-residual-breadth-utility-model-training`
- path: `.github/workflows/phase8a-exp055-fit-temporal-residual-breadth-utility-model-training.yml`
- event: `workflow_dispatch`
- branch: `main`

No EXP-055 historical model-result attempt had consumed the first-run slot.

## Frozen predecessor bindings

DEC-203 binds:

- DEC-201 merge: `a5825ec8008cbb9bf9783b15135faed1d7f5fb73`
- DEC-201 workflow blob: `da5b498deb7c8d15993eaeb686127f138ce9f161`
- DEC-201 CLI blob: `41eeb09fe0730f5184e71a9f7413a3bc5f568e63`
- DEC-201 execution-gate blob: `e252f0550ca1c0bdc2ea16d32bc0b6a854b1c39c`
- DEC-202 merge: `2f5be5d1f7aea4f69f6979e90a0784408b349d3f`
- DEC-202 terminal-review blob: `341d228b2521441c7d4b32d92349bc001cc78a91`

The previously frozen DEC-198/199/200 protocol, training-core, and artifact-contract identities remain unchanged.

## First-run guard

DEC-203 hardens the manual-main EXP-055 workflow with a rejection guard before the execution authorization step.

At runtime the guard:

1. fetches the current workflow run by `GITHUB_RUN_ID`;
2. verifies the current run's exact name/path/event/main-branch identity;
3. fetches manual-main runs for the exact EXP-055 workflow;
4. excludes the current run id;
5. fails closed if any prior manual-main EXP-055 run exists.

The guarded workflow blob is:

`f38e792dde45a977b19d1790bdfe94543d99eb36`

No retry, rerun, or replacement semantics are introduced.

## Outer historical-result slot

DEC-203 opens only the outer historical-result slot in the exact execution gate.

After merge, the gate may report true for:

- model-run dispatch authorization;
- authoritative historical result execution;
- model-protocol result production;
- model fitting for that bounded historical attempt.

The underlying protocol, training-core, and artifact-contract authorization constants remain false. DEC-203 is the only outer source authorization.

The execution-gate source blob is:

`ed86be7f49e57b957dd256dc99cc4d5b7b301479`

## One-attempt semantics

DEC-203 does not itself dispatch the workflow.

The first manual-main EXP-055 workflow attempt, once separately submitted, consumes the slot regardless of terminal outcome:

- success;
- failure;
- cancellation;
- timeout.

Any terminal outcome must route through the predeclared DEC-202 terminal-review contract.

A second EXP-055 attempt, rerun, retry, or replacement is not authorized.

## Downstream locks

DEC-203 keeps false:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

No portfolio/shadow candidate is created by this authorization source.

## Focused tests

Focused workflow/authorization tests are:

`tests/test_phase8a_exp055_model_workflow.py`

Git blob:

`31a194fa69cdd21a695edd6a46d2a934d1917c85`

They verify exact source binding, the one-slot outer authorization, the first-run rejection guard, manual-main/input-free workflow shape, pinned numerical runtime, evidence preservation, and the continued absence of a direct dispatch path from the CLI.

## Next gate

After DEC-203 is green and merged, the next safe gate is a separate clean-main, double-plan, one-way operator. It may derive at most one dispatch action only while the exact EXP-055 workflow state is still `MISSING`.

DEC-203 itself does not dispatch a model run.
