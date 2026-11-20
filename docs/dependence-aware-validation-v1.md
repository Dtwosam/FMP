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
| Nominal coverage and alpha | 0.95 and 0.05. Two-sided normal quantile 1.959963984540054. One-sided 95 percent quantile 1.6448536269514722, which is the inverse of the standard normal distribution at 0.95. |
| Monte Carlo interval | Two-sided Wilson score for coverage and for the excessive-error rule. The familywise upper-bound claim uses the one-sided Wilson score. |
| Clear undercoverage | Wilson upper bound below 0.90, with at least 40 available replicates. |
| Clear overcoverage | Wilson lower bound above 0.98. |
| Clear anti-conservative test | Wilson lower bound of the rejection rate above 0.15. |
| Validation precision | At least 200 replicates, Wilson half-width at most 0.04, unavailable fraction at most 0.01, assumptions matched, and the holdout partition. |
| Borderline miss | Nominal value outside the Wilson interval, without a clear failure: `INSUFFICIENT_MONTE_CARLO_PRECISION`. |
| Mismatched assumptions | `MODEL_ASSUMPTIONS_UNVERIFIED`, unless the numeric result is a clear failure, which is `FAILED_SYNTHETIC_CALIBRATION`. |
| Familywise excessive error | Two-sided Wilson lower bound above 0.05, with at least 40 replicates. A matching assumption is not required. This failure rule is unchanged. |
| Familywise empirical control | `finite_sample_assumptions_exact`, at least 200 replicates, two-sided Wilson half-width at most 0.04, and the one-sided 95 percent Wilson upper bound at or below 0.05. A point estimate at or below 0.05 is not control when that upper bound exceeds 0.05. The quantile is the module's existing 95 percent level. It was not chosen so that 17/400 or 19/400 would pass. |
| Familywise inconclusive | Every other simulation whose assumptions match, including a point estimate below 0.05 whose one-sided upper bound exceeds 0.05, and a rate above 0.05 whose two-sided lower bound still reaches 0.05. |
| Inspected holdout | The revised positive rule is a methodological correction of counts that were already inspected. It is not a fresh independent validation. `newly_established_independent_pass` stays false. |
| Closed-form replicates | 80 calibration, 400 holdout. |
| Bootstrap replicates | 20 calibration, 60 holdout, 99 draws. Below the validation floor on purpose. |
| Studentized replicates | 60 holdout replicates of 49 draws. Below the validation floor on purpose. |
| Stability replicates | 40 on each stability seed. |
| Generator | Box–Muller on `random.Random` with integer seeds. |

`VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL` means the procedure met its own predeclared synthetic check. It does not authorize catalogue inference. Software that round-trips canonical JSON is a separate fact from synthetic calibration, and synthetic calibration is a separate fact from authentic statistical validity.

A larger bootstrap validation, at least 200 replicates, was specified and was not launched. Its approximate cost relative to the 60-replicate bootstrap is a factor of about 3.33, before any increase in draws.

## Candidate methods

These procedures are candidates. Eligibility is fixed from the known data-generating process before the holdout counts are read.

