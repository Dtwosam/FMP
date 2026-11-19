# Dependence-aware statistical validation V1

**Status:** source-only infrastructure. Synthetic observations only.
**Governing method:** discovery-first annual pattern catalogue research under DEC-469 / DEC-268.
**Pattern tool:** `dependence-aware-validation-v1`.
**Protocol:** `fmp-annual-pattern-catalogue-dependence-validation-v1`.
**Parent contracts:** DEC-470, event-level evidence V1, and statistical uncertainty V1, all unchanged.

This tool asks whether a statistical procedure produces a defensible uncertainty statement when observations are serially dependent, overlapping, shared across hypotheses, or selected from a family. The rows are synthetic. A pass under a declared synthetic model leaves catalogue inference at `CATALOGUE_INFERENCE_NOT_AUTHORIZED`.

## Preserved contracts

The annual miner, the DEC-470 protocol, the cross-year engine, the event-level evidence schema, the statistical-uncertainty schema, and the frozen evidence validators are unchanged.

| Contract | Recorded state |
| --- | --- |
| DEC-470 fingerprint | `3f883b26f3d9da04840b9680701504833dbcb3ec2c919f74ed191a3ab1bd3d69` |
| Directional hypotheses per annual segment | 89,460 |
| DEC-470 thresholds | Unmodified. Support 75, cross-year segments 9, base positive fraction 0.80, stress positive fraction 2/3, median annual mean 0.10, pooled mean 0.25, pooled stress mean positive, maximum sign flips 3, near-duplicate Jaccard 0.90. |
| Statistical uncertainty V1 lags and blocks | Lags 1, 4, 8 and blocks 1, 4, 8. Lag 16 remains refused there. |
| Cross-year statistical block | `p_values`, `independent_trial_standard_errors`, and `multiple_comparison_adjustment` remain `UNAVAILABLE_NOT_COMPUTED`. |
| Annual run 385 | Unconsumed. |
| DEC-629 and DEC-630 | Unadopted. |
| Workflows 373883560 and 357842915 | Left disabled. This milestone does not edit workflow files. |

Newey–West lags 1, 4, and 8 in this module agree with statistical uncertainty V1 on a shared series. Lag 16 exists only in this module. It is a predeclared candidate, and it was fixed before any holdout count was used to choose it.

## What stays closed on catalogue evidence

An assessment of caller-supplied events returns `CATALOGUE_INFERENCE_NOT_AUTHORIZED` and `P_VALUES_UNAVAILABLE`. It computes no interval. Episode groups are refused as independent trials. An independence assumption is refused. A historical path, a request to authorize catalogue inference, a missing provenance record, and a claimed sample size that exceeds the unique-event count fail closed. Event ids are still refused when recovered from an annual `event_fingerprint`.

Effective sample size in this harness comes from the declared synthetic model: marginal variance divided by the variance of the mean. It is not estimated from a sample autocovariance, and it is not written onto event evidence. Duplicated hypothesis rows keep the event count. The row count is rejected as the effective sample size.

## Predeclared design

Development and evaluation are separate partitions. Calibration uses master seed 20261126. The holdout uses master seed 20261211. Stability uses 20261212 and 20261213 and is kept out of the holdout denominator. Family seeds are 20261130, 20261215, 20261216, 20261217, 20261219, 20261220, 20261221, and 20261222. Seeds 20261118 through 20261125 are refused. Those are the EXP-20261118-069 masters and the statistical-uncertainty V1 calibration masters. They are not reused as a second confirmation of those experiments.

The prior AR(1) counts from statistical uncertainty V1 stay context: IID coverage 73/160, Newey–West lag 8 coverage 117/160, moving-block length 8 coverage 13/20. The acceptance rule records that those counts are neither thresholds nor tuning targets.

A revision of a method after inspecting results requires a fresh holdout. The holdout seed in this build was not used to choose a lag, a block length, or a threshold. Calibration and stability rows are forced to `EXPLORATORY_ONLY`.

