# Phase 8A — EXP-058 First-Run Authorization Gate

**Date:** 2026-09-26
**Status:** APPROVED ONE-SLOT SOURCE AUTHORIZATION / NOT DISPATCHED
**Decision:** DEC-236
**Experiment:** EXP-20260925-058

## Zero-prior-run proof

Immediately before DEC-236 source was frozen, the latest 100 repository Actions runs were inspected.

Exact manual-main workflow-dispatch runs matching:

`phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training`

or:

`.github/workflows/phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml`

numbered exactly:

`0`

No EXP-058 historical model-result attempt had consumed the first-run slot.

## Frozen predecessor bindings

DEC-236 binds:

- DEC-234 merge: `365093ea81fdaf871680b42b02d67ebce3768d34`
- DEC-234 unguarded workflow blob: `78e9bf66ade5f6fb42ebe27e28b7ba24f36741b8`
- DEC-234 CLI blob: `e35a6ee0ff11bd3928b3bf05bf19f3572f64952c`
- DEC-234 execution-gate blob: `74881c0fee21392872ffd3df1378639bb04fea4a`
- DEC-235 merge: `a2e8614a87358763a838d8b02728f7c8216bc9d5`
- DEC-235 terminal-review blob: `76ba5de3ef92c02a8139213040dc3cf4d8efd75c`

It also retains the exact DEC-231/232/233 protocol/core/artifact provenance.

## First-run rejection guard

The exact manual-main EXP-058 workflow now contains a preflight rejection guard before result execution authorization.

Guarded workflow:

`.github/workflows/phase8a-exp058-fit-temporal-residual-regime-floor-utility-model-training.yml`

Git blob:

`9de995c0471e40539be679077db4ebc8fe33590c`

On any manual-main invocation, the guard:

- reads its own live Actions run identity;
- requires its exact workflow name/path, `workflow_dispatch`, and `main`;
- lists manual-main runs of the exact workflow;
- excludes only its own run id;
- fails closed if any other manual-main EXP-058 run exists.

The guard runs before `require-execution`.

## Outer historical-result authorization

Execution gate:

`src/fmp/market_learning/model_successor_fit_temporal_residual_regime_floor_utility_execution_gate.py`

Git blob:

`bd950a0091843c7630249a3ea7a6c1867f2b11ff`

DEC-236 opens exactly these outer fields:

- model-run dispatch authorization;
- authoritative historical model-result execution authorization;
- model-protocol result authorization;
- model-fit authorization.

The source gate stage is:

`FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RUN_DISPATCH_REQUIRED`

The underlying DEC-231 protocol, DEC-232 training core, and DEC-233 artifact-contract execution/fit constants remain false and are revalidated as false.

This is an outer workflow authorization only.

## One-attempt semantics

DEC-236 authorizes at most one guarded historical EXP-058 attempt after merge.

The first manual-main attempt consumes the slot on any terminal outcome and must route through DEC-235.

No rerun, retry, or replacement attempt is authorized.

DEC-236 itself does not dispatch the workflow.

## Downstream locks

DEC-236 keeps false:

- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Focused tests

Focused workflow/authorization tests:

`tests/test_phase8a_exp058_model_workflow.py`

Git blob:

`2706f53554145349fd6cb3fb7ba0784efc47fa20`

They pin the exact DEC-234/235 provenance, guarded workflow blob, authorization decision, four outer authorization fields, guard-before-authorization ordering, exact live workflow identity checks, unchanged matrix/runtime/evidence surface, execution-before-artifact-loading CLI ordering, and downstream locks.

## Next gate

After DEC-236 is green and merged, the next safe gate is a separate clean-main double-plan one-way operator.

That operator may only expose the frozen dispatch command while live state is exactly `MISSING`; it must never create rerun, retry, or replacement behavior.