| Method | Role and dependence assumption | Testing status |
| --- | --- | --- |
| IID normal interval | `SAMPLE_ESTIMATED`. Sample variance uses `n - 1` and the half-width uses the normal z quantile. On independent and identically distributed series the dependence structure matches, and the interval is still a sample-estimated approximation. With unknown variance the exact finite-sample Gaussian reference is Student's t with `n - 1` degrees of freedom. The calculation is unchanged. On the changing-volatility series the draws are serially independent and are not identically distributed, so the identical-distribution design does not apply. `finite_sample_reference_exact` is false. | Interval only. `P_VALUES_UNAVAILABLE`. |
| IID variance z | `KNOWN_MODEL_ORACLE` when the declared marginal variance divided by `n` equals the variance of the mean. The variance is not estimated from a sample autocovariance. That known variance can make the z interval an exact finite-sample Gaussian reference. | Exact Gaussian null p-value when that identity holds. |
| Declared-model z | `KNOWN_MODEL_ORACLE`. The caller supplies the true variance of the mean. A jointly Gaussian series with that declared variance has an exact finite-sample z reference, including the changing-volatility series, whose observations are not identically distributed. This is not an estimator of unknown dependence. An oracle pass does not validate a practical dependence estimator. `captures_all_dependence` stays false. | Exact Gaussian null p-value on a zero-mean series whose declared variance matches. Planted means are power diagnostics and stay `EXPLORATORY_ONLY`. |
| Newey–West, Bartlett kernel | `SAMPLE_ESTIMATED`. Lags 1, 4, 8, and 16. Autocovariances divide by `n`. A lag at an autocorrelation floor is `PRACTICAL_AUTOCORRELATION_TRUNCATION`: later autocorrelation is small, not absent. A lag that includes every nonzero autocovariance of an exact finite-horizon process is `ASYMPTOTIC_WEAK_DEPENDENCE`, because Bartlett weights are not the exact long-run variance. `finite_sample_assumptions_exact` is false. `captures_all_dependence` is false. | Interval only. `P_VALUES_UNAVAILABLE`. |
| Moving-block bootstrap | `EXPERIMENTAL_BOOTSTRAP`. Length 1 preserves serial independence when the observations are identically distributed. That preservation does not make the percentile interval an exact finite-sample confidence interval. Length 1 on the changing-volatility series is not an identical-distribution resample. A longer block that reaches an autocorrelation floor is a practical truncation. A longer block that meets an exact finite horizon is an asymptotic approximation. Neither contains all AR(1) dependence. | Interval only. `P_VALUES_UNAVAILABLE`. Holdout replicates stay at 60, so a preserved length-1 resample stays unresolved. |
| Circular and stationary block bootstrap | `EXPERIMENTAL_BOOTSTRAP`. Length 16, on independent, weak AR(1), strong AR(1), and long-memory series. The stationary bootstrap uses mean block length 16. Both are asymptotic devices. `captures_all_dependence` is false. | Interval only. `P_VALUES_UNAVAILABLE`. |
| Shared-clock block bootstrap | `EXPERIMENTAL_BOOTSTRAP`. One block index applied to both series. Block length 8. Meeting an exact horizon is an asymptotic approximation, not an exact sampling model. | Interval only. Equal length is not timestamp alignment. |
| Independent-column block bootstrap | `EXPERIMENTAL_BOOTSTRAP`. Each series draws its own indexes. | Always `finite_sample_assumptions_exact` false. Diagnostic of broken shared shocks. |
| Cluster-event bootstrap | `EXPERIMENTAL_BOOTSTRAP`. Unique events are the resampling units, so the independent-event structure is preserved. The percentile interval is not an exact finite-sample confidence interval. | Interval only. Copied rows are not extra trials. Holdout replicates stay at 60, so calibration stays unresolved. |
| Shock-rebuild bootstrap | `EXPERIMENTAL_BOOTSTRAP`. Resampling the known shocks and rebuilding the overlapping windows preserves the shock structure. The percentile interval is not an exact finite-sample confidence interval. | Interval only. Holdout replicates stay at 60, so calibration stays unresolved. |
| Studentized null-centered moving block | `EXPERIMENTAL_BOOTSTRAP`. The statistic uses Newey–West lag 16 and moving block 16. Neither component is an exact finite-sample dependence model, so `finite_sample_assumptions_exact` is false even when both components were predeclared. Plus-one p-value `(1 + exceedances) / (1 + draws)`. | Sixty replicates of 49 draws stay below the validation floor. `valid_p_values_established` is false. The percentile interval is not inverted. |

A constant shared-clock contrast is exactly that constant on every shared-clock draw. The normal standard error stays unavailable.

## Synthetic processes

Series length is 120 unless a row says otherwise. Innovation scale is 1. The generator restarts at the partition master for each scenario.

