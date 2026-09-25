# Phase 8A — EXP-057 Clean-Main One-Way Operator

**Date:** 2026-09-25
**Status:** APPROVED SOURCE-ONLY / NOT DISPATCHED
**Decision:** DEC-226
**Experiment:** EXP-20260925-057

## Purpose

DEC-226 freezes a clean-main, one-way operator for the single DEC-225-authorized EXP-057 historical attempt.

The operator can inspect the live workflow state and derive at most one authoritative next action. It does not itself dispatch a model run merely by being merged.

## Frozen authorization binding

DEC-226 binds DEC-225 merge:

`6ab3bff41b072b2a322ed1d89a3df852c8bef812`

The operator gate metadata requires:

- DEC-223 execution-gate decision;
- DEC-225 execution-authorization decision;
- DEC-220/221/222/223/224 merged-commit identities;
- DEC-223 workflow/CLI/gate blobs;
- DEC-224 terminal-review blob;
- the guarded EXP-057 workflow/CLI blobs.

## Clean-main checkout preflight

Before planning, the operator requires:

- local branch exactly `main`;
- local HEAD is a valid 40-character Git SHA;
- fetched `origin/main` is a valid 40-character Git SHA;
- local HEAD equals fetched `origin/main` exactly;
- working tree is clean;
- origin remote resolves exactly to `Dtwosam/FMP`.

The checkout report binds `dec225_merged_commit`.

## Live run classification

The operator queries only the exact workflow:

`phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml`

for:

- branch `main`;
- event `workflow_dispatch`;
- up to 100 runs.

It permits at most one exact manual-main run.

The live state is classified as:

- `MISSING`;
- `IN_PROGRESS`;
- `TERMINAL`.

More than one exact manual-main run fails closed.

## One-way action rule

Only `MISSING` is dispatchable.

For `MISSING`, the frozen command is:

`gh workflow run phase8a-exp057-fit-temporal-residual-lower-tail-utility-model-training.yml --ref main -R Dtwosam/FMP`

The report exposes the four bounded DEC-225 historical-run fields as true and keeps replacement/promotion/shadow/demo/broker/live/real-money/trading false.

For `IN_PROGRESS`:

- no dispatch command is exposed;
- all historical-run authorization fields in the next report are false;
- the operator instructs inspection of the existing run only.

For `TERMINAL`:

- no dispatch command is exposed;
- replacement remains false;
- the run routes through the frozen DEC-224 terminal-review contract.

## Public CLI

Public CLI:

`scripts/phase8a_exp057_operator.py`

The CLI exposes:

- `next`: read-only live plan;
- `advance`: report whether the plan is dispatchable without executing;
- `advance --execute`: execute only after two identical consecutive `next` plans.

Before execution:

1. the first plan must be dispatchable;
2. the CLI invokes the public `next` planner a second time;
3. the second plan must equal the first exactly;
4. the frozen dispatch command must still match exactly.

Any state drift fails closed.

No rerun subcommand exists.

## Terminal evidence

When the sole run is terminal, the operator fetches:

- exact run metadata;
- exact jobs payload;
- exact artifacts payload.

For successful runs it selects the exact non-expired aggregate artifact, safely extracts one `model-result-evidence.json`, requires its `code_commit` to equal the reviewed head SHA, and routes all evidence through DEC-224.

## Authorization state

DEC-226 does not itself dispatch a model workflow or consume the DEC-225 slot.

It keeps false:

- replacement model run;
- promotion;
- shadow execution;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

No second-run path exists.

## Source identity

Operator source:

`src/fmp/market_learning/model_successor_fit_temporal_residual_lower_tail_utility_repair_operator.py`

Git blob:

`58d0002e4d74a75fec77d3074249e505857b8603`

Public CLI:

`scripts/phase8a_exp057_operator.py`

Git blob:

`2ba08d3f4411a84ff3708cc338d26f3d90bbaad4`

Focused tests:

`tests/test_phase8a_exp057_operator.py`

Git blob:

`3bad42c0a55df7fe32028636a5681837e185a253`

## Next gate

After DEC-226 is green and merged, the next safe gate is a repository-hosted read-only `next` plan runner.

That proof runner must be read-permission only and must not invoke `advance`, `advance --execute`, or any direct workflow-dispatch command.
