# Phase 8A — EXP-044 Predeclared Model-Training Protocol

**Date:** 2026-09-23
**Status:** APPROVED — PREDECLARED SOURCE PROTOCOL; RESULT RUN STILL LOCKED
**Decision:** DEC-088
**Experiment:** EXP-20260923-044

## 1. Purpose

DEC-074 readiness has been satisfied by the persisted EXP-044 feature/outcome evidence chain. This opens source work for a separately frozen model-training protocol.

This decision freezes that protocol before any EXP-044 model-training result exists.

It does not authorize a result-producing fit.

## 2. Evidence boundary

The authoritative preparation chain is:

- feature workflow run `35867307338`;
- aggregate feature evidence fingerprint `1288f0fa0ca62069d651f86c21ff9d799e46f24c2eac2b555f177ee2dcfa0815`;
- outcome workflow run `35876715434`;
- aggregate outcome-evidence artifact `10758027876`;
- DEC-074 readiness artifact `10757578276`.

All EXP-044 historical evidence remains `RETROSPECTIVE_ALREADY_SEEN`.

No split in this protocol may be described as untouched out-of-sample evidence.

A later result-producing workflow must revalidate and bind the exact persisted readiness/evidence chain before any fit.

## 3. Model universe

Models are independent by:

- symbol: exactly `EURUSD`, `GBPUSD`, `USDJPY`;
- timeframe: exactly `5m`, `15m`, `1h`;
- forward horizon: exactly `60` and `240` minutes.

This creates exactly 18 model cells.

There is no pooled cross-pair, cross-timeframe, or cross-horizon model in V1.

## 4. Inputs

Each model uses exactly the 48 values in the frozen Phase 5 feature definition exposed as `FEATURE_VALUE_COLUMNS`.

Identity columns are not model inputs.

Outcome values, future prices, future labels, realized future PnL, model-selection statistics, and later-period statistics are never model inputs.

No target-aware feature selection is permitted.

## 5. Target

The only V1 training target is:

`best_direction_0p5`

from the cell's matching horizon row in `fmp-market-outcome-grid-v1`.

The target classes are exactly:

- `LONG`;
- `SHORT`;
- `NO_TRADE`.

The target therefore represents the best strictly positive direction after historical BID/ASK spread and exactly 0.5 pip adverse slippage per fill.

Rows without an exact outcome at the frozen horizon are excluded with explicit accounting. They are never shifted, interpolated, repaired, or assigned a synthetic target.

Each fit cell must contain all three target classes. Missing class support fails closed.

## 6. Chronological splits

The splits are frozen as:

- fit: `2015-01-01` through `2020-12-31` inclusive;
- selection: `2021-01-01` through `2022-12-31` inclusive;
- validation: `2023-01-01` through `2024-12-31` inclusive;
- retrospective holdout: `2025-01-01` through `2026-08-20` inclusive.

For a row to belong to a split:

- `available_at_utc` must be at or after the split start;
- `available_at_utc` must be before the split end-exclusive;
- `exit_timestamp_utc` must also be before the split end-exclusive.

The last rule automatically purges boundary observations whose 60m/240m target crosses into the next split.

There is no refit after the fit split.

Selection, validation, and retrospective-holdout rows may never alter preprocessing, estimator parameters, fitted weights, or confidence thresholds.

## 7. Preprocessing

Preprocessing is fit on the fit split only.

For both model families:

- non-finite/null feature values use fit-period median imputation;
- an entirely null/non-finite fit column fails closed;
- no forward fill or future-derived imputation is permitted.

For logistic regression only:

- fit-period median-imputed inputs are standardized using fit-period mean and scale.

Histogram gradient boosting uses the median-imputed values without standard scaling.

No class weighting, oversampling, undersampling, synthetic examples, or probability calibration is authorized in V1.

## 8. Model families

Dependency identity remains exactly `scikit-learn==1.9.1`.

The only model families are:

### L2 logistic regression

- penalty: `l2`;
- `C=1.0`;
- solver: `lbfgs`;
- tolerance: `1e-8`;
- intercept: enabled;
- class weight: none;
- max iterations: `2000`;
- warm start: false.

### Histogram gradient boosting

- loss: `log_loss`;
- learning rate: `0.05`;
- max iterations: `100`;
- max leaf nodes: `15`;
- max depth: `3`;
- minimum samples per leaf: `20`;
- L2 regularization: `1.0`;
- max features: `1.0`;
- max bins: `255`;
- early stopping: false;
- warm start: false;
- class weight: none;
- random seed: `20260923`.