| Scenario | Process | Dependence classification | Effective sample size |
| --- | --- | --- | --- |
| `independent_zero_edge` | Independent normal, mean 0. | Exact finite horizon 0. | 120 |
| `weak_ar1` | Stationary AR(1), phi 0.3, mean 0. | No exact finite horizon. Autocorrelation floor at lag 2. Autocorrelation continues after that floor. Process class `ASYMPTOTIC_WEAK_DEPENDENCE`. | 64.97237569060773 |
| `strong_ar1` | Stationary AR(1), phi 0.8, mean 0. | No exact finite horizon. Autocorrelation floor at lag 13. Autocorrelation continues after that floor. Process class `ASYMPTOTIC_WEAK_DEPENDENCE`. | 13.84615384615259 |
| `long_memory` | Moving-average of order 23. Weights follow `(k+1)^(-0.6)`, normalized so the lag-0 autocovariance is 1. | Exact finite horizon 23. The simulator is not an infinite long-memory process. | 7.663093882562344 |
| `overlapping_windows` | Mean of each 4 consecutive shocks. | Exact finite horizon 3. | 30.31578947368421 |
| `shared_identical_observations` | 60 independent events. The duplicated target repeats each event twice, in order. | Exact finite horizon 0 on the unique events. Duplicated rows are not an authorized sampling model. | 60 for both targets |
| `common_shock_cross_symbol` | Two series share a factor with weight squared 0.49. The contrast removes the factor. | Exact finite horizon 0. | 120 |
| `multiple_horizons` | The short series is the last shock of each window of 4. The long series is the window average. The contrast is long minus short. | Exact horizon 0 on the short series and 3 on the long series and the contrast. | 120 on the short series, 30.31578947368421 on the long series, unavailable on the contrast |
| `changing_volatility` | Serially independent normal draws that are not identically distributed. Scale 1 on the first half and scale 3 on the second half. | Autocovariance ends at lag 0. The observations are not identically distributed. The sample-variance z interval is not an exact reference. The declared-model interval can still be a known-variance Gaussian oracle. Newey–West and blocks are unverified approximations. | 120 under the average-innovation-variance definition |
| `regime_change` | 60 independent draws, then 60 independent AR(1) draws with phi 0.9. | No exact finite stationary horizon. Process class `UNVERIFIED_APPROXIMATION`. The declared-model interval can still be a known-variance oracle. | Unavailable |
| `planted_positive` / `planted_negative` | Independent normal draws with mean +0.35 or −0.35. | Exact finite horizon 0. | 120 |
| `degenerate_constant` | 120 zeros. | No variance. Unverified for every interval. | Unavailable |

The AR(1) effective sample size is the finite-sample variance-equivalent size `n / [1 + 2 * sum((1 - k/n) * phi**k)]`. The large-sample formula `n * (1 - phi) / (1 + phi)` is a different number. At n = 2 and phi = 0.5 the finite-sample variance of the mean is 1 and the effective sample size is 4/3. Overlapping means of length 2 and horizon 2 have variance 0.375. Episode groups are not trials.

## Holdout realization

The counts below are the Python 3.12.13 realization on this machine for master seed 20261211. Tests recompute each status from the stored numerator and denominator. They do not lock the numerators, because a different libm can change a count. The status rule is what the tests lock.

Holdout partition rows, after separating dependence match from finite-sample reference exactness: 22 `VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL`, 47 `FAILED_SYNTHETIC_CALIBRATION`, 7 `INSUFFICIENT_MONTE_CARLO_PRECISION`, 81 `MODEL_ASSUMPTIONS_UNVERIFIED`. The labels on the same numerators before this classification correction were 30, 47, 7, and 73. Those 30 had followed the earlier move from 40, 47, 46, and 24. Every numerator, denominator, and unavailable count is unchanged across the 284 rows. The status moves are a correction of the already inspected holdout, not a new measurement and not a new independent validation. Every row has catalogue inference `CATALOGUE_INFERENCE_NOT_AUTHORIZED`.

The 22 validated rows are known-variance Gaussian oracles only: `declared_model_z_interval` and `iid_variance_z_interval` where the declared variance matches. The validated sample-estimator list is empty. The validated experimental-bootstrap list is empty. The validated practical-dependence-estimator list is empty. `oracle_pass_validates_a_practical_dependence_estimator` is false. Favorable coverage does not validate a method whose finite-sample reference is not exact.

Eight IID normal intervals left `VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL`. Their coverage stayed inside the two-sided Wilson interval, and the observations on seven of the eight series are independent and identically distributed. The interval still uses the sample variance and a normal z quantile, so it is a sample-estimated approximation. The counts are independent 374/400, unique events 384/400, common-shock primary 381/400, common-shock contrast 378/400, short horizon 374/400, changing volatility 378/400, planted positive 374/400, and planted negative 374/400. Those rows are now `MODEL_ASSUMPTIONS_UNVERIFIED`. The changing-volatility row is also not an identical-distribution sample.

