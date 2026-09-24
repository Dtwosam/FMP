# Phase 8A — EXP-047 Operator Gate-Metadata Repair

**Date:** 2026-09-24
**Status:** SOURCE-ONLY REPAIR; EXP-047 RUN SLOT UNCONSUMED
**Decision:** DEC-120
**Experiment:** EXP-20260924-047

## 1. Purpose

DEC-120 repairs a fail-closed integration defect in the merged DEC-119 local operator before any EXP-047 historical model run occurred.

The public `next` path attempted to read a nonexistent `dec107_merged_commit` field from the DEC-118 execution gate and raised `KeyError` before producing an operator plan.

Live GitHub still reported zero manual-main `phase8a-exp047-density-model-training` runs when this repair began. Therefore the DEC-118 one-run slot remained unconsumed.

## 2. Root cause

DEC-119 was ported from an older one-way operator lineage. The CLI metadata projection retained one stale predecessor field name:

`dec107_merged_commit`

The DEC-118 gate correctly exposes the EXP-047 predecessor chain instead:

- `dec113_merged_commit`
- `dec114_merged_commit`
- `dec115_merged_commit`
- `dec116_merged_commit`
- `dec117_merged_commit`

The workflow, execution authorization, model protocol, training core, evidence contract, and terminal-review logic were not implicated.

## 3. Repair

DEC-120 moves gate-metadata projection into the operator core through:

`density_operator_gate_metadata(...)`

The helper requires:

- execution-gate decision exactly `DEC-116`;
- execution-authorization decision exactly `DEC-118`;
- valid 40-character Git identities for the DEC-113 through DEC-117 merge chain;
- exact DEC-116 workflow/CLI/gate source identities;
- exact DEC-117 review identity;
- exact authorized workflow and model CLI source identities.

Missing, malformed, or drifted metadata fails closed with `ValueError`.

The public CLI now merges only the validated metadata projection into the `next` report.

## 4. Regression coverage

Focused tests now require:

- DEC-118-shaped metadata to validate;
- missing `dec117_merged_commit` to fail closed;
- public CLI source to contain no `dec107_merged_commit`;
- public CLI to invoke `density_operator_gate_metadata(gate)`.

The existing DEC-119 one-way state-machine, dispatch-command, double-plan, no-rerun, and terminal-review tests remain unchanged.

## 5. Repaired source identities

Operator core:

`src/fmp/market_learning/model_successor_density_operator.py`

Git blob:

`00d4bbb4e239bc6ceba903a869a676bce816dacf`

Executable wrapper:

`scripts/phase8a_exp047_operator.py`

Git blob:

`0ad604619ef6f7067c494146960a092818a7b163`

Focused tests:

`tests/test_phase8a_exp047_operator.py`

Git blob:

`6192b7213ed5a786e5301f8859e547a504098495`

## 6. Authorization boundary

DEC-120 changes no EXP-047 workflow or execution authorization.

It does not dispatch the workflow.

The first later manual-main attempt still consumes the DEC-118 slot on any terminal outcome.

The following remain false:

- replacement-run authorization;
- promotion;
- prospective shadow;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization;
- trading authorization.

## 7. Next gate

After DEC-120 merges and local `main` is updated, rerun:

`python scripts/phase8a_exp047_operator.py next`

Only if the repaired operator returns:

`DENSITY_MODEL_RUN_DISPATCH_REQUIRED`

may the separately explicit:

`python scripts/phase8a_exp047_operator.py advance --execute`

be considered.
