# Phase 6 Statistical / ML Filter Design

**Date:** 2026-09-15
**Status:** APPROVED IN CHAT — PENDING WRITTEN-SPEC REVIEW
**Planned experiment:** `EXP-20260915-007`
**Final-test touched?: NO**

## 1. Purpose

Phase 6 answers one narrow question: do simple statistical / ML filters add robust incremental value over the two frozen Phase 4 rule-based candidates after realistic costs?

Phase 6 does not create a new trading strategy. It evaluates optional filters after an already-valid strategy candidate exists and before that candidate reaches the accepted Phase 3 decision / risk / execution machinery.

This matches the project architecture:

`Feature Engine -> Strategy Candidates -> Optional ML / Statistical Filters -> Decision Engine -> Risk Engine -> Backtest`

The ML layer must earn its place. A rule-only candidate remains preferred unless a simple model materially improves robust out-of-sample behavior under the frozen gate below.

## 2. Governing project rules

The following existing rules remain authoritative and are not changed by Phase 6:

- Forex-only V1.
- Canonical BID/ASK execution and accepted Phase 3 simulator semantics.
- Phase 3 risk policy: requested risk/trade 0.25%; hard max 0.50%; max simultaneous open risk 1.00%; UTC day-start realized-loss halt 1.50%.
- No look-ahead bias or random final time-series shuffling.
- Leakage-sensitive transforms fit on training data only.
- Complexity must materially outperform simpler baselines after costs.
- Failed model experiments remain evidence.
- Final untouched test remains 2024-01-01 through 2026-08-20 and is unavailable to normal Phase 6 tooling.
- Phase 7 walk-forward, broker/live/demo integration, and real-money trading remain separate later gates.

Phase 5 checkpoint `fmp-v1-phase5-features` at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0` remains the authoritative feature-engine freeze. Phase 6 may use only `fmp-feature-v1` semantics and accepted Phase 5 feature identities.

The accepted USDJPY Phase 2 processed-manifest SHA-256 remains:

`e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

## 3. Frozen rule baselines

Phase 6 evaluates exactly the two serious Phase 4 candidates, unchanged:

### Candidate A — session breakout

- symbol: USDJPY
- timeframe: 15m
- family: session breakout
- buffer: 5 pips
- target: 1.5x frozen session range
- Phase 4 source: EXP-20260914-001

### Candidate B — volatility breakout

- symbol: USDJPY
- timeframe: 1h
- family: rolling volatility breakout
- range expansion multiplier: 2.0x
- target: fixed 1.0R
- Phase 4 source: EXP-20260914-005

No stop, target, signal window, session definition, breakout threshold, cost assumption, or strategy parameter may be retuned in Phase 6.

## 4. Scope

Phase 6 V1 contains one predeclared experiment, `EXP-20260915-007`, covering both frozen rule baselines and exactly two simple model families.

Included:

- deterministic candidate / feature / label dataset construction;
- training-only preprocessing;
- one linear model and one shallow nonlinear model per frozen strategy;
- three predeclared score cutoffs per fitted model;
- chronological model selection using 2019-2020 only;
- one untouched external validation evaluation using 2021-2023 only;
- comparison against the corresponding rule-only baseline through unchanged Phase 3 backtesting semantics;
- deterministic evidence artifacts and experiment logging.

Excluded:

- generic next-bar prediction;
- new entry/exit logic;
- strategy-parameter retuning;
- feature-family expansion;
- target-driven feature selection;
- cross-pair models;
- cross-timeframe joins;
- deep learning / neural networks;
- random forests, SVM grids, AutoML, Bayesian optimization, random search, grid search, stacking, ensembling, or architecture search;
- probability-based position sizing;
- changing Phase 3 risk limits;
- final-test reads;
- Phase 7 walk-forward execution;
- broker/live/demo paths;
- real-money trading.

## 5. Data chronology

The existing development / validation / final chronology is preserved while development is split once for model fitting versus model selection.

Exact Phase 6 periods:

- model fit: 2015-01-01 through 2018-12-31 inclusive;
- model / cutoff selection: 2019-01-01 through 2020-12-31 inclusive;
- external validation: 2021-01-01 through 2023-12-31 inclusive;
- final untouched test: 2024-01-01 through 2026-08-20 inclusive.

Normal Phase 6 APIs expose only `fit`, `selection`, and `validation` split names. They do not expose an arbitrary date-range or `final` split option.

Any request, artifact, source partition, feature partition, candidate timestamp, label timestamp, or output timestamp reaching 2024-01-01 or later must fail before that final-test partition is opened.