Ten Newey–West rows that the previous rule called validated are now `MODEL_ASSUMPTIONS_UNVERIFIED`. Their coverage was inside the two-sided Wilson interval and was not a clear failure. A fixed Bartlett lag is not an exact finite-sample model, so that coverage is not a validated dependence estimator. The counts are independent lag 1 at 374/400, unique events lag 1 at 382/400 and lag 4 at 376/400, common-shock primary lags 1 and 4 at 378/400, common-shock contrast lag 1 at 377/400 and lag 4 at 372/400, short horizon lag 1 at 375/400, and planted positive and planted negative lag 1 at 374/400. Thirty-nine other previously insufficient Newey–West and block-bootstrap rows moved to `MODEL_ASSUMPTIONS_UNVERIFIED` for the same assumption correction. Their replicate counts were not increased.

The declared-model z interval, which uses the known variance of the mean, covered its true mean on the eligible zero-mean series at 374/400 to 386/400. Its null rejection counts on those series were 14/400 to 26/400. Those oracle rows have `valid_p_values_established` true. That oracle pass is not evidence that a sample autocovariance estimator or a bootstrap has been validated. The same interval on the planted series covered the planted mean at 375/400. Rejecting zero there is a power count, 384/400 for the positive mean and 386/400 for the negative mean, and those p-value rows stay `EXPLORATORY_ONLY`.

Procedures that failed their own numeric check were left at the predeclared lag or block. `FAILED_SYNTHETIC_CALIBRATION` does not require `finite_sample_assumptions_exact`. Unfavorable coverage was not treated as an implementation defect, and no lag or block was retuned from the inspected holdout.

| Series | Method | Coverage | Wilson 95 percent bounds | Status |
| --- | --- | --- | --- | --- |
| Strong AR(1) | Newey–West lag 16 | 325/400 | 0.771344 to 0.847711 | Failed. The lag reaches the autocorrelation floor of 13. Autocorrelation continues. The Bartlett lag does not capture all dependence. |
| Overlapping windows | Newey–West lag 16 | 343/400 | 0.819837 to 0.888362 | Failed. The lag window includes the exact horizon of 3. Bartlett weights are not the exact long-run variance. |
| Unique events, n = 60 | Newey–West lag 16 | 347/400 | 0.830754 to 0.897255 | Failed. A long lag on a short independent series undercovered. The lag is an asymptotic approximation, not an exact model. |
| Strong AR(1) | Moving block 16 | 49/60 | 0.700802 to 0.894422 | Failed. The block reaches the autocorrelation floor and does not contain all dependence. |
| Strong AR(1) | Circular block 16 | 49/60 | 0.700802 to 0.894422 | Failed. The block is an asymptotic device. |
| Overlapping windows | Moving block 4 | 48/60 | 0.682182 to 0.881715 | Failed. The block meets the exact horizon and is still not an exact sampling model. |
| Horizon contrast | Newey–West lags 4, 8, and 16 | 400/400 | 0.990488 to 1 | Failed by overcoverage. The intervals were wide relative to the Monte Carlo standard deviation of the mean, 0.011606, against a lag-16 mean width of 0.121360. |

Ineligible procedures that failed in the expected direction include the IID interval on weak AR(1) at 342/400, strong AR(1) at 186/400, long memory at 133/400, overlapping windows at 266/400, the long horizon at 266/400, regime change at 132/400, and duplicated rows at 340/400. The duplicated-row IID interval uses 120 rows for a process whose effective sample size is 60. The declared-model interval on those duplicated rows covered at 386/400 and remains `MODEL_ASSUMPTIONS_UNVERIFIED`, because a duplicated representation is not an authorized sampling model. Its p-values stay `P_VALUES_UNAVAILABLE`.

Long memory has material horizon 23. No predeclared lag or block is eligible. Newey–West lag 16 covered 285/400 and moving block 16 covered 42/60. Both failed under mismatched assumptions. The declared-model interval covered 374/400 and validated.

Changing volatility covered the declared-model oracle at 378/400, and that oracle stays validated. The same 378/400 count for the sample-variance z interval is now `MODEL_ASSUMPTIONS_UNVERIFIED`: the draws are serially independent and are not identically distributed. The marginal-variance z interval was unavailable on all 400 replicates. Newey–West coverage from 358/400 to 380/400 stayed `MODEL_ASSUMPTIONS_UNVERIFIED`.