| Item | Predeclared value |
| --- | --- |
| Estimand | Mean of the named synthetic series. |
| Null | Mean equals 0, except the planted series. |
| Alternatives | Planted means +0.35 and −0.35. Family alternatives use mean 0.5. |
| Nominal coverage and alpha | 0.95 and 0.05. Normal quantile 1.959963984540054. |
| Monte Carlo interval | Wilson score, same quantile. |
| Clear undercoverage | Wilson upper bound below 0.90, with at least 40 available replicates. |
| Clear overcoverage | Wilson lower bound above 0.98. |
| Clear anti-conservative test | Wilson lower bound of the rejection rate above 0.15. |
| Validation precision | At least 200 replicates, Wilson half-width at most 0.04, unavailable fraction at most 0.01, assumptions matched, and the holdout partition. |
| Borderline miss | Nominal value outside the Wilson interval, without a clear failure: `INSUFFICIENT_MONTE_CARLO_PRECISION`. |
| Mismatched assumptions | `MODEL_ASSUMPTIONS_UNVERIFIED`, unless the numeric result is a clear failure, which is `FAILED_SYNTHETIC_CALIBRATION`. |
| Familywise failure | Wilson lower bound above 0.05. |
| Familywise validation | Assumptions matched, validation precision, point estimate at or below 0.05, and Wilson lower bound at or below 0.05. A point above 0.05 whose Wilson interval still reaches 0.05 is insufficient precision. |
| Closed-form replicates | 80 calibration, 400 holdout. |
| Bootstrap replicates | 20 calibration, 60 holdout, 99 draws. Below the validation floor on purpose. |
| Studentized replicates | 60 holdout replicates of 49 draws. Below the validation floor on purpose. |
| Stability replicates | 40 on each stability seed. |
| Generator | Box–Muller on `random.Random` with integer seeds. |

`VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL` means the procedure met its own predeclared synthetic check. It does not authorize catalogue inference. Software that round-trips canonical JSON is a separate fact from synthetic calibration, and synthetic calibration is a separate fact from authentic statistical validity.

A larger bootstrap validation, at least 200 replicates, was specified and was not launched. Its approximate cost relative to the 60-replicate bootstrap is a factor of about 3.33, before any increase in draws.

## Candidate methods

These procedures are candidates. Eligibility is fixed from the known data-generating process before the holdout counts are read.

| Method | Eligibility in this build | Testing status |
| --- | --- | --- |
| IID normal interval | Stationary dependence horizon 0, or independent observations with a variance break. Sample variance uses `n - 1`. | Interval only. `P_VALUES_UNAVAILABLE`. |
| IID variance z | The marginal variance divided by `n` equals the exact variance of the mean. | Exact Gaussian null p-value when eligible. |
| Declared-model z | Caller supplies the exact variance of the mean. Duplicated rows and a constant series are ineligible even when a number can be computed. | Exact Gaussian null p-value on a zero-mean eligible series. Planted means are power diagnostics and stay `EXPLORATORY_ONLY`. |
| Newey–West, Bartlett kernel | Covariance-stationary target whose material autocovariance horizon is within the lag. Lags 1, 4, 8, and 16. Autocovariances divide by `n`. | Interval only. `P_VALUES_UNAVAILABLE`. |
| Moving-block bootstrap | Stationary target and block length at least the material horizon. Length 1 is eligible for independent series and for the variance break. Lengths 1, 4, 8, and 16 are predeclared. Percentile of 99 draw means. | Interval only. `P_VALUES_UNAVAILABLE`. |
| Circular and stationary block bootstrap | Same stationary rule, length 16 only, on independent, weak AR(1), strong AR(1), and long-memory series. The stationary bootstrap uses mean block length 16. | Interval only. `P_VALUES_UNAVAILABLE`. |
| Shared-clock block bootstrap | One block index applied to both series. Block length 8. Eligible when the dependence horizon is at most 8. | Interval only. Equal length is not timestamp alignment. |
| Independent-column block bootstrap | Each series draws its own indexes. | Always ineligible. Diagnostic of broken shared shocks. |
| Cluster-event bootstrap | Unique events of the shared-observation scenario. | Interval only. Copied rows are not extra trials. |
| Shock-rebuild bootstrap | Overlapping windows, resampling the underlying shocks and rebuilding the windows. | Interval only. |
| Studentized null-centered moving block | Eligible only where both block 16 and Newey–West lag 16 are eligible. Statistic is the mean divided by that Newey–West standard error. Blocks are drawn from the centered series. Plus-one p-value `(1 + exceedances) / (1 + draws)`. | A computed p-value whose Monte Carlo size is below the validation floor stays `INSUFFICIENT_MONTE_CARLO_PRECISION`. `valid_p_values_established` is false. The percentile interval is not inverted. |