No hyperparameter search, AutoML, neural network, post-result model-family expansion, or post-result tuning is authorized.

## 9. Candidate conversion

Each fitted model emits probabilities for all three frozen classes.

A directional candidate exists only when:

1. one of `LONG` or `SHORT` is the strict unique highest-probability class; and
2. that directional probability is at least the frozen confidence cutoff.

Any probability tie is `NO_TRADE`.

The only confidence cutoffs are:

- `0.50`;
- `0.60`;
- `0.70`.

The thresholds are fixed constants. Selection results may choose among them but may never numerically move them.

Position size is not a function of model probability.

## 10. Selection

Each of the two model families × three confidence cutoffs creates exactly six variants per model cell.

Selection uses only the 2021-2022 split.

A variant passes the selection gate at the 0.5-pip scenario only if all are true:

- at least 250 directional candidates;
- total realized candidate net pips are strictly positive;
- mean realized candidate net pips are strictly positive;
- gross positive pips are strictly greater than absolute gross negative pips.

`NO_TRADE` rows contribute no candidate PnL.

If multiple variants pass, choose exactly one using this deterministic order:

1. higher total 0.5-pip net pips;
2. higher directional candidate count;
3. logistic regression before histogram gradient boosting;
4. higher confidence cutoff before lower confidence cutoff.

If no variant passes, the cell result is `NO_MODEL_CHALLENGER` and validation is not opened for that cell.

## 11. Validation

There is no refit.

A selected variant is evaluated unchanged on 2023-2024.

The validation gate requires the same four conditions independently under both:

- 0.5 pip adverse slippage per fill;
- 1.0 pip adverse slippage per fill.

The 0.2-pip scenario is retained as diagnostic evidence only.

A validation failure rejects the cell and leaves its retrospective holdout unopened.

## 12. Retrospective holdout

Only a cell that passes validation may open its frozen 2025-01-01 through 2026-08-20 retrospective holdout.

The exact fit-period preprocessor, estimator, and selected confidence cutoff are reused unchanged.

The holdout gate repeats the validation gate under both 0.5 and 1.0 pip adverse slippage.

Passing this historical gate may establish a historically qualified research candidate only.

Because this history was already seen elsewhere in the project, it is not untouched OOS evidence and does not authorize shadow/demo/live activity.

## 13. Metrics

For a directional candidate, realized candidate pips use the outcome column matching its predicted direction and evaluation slippage scenario.

Required evidence includes:

- directional candidate count;
- directional candidate rate;
- LONG/SHORT counts;
- total net pips;
- mean net pips;
- gross positive pips;
- absolute gross negative pips;
- positive/negative/zero candidate counts;
- class prevalence;
- confusion matrix;
- multiclass log loss where defined;
- model probability digest;
- deterministic candidate identity digest.

Classification diagnostics are preserved but do not override the frozen financial gate.

## 14. Relationship to rule benchmarks

DEC-073 still requires later comparison with transparent rule-based benchmarks.

DEC-088 does not pretend that fixed-horizon direct-market labels and Phase 3 stop/target strategy returns are identical financial objects.

Any benchmark comparison or portfolio/promotion decision therefore requires a later explicitly frozen gate.

## 15. Determinism and evidence

A later result-producing implementation must bind:

- the exact merged DEC-088 protocol source commit;
- a canonical protocol fingerprint;
- the exact DEC-074 readiness evidence;
- exact feature/outcome manifest identities for each cell;
- runtime dependency versions;
- preprocessing state;
- estimator configuration;
- fitted-model identity;
- score/candidate digests;
- every rejected or failed cell.

Negative results remain evidence.

## 16. Locks

DEC-088 keeps all of the following false:

- `model_protocol_result_authorized`;
- `model_fit_authorized`;
- `promotion_authorized`;
- shadow authorization;
- demo-order authorization;
- broker mutation;
- live-order authorization;
- real-money authorization.

No model fit may occur merely because this source protocol has been merged.

## 17. Next gate

After DEC-088 source and tests are merged on `main`, a separate guarded decision may authorize exactly one result-producing EXP-044 model-training workflow.

That future gate must bind the merged protocol fingerprint and the verified DEC-074 readiness chain before changing either `model_protocol_result_authorized` or `model_fit_authorized`.