Three preserved-resampling rows stay `INSUFFICIENT_MONTE_CARLO_PRECISION`. Moving block length 1 on the independent series covered 56/60. The cluster-event bootstrap covered 58/60. The shock-rebuild bootstrap covered 55/60. `dependence_preserved` is true on each row and `finite_sample_reference_exact` is false. Sixty replicates remain below 200, so the percentile intervals stay unresolved.

Studentized null tests rejected 4/60, 4/60, 5/60, and 3/60 on the independent, weak AR(1), strong AR(1), and overlapping series. Each Wilson interval still reaches both sides of 0.05, and 60 replicates are below 200, so each row stays `INSUFFICIENT_MONTE_CARLO_PRECISION`. `finite_sample_reference_exact` is false because the fixed lag and the fixed block are not an exact finite-sample reference. The p-values were computed. They are not established, and catalogue assessment still returns `P_VALUES_UNAVAILABLE`.

Bootstrap and studentized rows cannot reach `VALIDATED_UNDER_DECLARED_SYNTHETIC_MODEL` in this build. The import-time check requires their replicate counts to stay below 200. Preserving an event or shock structure does not remove that limit.

Stability seeds 20261212 and 20261213, 40 replicates each, stayed `EXPLORATORY_ONLY` and were not pooled. IID coverage rates were 0.925 and 0.95 on the independent series, 0.45 and 0.45 on the strong AR(1), and 0.675 and 0.65 on the overlapping windows. Newey–West lag 16 rates were 0.825 and 0.90, 0.825 and 0.825, and 0.85 and 0.90 on those three series. The span is a seed range. It is not a binomial standard error.

## Multiple testing and selection

The reference family remains 89,460 directional hypotheses per annual segment. A bounded synthetic family does not replace it. Familywise error at 89,460 was not estimated. Holm arithmetic on one vector of 89,460 uniform draws took 0.044332 seconds in this classification correction and estimated no error rate.

Individual p-values in the synthetic families are exact Gaussian tail probabilities at standard error `1/sqrt(120)`. Holm uses the step-down adjusted p-values with the running maximum. The hand example `[0.01, 0.04, 0.03]` adjusts to `[0.03, 0.06, 0.06]`. Holm's theorem says the familywise error is at most alpha when those marginal p-values are valid, under arbitrary dependence. That guarantee is conditional on the p-values. It is not a Monte Carlo result, and `established_by_simulation` stays false. Uncorrected tests and Holm applied only to the selected winner do not receive the guarantee.

The empirical claim is separate. Control requires the one-sided 95 percent Wilson upper bound to be at or below 0.05, together with the precision floor. The inspected holdout was already read under the previous point-estimate rule. Reclassifying those same counts is a correction of that reading. It does not establish a new independent pass. No new familywise experiment was launched.

| Study | Seed | Size | Holm familywise count | One-sided 95 percent upper bound | Holm empirical status | Uncorrected count | Uncorrected status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Calibration, equicorrelated complete null, rho 0.3 | 20261130 | 40 | 1/40 | 0.104589 | Exploratory. Not a validation partition. | 30/40 | Exploratory |
| Holdout, equicorrelated complete null, rho 0.3 | 20261215 | 40 | 17/400 | 0.062392 | Inconclusive. The point estimate 0.0425 is below 0.05 and the upper bound is not. Previously labeled validated. | 286/400 | Failed |
| Holdout, independent complete null | 20261216 | 40 | 19/400 | 0.068238 | Inconclusive. The point estimate 0.0475 is below 0.05 and the upper bound is not. Previously labeled validated. | 348/400 | Failed |
| Holdout, mixed, 36 nulls and 4 alternatives at mean 0.5, rho 0.3 | 20261217 | 40 | 17/400 true-null familywise rejections | 0.062392 | Inconclusive. Same bound as the equicorrelated 17/400 count. Previously labeled validated. | 400/400 | Failed |
| Holdout, independent complete null | 20261222 | 10 | 26/400 | 0.088339 | Inconclusive. Two-sided bounds 0.044740 to 0.093535. The lower bound does not clear 0.05, so this is not excessive error. | 174/400 | Failed |
| Scaling complete null, rho 0.3 | 20261221 | 160 | 4/80 | 0.106799 | Inconclusive. Eighty replicates are below the precision floor. | 78/80 | Failed |

The mixed-family Holm detection count on the four alternatives was 1582/1600. That power row is exploratory and is not an acceptance gate. Winner's-curse inflation is recorded and is not an acceptance gate. Shortlist-only Holm does not control the search that chose the winner.