A constant shared-clock contrast is exactly that constant on every shared-clock draw. The normal standard error stays unavailable.

## Synthetic processes

Series length is 120 unless a row says otherwise. Innovation scale is 1. The generator restarts at the partition master for each scenario.

| Scenario | Process | Material horizon | Effective sample size |
| --- | --- | --- | --- |
| `independent_zero_edge` | Independent normal, mean 0. | 0 | 120 |
| `weak_ar1` | Stationary AR(1), phi 0.3, mean 0. | 2 | 64.97237569060773 |
| `strong_ar1` | Stationary AR(1), phi 0.8, mean 0. | 13 | 13.84615384615259 |
| `long_memory` | Moving-average of order 23. Weights follow `(k+1)^(-0.6)`, normalized so the lag-0 autocovariance is 1. | 23 | 7.663093882562344 |
| `overlapping_windows` | Mean of each 4 consecutive shocks. | 3 | 30.31578947368421 |
| `shared_identical_observations` | 60 independent events. The duplicated target repeats each event twice, in order. | 0 on the unique events | 60 for both targets |
| `common_shock_cross_symbol` | Two series share a factor with weight squared 0.49. The contrast removes the factor. | 0 | 120 |
| `multiple_horizons` | The short series is the last shock of each window of 4. The long series is the window average. The contrast is long minus short. | 0 on the short series, 3 on the long series and the contrast | 120 on the short series, 30.31578947368421 on the long series, unavailable on the contrast |
| `changing_volatility` | Independent normal draws. Scale 1 on the first half and scale 3 on the second half. | Variance break. Newey–West and long blocks are ineligible. | 120 under the average-innovation-variance definition |
| `regime_change` | 60 independent draws, then 60 independent AR(1) draws with phi 0.9. | Nonstationary. Only the declared-model z is eligible. | Unavailable |
| `planted_positive` / `planted_negative` | Independent normal draws with mean +0.35 or −0.35. | 0 | 120 |
| `degenerate_constant` | 120 zeros. | No variance. | Unavailable |

The AR(1) effective sample size is the finite-sample variance-equivalent size `n / [1 + 2 * sum((1 - k/n) * phi**k)]`. The large-sample formula `n * (1 - phi) / (1 + phi)` is a different number. At n = 2 and phi = 0.5 the finite-sample variance of the mean is 1 and the effective sample size is 4/3. Overlapping means of length 2 and horizon 2 have variance 0.375. Episode groups are not trials.

## Holdout realization

The counts below are the Python 3.12.13 realization on this machine for master seed 20261211. Tests recompute each status from the stored numerator and denominator. They do not lock the numerators, because a different libm can change a count. The status rule is what the tests lock.

Holdout partition rows: 40 `VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL`, 47 `FAILED_SYNTHETIC_CALIBRATION`, 46 `INSUFFICIENT_MONTE_CARLO_PRECISION`, 24 `MODEL_ASSUMPTIONS_UNVERIFIED`. Every row has catalogue inference `CATALOGUE_INFERENCE_NOT_AUTHORIZED`.

