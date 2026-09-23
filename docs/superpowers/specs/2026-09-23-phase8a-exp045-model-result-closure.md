# Phase 8A — EXP-045 Successful Historical Result Review and Closure

**Date:** 2026-09-23
**Status:** REVIEWED — SUCCESSFUL WORKFLOW, NO VALIDATED MODEL CANDIDATE
**Decision:** DEC-102
**Experiment:** EXP-20260923-045
**Run:** 35911916239

## 1. Purpose

DEC-099 authorized at most one guarded historical EXP-045 model-result run.

DEC-100 predeclared its terminal-review contract before any EXP-045 result existed.

DEC-101 froze the single-step operator that submitted the one authorized run only after a clean-main and zero-prior-run check.

DEC-102 records the exact terminal result, validates it against DEC-100, and closes EXP-045 without a replacement run, promotion, prospective shadow admission, demo orders, broker mutation, live orders, real-money trading, or trading authorization.

## 2. Exact reviewed run

The only EXP-045 historical model run is:

- GitHub Actions run ID: `35911916239`;
- workflow: `phase8a-exp045-model-training`;
- event: `workflow_dispatch`;
- branch: `main`;
- head SHA: `6d42a5053c5f2f696071715640dab24973a40517`;
- run attempt: `1`;
- terminal status: `completed`;
- conclusion: `success`.

The one-run authorization is consumed. No rerun or replacement run is authorized.

## 3. Exact successful job inventory

All 11 jobs completed successfully:

- authorization preflight: `107353620434`;
- EURUSD 5m: `107353779188`;
- EURUSD 15m: `107353779209`;
- EURUSD 1h: `107353779245`;
- GBPUSD 5m: `107353779183`;
- GBPUSD 15m: `107353779152`;
- GBPUSD 1h: `107353779161`;
- USDJPY 5m: `107353779255`;
- USDJPY 15m: `107353779328`;
- USDJPY 1h: `107353779202`;
- aggregate evidence: `107365635911`.

The authorization preflight independently passed the exact merged-main, first-run, frozen-source, pinned-runtime, and DEC-099 execution checks before model fitting began.

## 4. Persisted evidence

All nine pair/timeframe result artifacts and the one aggregate artifact were persisted.

The exact aggregate artifact is:

`exp045-model-result-evidence-6d42a5053c5f2f696071715640dab24973a40517-from-feature-35867307338-outcome-35876715434`

Artifact ID:

`10774927034`

Artifact ZIP digest:

`sha256:8602d0b5e9bb6ad746f5cd5c96e878e631d6ed090dcd7a236c0ee00c6fadd5a5`

Aggregate evidence fingerprint:

`3e0ebac02dbba690b4c03dd10c3fdd30c5eb0d6356b881e38f9a3527f0135c55`

The aggregate fingerprint was independently recomputed from canonical JSON and matched exactly.

The DEC-102 result-record implementation is frozen at Git blob:

`f0f84ad7e32b8d44a652dbeaed841c87661af4da`

## 5. Aggregate result

The aggregate contains exactly 18 model cells.

The frozen counts are:

- selected cells: `1`;
- no-model-challenger cells: `17`;
- no-model-family-available cells: `0`;
- validation-pass cells: `0`;
- retrospective-holdout-pass cells: `0`;
- logistic non-convergence cells: `6`.

Histogram gradient boosting fitted in all 18 cells.

The six predeclared logistic non-convergence cells are:

- EURUSD 5m / 60m;
- EURUSD 5m / 240m;
- EURUSD 15m / 240m;
- GBPUSD 5m / 60m;
- USDJPY 5m / 60m;
- USDJPY 5m / 240m.

These family-level failures are handled exactly as predeclared by DEC-095/096 and do not trigger a retry, rescue fit, hyperparameter change, or replacement experiment.

## 6. Only selected challenger

The only cell that passed the selection gate was:

- symbol: GBPUSD;
- timeframe: 5m;
- horizon: 240m;
- model family: `hist_gradient_boosting`;
- confidence threshold: `0.6`;
- result fingerprint:
  `d6c2ce934be43e1e76852bb7d6c6ca46d33160bff372719bf083cb7923b352ff`.

At the frozen 0.5-pip selection scenario it produced:

- directional candidate count: `460`;
- total net pips: approximately `+2353.7`;
- selection gate: PASS.

This selection result alone is not acceptance.

## 7. Validation rejection

The exact selected challenger failed the separately frozen validation gate.

At the frozen 0.5-pip validation scenario it produced:

- directional candidate count: `83`;
- total net pips: approximately `-1397.5`;
- validation gate: FAIL.

The validation status is therefore:

`REJECT`

The retrospective holdout remained:

`LOCKED_VALIDATION_REJECT`

No holdout result was opened for the rejected challenger.

## 8. Interpretation boundary

The historical workflow succeeded operationally, but EXP-045 produced no validated model candidate.

The evidence remains:

- post-result-informed;
- retrospective;
- `untouched_oos=false`;
- not prospective evidence.

The positive selection result must not be separated from the validation rejection or described as a qualified trading model.

## 9. Closure

DEC-102 closes EXP-045 with:

- replacement model run authorization: false;
- promotion authorization: false;
- shadow admission: false;
- demo-order authorization: false;
- broker mutation: false;
- live-order authorization: false;
- real-money authorization: false;
- trading authorization: false.

No parameter rescue, threshold adjustment, model-family substitution, feature change, refit, or retry is authorized under EXP-045.

Any further learned-model research must begin under a separately predeclared successor experiment/protocol that explicitly acknowledges the EXP-045 result as prior information.

## 10. Phase 8B boundary

DEC-102 does not unlock Phase 8B.

No EXP-045 model is eligible for prospective shadow admission.

Existing Phase 8B source/safety preparation remains preserved, but prospective shadow activity remains locked until a separately accepted Phase 8A candidate exists under its own acceptance decision.