Four annual segments of 20 complete-null hypotheses, 400 replicates, seed 20261219, selected the same hypothesis in at least two segments on 115/400 replicates. That chance recurrence is exploratory. It is not cross-year confirmation. The mean correlation between two independently drawn segments was 0.01616637208387591. An identical copy of one draw had correlation 1.0. Confirmation p-values for the shared copy and for the independent segments are `P_VALUES_UNAVAILABLE`.

## Integrity and cost

Canonical documents are UTF-8 JSON with sorted keys, compact separators, a trailing newline, and no duplicate keys. `content_sha256` is the SHA-256 of that document with the hash field removed. Wall-clock timings stay outside the hashed document.

`validate_dependence_validation_document` checks canonical bytes, recomputes row statuses from the recorded numerators, recomputes familywise claims from those numerators, and recomputes the dependence class from the scenario, target, and method identity. It checks that authorization flags stay closed. It does not regenerate the 400-replicate experiment. The return value sets `numerical_experiment_regenerated`, `full_monte_carlo_reproduced`, `independently_reproduced_evidence`, and `recomputed_digest_of_altered_counts_is_independent_reproduction` to false. A caller can change a count, recompute a SHA-256 digest, and still receive a structurally consistent document. That digest is not independently reproduced evidence. Labeling the same counts as `newly_established_independent_pass` is rejected. Changing `assumptions_match` and repairing the numeric status to match the flipped flag is rejected, because the class is recomputed from the declared process. Marking this classification correction as a new independent validation is rejected. A validated row must be a known-variance Gaussian oracle. A sample-variance z interval and a preserved percentile bootstrap cannot be labeled finite-sample exact. Changing-volatility rows must record serial independence without identical distribution.

A separate bounded check runs one synthetic family twice: seed 20261230, 4 replications, family size 3, correlation 0. The two numerators must agree. The count is not an acceptance threshold, not the inspected holdout, and not a validation sample. The seed is outside 20261118 through 20261125 and is not 20261211.

One canonical compile on Python 3.12.13 took 18.334 seconds, including that bounded check inside validation. Tracemalloc peak was 9,821,734 bytes. Canonical JSON was 1,270,910 bytes. SHA-256 was `a010913db8697ad6535fb49dae8ed8709d92829811b5d8471d6361c8ccb35ae9`. The previous document, before this classification correction, was SHA-256 `45fc28d57302936bcd6af144081dab8850eee10ba26bb5ab803566f67df1a090` and 1,200,625 bytes. The earlier harness document remains SHA-256 `296cd7113a302a893717cbc1d442efffc487c5169b5ca60568451116ac4b7c59` and 974,640 bytes. The hash changed because classifications and statuses changed. The synthetic numerators did not.

Holm arithmetic on one random p-value vector, measured outside the document, took 0.044332 seconds at 89,460 hypotheses and estimated no familywise error. That timing is not an error-rate estimate. The earlier timing of 0.035565 seconds was the same non-estimate on the previous document.

Focused `tests.test_annual_pattern_catalogue_dependence_validation` was 12 tests and exited 0 in 25.514 seconds. Neighboring statistical-uncertainty, event-evidence, protocol, miner, cross-year, and segment-evidence tests were 82 tests and exited 0 in 42.588 seconds.

## Authorization

Historical artifact reads, protected-year research, annual catalogue execution, authentic historical statistical results, DEC-470 retuning, research-gate retuning, pattern promotion, Strategy V1 synthesis, workflow activation, DEC-629, DEC-630, annual run 385, broker mutation, demo orders, and live trading stay closed. No trading or statistical promotion authorization is granted.

## Experiment

`EXP-20261119-074` records the original synthetic harness. `EXP-20261120-075` records the interpretation correction: the one-sided familywise bound, the separation of exact, truncated, asymptotic, and unverified dependence, and the separation of oracles from sample estimators. `EXP-20261120-076` records this classification correction: a sample-variance z interval is not a finite-sample exact reference, a preserved percentile bootstrap is not an exact confidence interval, and changing-volatility observations are not identically distributed. No decision-log number is assigned. The milestone does not change V1 instruments, the cost constraint, canonical granularity, testing gates, risk limits, real-money rules, or phase order. None of these experiments authorizes a merge. The inspected holdout is not a new independent confirmation of the revised classification.