## 6. Modeling unit

Models are fitted separately for Candidate A and Candidate B. There is no pooled cross-strategy model.

One row represents one directional strategy setup emitted by the exact frozen Phase 4 strategy implementation.

`NO_TRADE` strategy outputs are retained in rule-baseline accounting but are not model-training examples. Directional setups that fail structural executability checks are recorded as rejected / unlabelable evidence and are not silently repaired.

## 7. Feature provenance, materialization, and decision-time safety

Phase 6 does not require GitHub's Phase 5 acceptance ZIPs to remain permanent storage. It may deterministically regenerate only the required USDJPY 15m and 1h `fmp-feature-v1` tables from the accepted Phase 2 processed artifact, using feature-engine code whose behavior remains byte-equivalent to the Phase 5 checkpoint. Phase 6 must not modify Phase 5 feature semantics.

Every regenerated feature manifest must bind:

- `feature_set_version == "fmp-feature-v1"`;
- Phase 5 checkpoint `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`;
- USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`;
- exact 2015-01-01 through 2023-12-31 maximum allowed feature coverage;
- deterministic file / schema digests.

For a strategy signal based on the left-labelled observation bar beginning at `T` with width `D`:

- strategy observation timestamp = `T`;
- signal known timestamp = `T + D`;
- the joined Phase 5 feature row must have `bar_start_utc == T`;
- the same row must have `available_at_utc == T + D`;
- feature set version must equal `fmp-feature-v1`;
- feature processed-manifest identity must match the accepted USDJPY identity.

The model input is therefore frozen at the same true-known time as the strategy signal and cannot see the next execution bar.

The exact 48 Phase 5 feature values are eligible inputs. Add exactly one strategy-known field:

- `signal_direction`: LONG = `+1`, SHORT = `-1`.

No future geometry, realized PnL, target outcome, validation statistics, or post-signal observation may be an input.

## 8. Label contract

Primary label: `target_before_stop`.

For each structurally executable directional setup:

- label `1` if the frozen strategy target is reached before the frozen stop and before the mandatory strategy time exit;
- label `0` if the frozen stop is reached first, the mandatory time exit occurs before target, or unresolved same-bar target/stop reachability is conservatively resolved to stop under accepted Phase 3 semantics.

The label is generated from future historical BID/ASK bars only after the feature row is frozen. It is never exposed as a feature. Label resolution is itself restricted to pre-2024 source coverage.

### 8.1 Structural executability

A setup is label-eligible only if:

- the first true next execution bar exists;
- frozen stop / target geometry remains valid at the accepted executable-side entry convention;
- the exact mandatory exit required by the strategy exists;
- future bars required to resolve stop / target / time exit are present under the frozen strategy semantics.

If any of these fail, the setup is recorded as unlabelable / structurally rejected with a reason code and excluded from model fitting. The strategy is never repaired, widened, chased, or retried.

### 8.2 Risk-policy independence of the label

`target_before_stop` describes setup path quality, not portfolio state. Daily halt or simultaneous-risk rejection does not change the historical label. Financial promotion is decided later by running admitted signals through the unchanged Phase 3 engine, where all risk rejections remain authoritative.

## 9. Preprocessing

Preprocessing is fitted independently per strategy on the 2015-2018 fit rows only.

Common preprocessing:

- retain the frozen input-column order;
- convert booleans to deterministic 0/1 numeric values;
- replace non-finite values with null before fitting;
- fit a per-column median imputer on fit rows only;
- apply those frozen medians unchanged to selection and validation;
- if an input column is entirely null in the fit period, fail closed for that strategy/model experiment rather than invent a fill value;
- record every fitted median in the evidence manifest.

Logistic regression additionally fits `StandardScaler` means / scales on the median-imputed fit rows only. Those scaler parameters remain frozen for selection and validation.

The tree challenger receives the same median-imputed input values but no scaling.

No target-aware feature selector is authorized.

## 10. Model dependencies and determinism

Use `scikit-learn==1.9.1`, the current stable release verified from the official scikit-learn release documentation on 2026-09-15.

The exact runtime versions of Python, scikit-learn, NumPy, SciPy, Polars, and platform architecture must be recorded in evidence.

Global experiment seed: `20260915`.

Model fitting must be deterministic under the pinned dependency / runtime contract. Repeated fits on identical bytes must produce identical prediction-score digests on fit, selection, and validation inputs.

No accepted evidence depends on a pickle / joblib model object. Reproducibility is established from frozen data identities, preprocessing parameters, model configuration, seed, fitted public parameters where available, and deterministic prediction digests.

## 11. Frozen model families

Exactly two challengers are authorized per frozen strategy.

### 11.1 Model L — L2 logistic regression

`sklearn.linear_model.LogisticRegression` with exactly:

- `penalty="l2"`;
- `C=1.0`;
- `solver="lbfgs"`;
- `tol=1e-8`;
- `fit_intercept=True`;
- `class_weight=None`;
- `max_iter=2000`;
- `warm_start=False`.

The model consumes median-imputed and standardized inputs.

Failure to converge is a model failure, not a reason to raise `max_iter`, change `C`, or switch solver under the same experiment ID.

### 11.2 Model H — shallow histogram gradient boosting

`sklearn.ensemble.HistGradientBoostingClassifier` with exactly:

- `loss="log_loss"`;
- `learning_rate=0.05`;
- `max_iter=100`;
- `max_leaf_nodes=15`;
- `max_depth=3`;
- `min_samples_leaf=20`;
- `l2_regularization=1.0`;
- `max_features=1.0`;
- `max_bins=255`;
- `early_stopping=False`;
- `warm_start=False`;
- `class_weight=None`;
- `random_state=20260915`.

The model consumes median-imputed unscaled inputs.

There is no tree hyperparameter search.

## 12. Score semantics and calibration

Both models emit the positive-class `predict_proba[:, 1]` value as `model_score`.

The score is used only for ranking / filtering. Phase 6 does not assume it is a calibrated real-world probability and does not use it for position sizing or a fixed probability interpretation.

Required diagnostics per strategy/model/split:

- ROC-AUC;
- `average_precision_score`;
- Brier score;
- positive-class prevalence;
- score min / max / mean / median;
- deterministic 10-bin equal-frequency reliability summary where sample size permits.

Reliability bins are formed after sorting by `(model_score, candidate_id)` and splitting the sorted rows into at most ten contiguous chunks whose sizes differ by at most one. Each bin records row count, mean model score, and observed positive rate. The reliability summary is diagnostic only and never participates in promotion.

Because promotion uses score ranks rather than claimed probability levels, no extra probability calibrator is fitted in this experiment. If a later system needs numerically calibrated probabilities, that requires a separate predeclared experiment rather than post-result calibration here.

If a required split has only one label class, model evaluation fails closed for that strategy/model; no metric fabrication or rescue split is allowed.

## 13. Frozen score cutoffs

Threshold candidates are derived from the 2015-2018 fit-period score distribution only.

For each strategy/model, define desired retained fractions exactly:

- `0.75`;
- `0.50`;
- `0.25`.

For a retained fraction `r`, sort the `N` fit scores ascending and choose cutoff index:

`min(N - 1, ceil((1 - r) * N))`.

The cutoff is the score at that zero-based index. Future setups are admitted when `model_score >= cutoff`.

Ties may therefore retain more than the nominal fraction. Actual retained count / rate is always reported.

No threshold is derived from selection or validation scores.

The unfiltered rule-only candidate remains the baseline and is not considered a threshold candidate.

## 14. Model / cutoff selection gate

Each of the six model-filter variants per strategy (2 models x 3 frozen cutoffs) is evaluated on 2019-2020 only.

Financial evaluation uses the unchanged Phase 3 engine and the exact Phase 4 candidate configuration.

Mandatory baseline cost scenario:

- adverse slippage: 0.2 pip per fill;
- commission: zero;
- financing: zero;
- historical BID/ASK spread remains inherent;
- Phase 3 risk policy unchanged.

A filtered variant qualifies for external validation only if, on the 2019-2020 selection period, all conditions hold:

1. actual executed trade count is at least 40% of the rule-only baseline trade count;
2. net return > 0;
3. expectancy/trade > 0;
4. profit factor > 1;
5. filtered net return > rule-only net return;
6. filtered expectancy/trade > rule-only expectancy/trade;
7. filtered profit factor > rule-only profit factor;
8. filtered maximum drawdown <= rule-only maximum drawdown.

### 14.1 Single selection per strategy

At most one model + cutoff is frozen per strategy for external validation.

Among qualifying variants, rank by:

1. highest net return improvement over rule baseline;
2. then highest expectancy improvement;
3. then highest profit-factor improvement;
4. then lowest maximum drawdown;
5. then higher retained trade count;
6. then simpler model family, with logistic regression preferred over histogram boosting;
7. then less restrictive cutoff: 0.75 retained fraction before 0.50 before 0.25.

If no variant qualifies, that strategy receives no ML challenger and validation cannot be used to rescue one.

Selection outcomes are frozen before opening the 2021-2023 validation partition.

## 15. External validation gate

The one frozen selection, if any, is evaluated exactly once on 2021-2023.

The model, preprocessing parameters, and cutoff remain exactly those fitted / derived from 2015-2018. There is no refit on 2019-2020 before validation. The 2019-2020 period selects among already-fitted variants only.

### 15.1 Baseline 0.2-pip gate

Promotion requires every condition:

1. executed trade count >= 40% of the corresponding rule-only validation baseline;
2. net return > 0;
3. expectancy/trade > 0;
4. profit factor > 1;
5. filtered net return > rule-only net return;
6. filtered expectancy/trade > rule-only expectancy/trade;
7. filtered profit factor > rule-only profit factor;
8. filtered maximum drawdown <= rule-only maximum drawdown;
9. filtered yearly net PnL exceeds the rule-only yearly net PnL in at least two of validation years 2021, 2022, and 2023.

### 15.2 0.5-pip robustness gate

The same frozen model/cutoff is rerun with adverse slippage 0.5 pip per fill.

It must:

- remain positive in net return and expectancy with profit factor > 1;
- outperform the corresponding 0.5-pip rule-only baseline on net return, expectancy, and profit factor;
- have maximum drawdown no worse than the corresponding rule-only baseline.

### 15.3 1.0-pip diagnostic

The exact frozen variant is also evaluated at 1.0 pip adverse slippage as a diagnostic only.

A 1.0-pip result cannot rescue a failure at 0.2 or 0.5 pip and is not itself a universal rejection condition.

## 16. Filter behavior inside backtesting

For a directional candidate:

- if score >= frozen cutoff, preserve the original strategy candidate unchanged;
- if score < cutoff, convert the opportunity into an explicit model-filter rejection / `NO_TRADE` record with reason `ML_FILTER_REJECTED` and record model ID, score, cutoff, strategy candidate ID, feature-row identity, and feature-set version.

No accepted signal may have its stop, target, time exit, risk request, or timestamp changed by the model.

Risk and daily-halt behavior are evaluated only inside the unchanged Phase 3 engine after filtering.

## 17. Evidence artifacts

Every result-producing cell must emit deterministic evidence containing at minimum:

### 17.1 Dataset identity

- experiment ID;
- code commit;
- strategy family / exact frozen config;
- symbol / timeframe;
- split;
- Phase 5 feature-set version;
- Phase 5 checkpoint identity;
- accepted processed-manifest SHA-256;
- candidate row count and candidate digest;
- labeled row count;
- rejected / unlabelable counts by reason;
- feature row count / joined count;
- exact input-column list;
- label prevalence;
- earliest/latest feature availability timestamp;
- earliest/latest label-resolution timestamp;
- proof that all opened coverage is pre-2024.

### 17.2 Preprocessing identity

- imputation medians;
- scaler means/scales where applicable;
- null counts before/after transformation;
- transformed matrix digest.

### 17.3 Model identity

- model family / frozen config;
- random seed;
- Python / scikit-learn / NumPy / SciPy / Polars versions;
- fit-row count;
- convergence / fit status;
- deterministic fit/selection/validation score digests.

### 17.4 Threshold / selection evidence

- three fit-derived cutoff values;
- nominal and actual retained fractions;
- all six selection-period filtered financial rows per strategy;
- rule-only baseline rows;
- gate booleans for each criterion;
- deterministic tie-break record;
- frozen selected variant or explicit `NO_ML_CHALLENGER`.

### 17.5 Validation evidence

For the one selected variant per strategy, if any:

- 0.2 / 0.5 / 1.0-pip cost rows;
- corresponding rule-only rows;
- classification diagnostics;
- calendar-year breakdowns;
- retention counts;
- all promotion-gate booleans;
- conclusion: `PROMOTE_ML_FILTER` or `REJECT_ML_FILTER`.

No result file may contain final-test metrics.

## 18. Determinism / leakage tests

Required permanent tests include:

1. Phase 6 split parser exposes only fit/selection/validation.
2. 2024+ request fails before feature/candidate/source partition open.
3. Feature join requires exact observation-bar / available-at identity.
4. Future feature perturbation cannot affect earlier model rows.
5. Label generation uses no value at or before feature freeze that depends on the future.
6. Same-bar target/stop ambiguity maps to label 0 / stop-first semantics.
7. Time-exit-before-target maps to label 0.
8. Structurally invalid next-bar geometry is excluded with an explicit reason.
9. Fit-only imputer/scaler parameters are unchanged when selection/validation values are perturbed.
10. Thresholds depend only on fit scores.
11. Validation cannot be opened until the selection artifact is frozen.
12. No refit occurs after model/cutoff selection and before external validation.
13. Two identical fits yield identical prediction-score digests.
14. Filter rejection never mutates accepted candidate stop/target/timestamps.
15. Financial evaluation uses unchanged Phase 3 risk/cost semantics.
16. Rule-only baseline reproduction matches the frozen candidate protocol.
17. Experiment artifacts are byte-deterministic after canonical serialization.
18. No model code imports broker/live/demo/execution adapters.
19. No final-test path can appear in Phase 6 evidence.
20. Required USDJPY feature manifests bind the Phase 5 checkpoint and accepted processed-manifest identity.

## 19. Implementation architecture

Introduce a new package `src/fmp/models/` with focused modules:

- `contracts.py` — experiment/model/split contracts;
- `data.py` — pre-2024 candidate-feature join and split reader;
- `labels.py` — deterministic target-before-stop labels;
- `preprocessing.py` — fit-only median / scaling transforms;
- `estimators.py` — exact two frozen sklearn estimators;
- `thresholds.py` — fit-only cutoff derivation;
- `filtering.py` — explicit admit/reject adapter for strategy candidates;
- `evaluation.py` — classification + financial gate evaluation;
- `artifacts.py` — deterministic manifests/evidence;
- `cli.py` — source-free research CLI with no final split.

Do not move or rewrite Phase 3 / Phase 4 / Phase 5 implementation unless a small interface adapter is strictly required and separately tested.

## 20. Workflow shape

Add a manual/source-free Phase 6 workflow only after implementation tests are green.

The authoritative experiment runs exactly two strategy cells:

- USDJPY / 15m / session-breakout Candidate A;
- USDJPY / 1h / volatility-breakout Candidate B.

Each cell must:

1. obtain accepted processed data and deterministically materialize / verify the required Phase 5 feature inputs without source acquisition;
2. verify the accepted USDJPY processed-manifest and Phase 5 checkpoint identities;
3. build deterministic candidate-feature-label rows for fit/selection only;
4. fit both models twice and verify identical score digests;
5. evaluate all six selection variants;
6. freeze zero or one challenger before opening validation;
7. if a challenger exists, open validation once and evaluate the same frozen fit/preprocessor/cutoff under exact 0.2/0.5/1.0 scenarios;
8. upload deterministic evidence.

The workflow must have no Dukascopy acquisition path, no Supabase write path, no broker/live/demo path, and no final-test path.

## 21. Phase 6 acceptance semantics

Phase 6 PASS does not require an ML winner.

The ML question is considered answered honestly when both frozen strategies have completed the predeclared experiment with deterministic leakage-safe evidence.

Possible outcomes:

### Outcome A — ML adds robust incremental value

At least one strategy has exactly one frozen model-filter challenger that clears the full selection and external-validation gates. That challenger is retained unchanged for Phase 7 comparison alongside the underlying rule baseline.

### Outcome B — ML is rejected

No challenger clears the full gates. The negative evidence remains recorded and the simpler rule-only candidate(s) remain preferred for Phase 7.

Phase 6 can PASS under either outcome if the protocol was executed correctly and completely.

## 22. Checkpoint and later-phase locks

After implementation, experiment execution, independent evidence audit, acceptance closure, merged-main regression verification, and explicit Phase 6 acceptance review, create:

`fmp-v1-phase6-models`

The checkpoint does not itself authorize final-test access.

Phase 7 remains a separate walk-forward design/implementation gate. The final untouched test remains locked until a later explicit promotion decision after candidate selection and walk-forward evidence are materially complete.

Broker/live/demo integration and real-money trading remain locked.

## 23. Planned change-control record

After written-spec approval, record DEC-031 as the Phase 6 statistical / ML filter protocol and mark Phase 6 ACTIVE. DEC-031 must reference this design, the exact chronology, both frozen candidate configurations, two frozen model configurations, selection / validation gates, final-test hard block, and `EXP-20260915-007`.

No result-driven widening is permitted under `EXP-20260915-007`. Any new model family, hyperparameter search, different label, different retention threshold, different split, probability calibration layer, new feature, pooled strategy model, altered refit rule, or altered promotion gate requires a new experiment ID and explicit design/change-control decision before execution.