The declared-model z interval, which uses the known variance of the mean, covered its true mean on the eligible zero-mean series at 374/400 to 386/400. Its null rejection counts on those series were 14/400 to 26/400. Those rows have `valid_p_values_established` true. The same interval on the planted series covered the planted mean at 375/400. Rejecting zero there is a power count, 384/400 for the positive mean and 386/400 for the negative mean, and those p-value rows stay `EXPLORATORY_ONLY`.

Eligible procedures that failed their own check, and were left at the predeclared lag or block:

| Series | Method | Coverage | Wilson 95 percent bounds | Status |
| --- | --- | --- | --- | --- |
| Strong AR(1) | Newey–West lag 16 | 325/400 | 0.771344 to 0.847711 | Failed. The lag meets the horizon of 13. |
| Overlapping windows | Newey–West lag 16 | 343/400 | 0.819837 to 0.888362 | Failed. The lag meets the horizon of 3. |
| Unique events, n = 60 | Newey–West lag 16 | 347/400 | 0.830754 to 0.897255 | Failed. A long lag on a short independent series undercovered. |
| Strong AR(1) | Moving block 16 | 49/60 | 0.700802 to 0.894422 | Failed. The block meets the horizon. |
| Strong AR(1) | Circular block 16 | 49/60 | 0.700802 to 0.894422 | Failed. |
| Overlapping windows | Moving block 4 | 48/60 | 0.682182 to 0.881715 | Failed. The block meets the horizon. |
| Horizon contrast | Newey–West lags 4, 8, and 16 | 400/400 | 0.990488 to 1 | Failed by overcoverage. The intervals were wide relative to the Monte Carlo standard deviation of the mean, 0.011606, against a lag-16 mean width of 0.121360. |

Ineligible procedures that failed in the expected direction include the IID interval on weak AR(1) at 342/400, strong AR(1) at 186/400, long memory at 133/400, overlapping windows at 266/400, the long horizon at 266/400, regime change at 132/400, and duplicated rows at 340/400. The duplicated-row IID interval uses 120 rows for a process whose effective sample size is 60. The declared-model interval on those duplicated rows covered at 386/400 and remains `MODEL_ASSUMPTIONS_UNVERIFIED`, because a duplicated representation is not an authorized sampling model. Its p-values stay `P_VALUES_UNAVAILABLE`.

Long memory has material horizon 23. No predeclared lag or block is eligible. Newey–West lag 16 covered 285/400 and moving block 16 covered 42/60. Both failed under mismatched assumptions. The declared-model interval covered 374/400 and validated.

Changing volatility left the IID interval and the declared-model interval validated at 378/400. The marginal-variance z interval was unavailable on all 400 replicates. Newey–West coverage from 358/400 to 380/400 stayed `MODEL_ASSUMPTIONS_UNVERIFIED`.

Studentized null tests rejected 4/60, 4/60, 5/60, and 3/60 on the independent, weak AR(1), strong AR(1), and overlapping series. Each Wilson interval still reaches both sides of 0.05, and 60 replicates are below 200, so each row is `INSUFFICIENT_MONTE_CARLO_PRECISION`. The p-values were computed. They are not established, and catalogue assessment still returns `P_VALUES_UNAVAILABLE`.

Bootstrap and studentized rows cannot reach `VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL` in this build. The import-time check requires their replicate counts to stay below 200.

Stability seeds 20261212 and 20261213, 40 replicates each, stayed `EXPLORATORY_ONLY` and were not pooled. IID coverage rates were 0.925 and 0.95 on the independent series, 0.45 and 0.45 on the strong AR(1), and 0.675 and 0.65 on the overlapping windows. Newey–West lag 16 rates were 0.825 and 0.90, 0.825 and 0.825, and 0.85 and 0.90 on those three series. The span is a seed range. It is not a binomial standard error.

## Multiple testing and selection

The reference family remains 89,460 directional hypotheses per annual segment. A bounded synthetic family does not replace it. Familywise error at 89,460 was not estimated. Holm arithmetic on one vector of 89,460 uniform draws took 0.035872 seconds and estimated no error rate.

