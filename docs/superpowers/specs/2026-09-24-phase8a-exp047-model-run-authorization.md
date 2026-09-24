# Phase 8A — EXP-047 Single Historical Model-Run Authorization

**Date:** 2026-09-24
**Status:** AUTHORIZED SOURCE; NO EXP-047 RUN DISPATCHED BY THIS DECISION
**Decision:** DEC-118
**Experiment:** EXP-20260924-047

## 1. Preconditions

Before DEC-118 source work, GitHub reported zero manual-main runs for:

`phase8a-exp047-density-model-training`

DEC-117 terminal review was already merged.

DEC-118 therefore considers only the first guarded historical EXP-047 result-producing attempt.

## 2. Frozen predecessor bindings

DEC-118 binds:

- DEC-113 protocol merge/source;
- DEC-114 density-core merge/source;
- DEC-115 artifact/evidence merge/source;
- DEC-116 locked workflow source merge: `b133424949c906d2683692e9d2ad746a33397ffc`
- DEC-116 pre-authorization workflow blob: `7ae75dbca58266736be6a6cdf66bf58b61ec3b63`
- DEC-116 CLI blob: `28941013c2cf9942a94667d58ec6b76de9d13cd2`
- DEC-116 pre-authorization gate blob: `8a581384a32c10246d123902c0cb30711456c268`
- DEC-117 review merge: `691448db95a0ab43e2ceb319b1f215c88a856613`
- DEC-117 review blob: `466e163edc42145b7cf2d698c48c713e0e804a95`

## 3. First-run rejection guard

DEC-118 hardens the workflow before model installation or fitting.

The authorization-preflight now:

1. fetches the exact current workflow run by `GITHUB_RUN_ID`;
2. verifies exact workflow name/path, event `workflow_dispatch`, and branch `main`;
3. lists manual-main runs for the exact EXP-047 workflow;
4. excludes only the current `GITHUB_RUN_ID`;
5. fails if any other prior manual-main EXP-047 run exists.

The hardened workflow Git blob is:

`34926f0863086e15fe8646b0d93dc3eebd1b2cc6`

## 4. Single-attempt semantics

The first manual-main EXP-047 workflow attempt consumes the DEC-118 run slot regardless of whether it:

- succeeds;
- fails;
- is cancelled;
- times out.

No automatic rerun or replacement is authorized.

A GitHub "rerun failed jobs" / "rerun all jobs" action is not authorized by DEC-118.

## 5. Outer authorization layer

The authorized execution-gate source is:

`src/fmp/market_learning/model_successor_density_execution_gate.py`

Git blob:

`e20ee40678448df00af6885c7419506d476bcb75`

It records:

`DENSITY_MODEL_EXECUTION_AUTHORIZATION_DECISION = "DEC-118"`

and opens only the outer historical result-producing flags:

- `DENSITY_MODEL_RUN_DISPATCH_AUTHORIZED = true`
- `AUTHORITATIVE_DENSITY_MODEL_RESULT_EXECUTION_AUTHORIZED = true`
- `DENSITY_MODEL_PROTOCOL_RESULT_AUTHORIZED = true`
- `DENSITY_MODEL_FIT_AUTHORIZED = true`

The underlying DEC-113 protocol, DEC-114 core, and DEC-115 artifact-runner source-level authorization constants remain false and are explicitly checked as frozen dependencies.

## 6. What remains unchanged

DEC-118 does not change:

- HGB-only model-family boundary;
- logistic exclusion;
- 250/500/1000 candidate-density anchors;
- HGB model configuration;
- feature columns;
- target;
- data chronology;
- 250-candidate aggregate floor;
- aggregate financial gate;
- four-window stability screen;
- historical feature/outcome/readiness artifacts;
- pinned runtime;
- artifact/evidence validation;
- terminal-review semantics.

## 7. Mandatory terminal review

Any terminal EXP-047 run must be reviewed through DEC-117.

Success requires the exact complete 11-job/10-artifact shape and DEC-115 aggregate evidence revalidation.

Failure/cancellation/timeout may preserve valid partial cell evidence but cannot claim aggregate result evidence.

DEC-118 does not authorize a replacement after any terminal outcome.

## 8. No dispatch by this decision

DEC-118 changes source authorization only.

It does **not** invoke:

`gh workflow run phase8a-exp047-density-model-training.yml --ref main -R Dtwosam/FMP`

A separate operator/execution step is required after DEC-118 merges.

## 9. Downstream authorization state

DEC-118 keeps false:

- replacement model-run authorization;
- promotion;
- prospective shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading authorization.

No accepted candidate exists merely because one historical result run is authorized.

## 10. Next gate

The next safe source step is a one-way, clean-main operator that can expose exactly one dispatch only while no EXP-047 run exists and routes terminal evidence through DEC-117.

DEC-118 itself dispatches nothing.