Individual p-values in the synthetic families are exact Gaussian tail probabilities at standard error `1/sqrt(120)`. Holm uses the step-down adjusted p-values with the running maximum. The hand example `[0.01, 0.04, 0.03]` adjusts to `[0.03, 0.06, 0.06]`. Uncorrected familywise tests and Holm applied only to the selected winner are ineligible for error-control claims.

| Study | Seed | Size | Holm familywise count | Holm status | Uncorrected count | Uncorrected status |
| --- | --- | --- | --- | --- | --- | --- |
| Calibration, equicorrelated complete null, rho 0.3 | 20261130 | 40 | 1/40 | Exploratory | 30/40 | Exploratory |
| Holdout, equicorrelated complete null, rho 0.3 | 20261215 | 40 | 17/400 | Validated under the declared model | 286/400 | Failed |
| Holdout, independent complete null | 20261216 | 40 | 19/400 | Validated under the declared model | 348/400 | Failed |
| Holdout, mixed, 36 nulls and 4 alternatives at mean 0.5, rho 0.3 | 20261217 | 40 | 17/400 true-null familywise rejections | Validated under the declared model | 400/400 | Failed |
| Holdout, independent complete null | 20261222 | 10 | 26/400 | Insufficient precision. Wilson bounds 0.044740 to 0.093535. | 174/400 | Failed |
| Scaling complete null, rho 0.3 | 20261221 | 160 | 4/80 | Insufficient precision | 78/80 | Failed |

The mixed-family Holm detection count on the four alternatives was 1582/1600. That power row is exploratory and is not an acceptance gate. Winner's-curse inflation is recorded and is not an acceptance gate. Shortlist-only Holm does not control the search that chose the winner.

Four annual segments of 20 complete-null hypotheses, 400 replicates, seed 20261219, selected the same hypothesis in at least two segments on 115/400 replicates. That chance recurrence is exploratory. It is not cross-year confirmation. The mean correlation between two independently drawn segments was 0.01616637208387591. An identical copy of one draw had correlation 1.0. Confirmation p-values for the shared copy and for the independent segments are `P_VALUES_UNAVAILABLE`.

## Integrity and cost

Canonical documents are UTF-8 JSON with sorted keys, compact separators, a trailing newline, and no duplicate keys. `content_sha256` is the SHA-256 of that document with the hash field removed. Wall-clock timings stay outside the hashed document.

One canonical compile on Python 3.12.13 took 17.177 seconds. Tracemalloc peak was 7,871,316 bytes. Canonical JSON was 974,640 bytes. SHA-256 was `296cd7113a302a893717cbc1d442efffc487c5169b5ca60568451116ac4b7c59`.

Holm arithmetic on one random p-value vector, measured outside the document: 40 hypotheses in 0.000014 seconds, 160 in 0.000033, 640 in 0.000162, 2,560 in 0.000646, 10,240 in 0.003010, and 89,460 in 0.035872. Those timings are not familywise-error estimates.

Focused `tests.test_annual_pattern_catalogue_dependence_validation` was 10 tests and exited 0 in 24.177 seconds. Neighboring statistical-uncertainty, event-evidence, protocol, miner, cross-year, and segment-evidence tests were 82 tests and exited 0 in 41.133 seconds.

## Authorization

Historical artifact reads, protected-year research, annual catalogue execution, authentic historical statistical results, DEC-470 retuning, research-gate retuning, pattern promotion, Strategy V1 synthesis, workflow activation, DEC-629, DEC-630, annual run 385, broker mutation, demo orders, and live trading stay closed. No trading or statistical promotion authorization is granted.

## Experiment

`EXP-20261119-074` records this synthetic harness. No decision-log number is assigned. The milestone does not change V1 instruments, the cost constraint, canonical granularity, testing gates, risk limits, real-money rules, or phase order. The experiment does not authorize a merge.
