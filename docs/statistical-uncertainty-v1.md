# Statistical uncertainty V1

**Status:** source-only infrastructure. Synthetic observations only.
**Governing method:** discovery-first annual pattern catalogue research under DEC-469 / DEC-268.
**Pattern tool:** `statistical-uncertainty-v1`.
**Protocol:** `fmp-annual-pattern-catalogue-statistical-uncertainty-v1`.
**Parent contracts:** DEC-470 and event-level evidence V1, both unchanged.

This tool asks how uncertainty changes when outcome windows overlap, when outcomes are serially dependent, and when a frozen family of 89,460 directional hypotheses is searched together. It does not estimate that uncertainty for a historical catalogue. Event-evidence inference stays unavailable. Exploratory intervals live only in a predeclared synthetic harness, and that harness does not claim calibrated error control.

## What stays unavailable on event evidence

A validated event document supplies descriptive counts: raw directional support, unique events, overlapping pairs, and overlap-connected episode groups. The assessment copies those counts and does not turn them into a sampling distribution.

| Quantity | Status on event evidence |
| --- | --- |
| Raw observation support | Descriptive count |
| Unique physical events | Descriptive count |
| Overlap-connected episode groups | Descriptive count. Not an independent-trial count. |
| Serial dependence beyond geometric overlap | Unavailable. The overlap graph is not an autocovariance. |
| Dependence across horizons, symbols, and timeframes | Unavailable. The event contract records those channels as unmeasured. |
| Effective sample size | Unavailable. It is not identified from the overlap counts. |
| Sampling uncertainty of the mean | Unavailable. No standard error or interval is attached. |
| Multiple-hypothesis and selection uncertainty | Not applied. Individual p-values are unavailable. |

The unweighted mean of supplied base nets is reported as a descriptive sample mean. It is not a realizable portfolio profit. Overlapping signals are not treated as simultaneously executable independent trades.

Episode-group counts are never written into the effective-sample-size field. Asking the assessment to assume independence, or to treat episode groups as trials, fails closed.

Caller-supplied pattern membership stays an assertion. It is not feature-state proof. Event ids are not recovered from an annual `event_fingerprint`. The cross-year engine's `p_values`, `independent_trial_standard_errors`, and `multiple_comparison_adjustment` remain `UNAVAILABLE_NOT_COMPUTED`. This module does not import that engine and does not change its contract.

## Exploratory methods

The calibration harness is labeled `EXPLORATORY_NOT_INFERENCE`. None of the methods were chosen because they covered a nominal rate, and none were fit to EXP-20261118-069. That experiment, including 4,922 correlated zero-gross passes at 8 pips on seed 20261120, stays historical context. Its seeds 20261118, 20261119, and 20261120 are refused as tuning seeds. The harness uses 20261121, 20261122, 20261123, and a separate Holm seed 20261124.

Each scenario restarts at the primary seed. Scenarios that consume the same normal draws therefore share a noise path. That is a paired comparison, not extra independent evidence. Variability across the three seeds is a separate stream. It is not pooled into the Monte Carlo denominator, and the seed range is not a binomial standard error.

| Method | What it assumes | How it fails |
| --- | --- | --- |
| IID normal interval | Independent, approximately normal observations; sample variance uses `n - 1`; the 95 percent quantile is the fixed normal value 1.959963984540054. | Overlap, serial correlation, and stacked copies of one shock make the interval too narrow. A constant sample has no variance. The interval is not a portfolio profit and not a p-value. |
| Newey-West, Bartlett kernel | Covariance stationarity and weak dependence. Lags 1, 4, and 8 are predeclared. Autocovariances divide by `n`. | A short lag misses dependence. A long lag is noisy in a short sample. A non-positive long-run variance is unavailable, not clipped to zero. A univariate lag does not carry another symbol or horizon. |
| Moving-block bootstrap | Dependence is mostly inside a block. Lengths 1, 4, and 8 are predeclared. The interval is a percentile of 99 draw means. | Block length 1 resamples adjacent outcomes independently and is an incorrect-assumption diagnostic, not a recommended estimator. The percentile interval is coarse. It is not treated as a valid p-value. |
| Shared-clock block bootstrap | Caller-supplied numeric series. A validated `synthetic-clock-` id means one index block is applied to every series. Equal length is not timestamp alignment. | Independent column resampling gives those series different indexes and breaks a common shock. Market timestamps and authentic event timelines are refused. The shared clock still does not create a p-value or a scalar effective sample size. |
| Holm step-down | Used only when individual p-values are declared valid for a known-sigma Gaussian synthetic complete null, including a correlated null whose marginal p-values stay valid. | Bootstrap and catalogue sources are refused. A caller declaration is not market evidence. Holm on a shortlist would not control the search that produced the shortlist. The bounded check does not control the catalogue or selection across years. |

The estimand throughout is the mean of a synthetic net-pip series. It is not a claim about simultaneously holding overlapping positions.

## Effective sample size

Effective sample size is reported only when the scenario itself states the dependence model. Neither AR(1) expression below is an effective sample size for authentic event evidence. Event evidence still has to supply a justified dependence model before either expression can be used, and this contract does not supply that model.

- Declared independent draws: the sample size is `n`. This is not an event-evidence result.
- Declared stationary AR(1) with known phi. Phi is the scenario constant 0.8. It is not estimated from the sample.
  - Finite-sample variance-equivalent size: `n / [1 + 2 * sum((1 - k/n) * phi**k for k in 1..n-1)]`. This is the number of independent draws, with the same marginal variance, that matches the exact finite-sample variance of the mean when the autocorrelation at lag k is `phi**k`.
  - Large-sample approximation: `n * (1 - phi) / (1 + phi)`. This replaces the finite-sample weights with an infinite sum. It is not the exact finite-sample variance of the mean.
  - The reported scenario value is the finite-sample expression. The approximation is stored beside it and is not used as that value. The two expressions are not interchangeable. At phi 0.8 their absolute gap stays near one half of an observation from n = 80 through n = 2,000, while the relative gap shrinks.
- Declared shared-event copies: the sample size is the event count, not the doubled hypothesis-row count.
- Overlapping horizons, common shocks, and event-evidence overlap counts: unavailable. Overlap counts do not justify either AR(1) formula.
- Constant outcomes: degenerate variance. No precision is invented.

## Monte Carlo uncertainty

Every coverage rate and every rejection rate records its numerator and denominator. The denominator is the number of available intervals. Unavailable intervals stay out of that denominator, and their count is recorded separately. A zero denominator leaves the interval unavailable.

The interval is a 95 percent Wilson score interval. The normal quantile is the same fixed value used by the exploratory normal intervals, 1.959963984540054. The binomial standard error is `sqrt(rate * (1 - rate) / denominator)`. That standard error is zero when the rate is zero or one, so the Wilson interval is the reported interval.

Empirical coverage from 160 closed-form replications is not an exact population error rate. The 20 bootstrap replications do not establish calibrated confidence intervals. The bootstrap calibration conclusion is unresolved. Seed-to-seed ranges are a different record from this Monte Carlo uncertainty.

## Multiple testing

The relevant family for one annual segment is the frozen 89,460 directional hypotheses, not a shortlist of winners. That count is the frozen per-segment search universe. It is not proof that multiple testing or selection across years has been controlled. Holm is not applied to that family because no valid individual p-values exist. Dependence-preserving resampling is not assumed to produce them. Selection bias stays unavailable. No real catalogue p-value, statistical promotion, or Strategy V1 significance claim is authorized.

A separate method check draws 40 known-sigma Gaussian hypotheses under a complete null and applies Holm at alpha 0.05. One stream is independent. A second stream adds a shared shock while keeping the marginal variance at 1, so the marginal p-values stay valid under that synthetic process. That family is not the annual universe. The check can show that Holm rejects fewer complete-null families than the uncorrected tests under its own assumptions. One hundred sixty replications do not establish a calibrated familywise error rate, so that calibration conclusion is unresolved. The check does not control the catalogue or selection across years.

Full-universe Holm arithmetic would be cheap. The reason it is not run is scientific, not computational. The harness does not simulate 89,460 series.

## Synthetic scenarios

Closed-form intervals use 160 replications. Block resampling uses 20 replications and 99 draws, and it runs only on the dependence scenarios. The generator is Box-Muller on `random.Random`. Direct series longer than 2,000 values are rejected. The longest predeclared series has 240 values.

| Scenario | Data-generating process |
| --- | --- |
| `zero_edge_independent` | 80 independent normal draws, mean 0. |
| `negative_after_cost` | Those draws minus a synthetic 0.5 pip shift. The shift is not a broker model. |
| `planted_positive_edge` | Independent normal draws with mean 0.4. |
| `serial_correlated_noise` | Stationary AR(1), phi 0.8, mean 0. |
| `shared_event_membership` | Two hypotheses copy one independent event series. |
| `overlapping_horizons` | A short series and a 4-observation overlapping average of the same shocks. |
| `common_shock_cross_symbol` | Two series share one shock plus their own noise. |
| `sparse_support` | 12 independent draws. |
| `dense_support` | 240 independent draws. |
| `degenerate_constant_outcomes` | 20 zeros. |

Diagnostics are coverage of the known mean, the rate at which an interval excludes zero, the rate at which an interval lies entirely above zero, interval width, and the mean of the sample means. A replication with a non-positive long-run variance or a zero sample variance does not enter the coverage denominator. Constant outcomes have no coverage to compute.

The same three seeds also rerun the zero-edge dependence scenarios: serially correlated observations, shared-event copies, overlapping outcomes, and common-shock cross-symbol observations. Those rows record coverage and false-exclusion rates for the IID interval, the predeclared Newey-West lags, the predeclared moving-block lengths, the shared-clock resample, and the incorrect independent-column resample. The primary-seed row is the primary calibration row. No lag, block length, method, or threshold is chosen from the observed coverage.

These rates describe the exploratory methods under the stated synthetic processes. They are not a claim that FMP has calibrated error control for the annual catalogue.

## Scaling and integrity

Canonical documents are UTF-8 JSON with sorted keys, compact separators, a trailing newline, and no duplicate keys. `content_sha256` is the SHA-256 of that document with the hash field removed. Validation recomputes the document. An assessment cannot be validated without the event document that produced it, and the event hash must match. Provenance requires a source label, a 40-character commit, and a 64-character manifest digest.

Historical reads, catalogue execution, cross-year result production, Strategy V1 synthesis, statistical promotion, candidate compilation, workflow activation, DEC-629, DEC-630, annual run 385, and trading stay closed.

## Experiment

`EXP-20261119-072` records the synthetic harness. `EXP-20261119-073` records the pre-merge hardening of finite-sample AR(1) reporting, Monte Carlo intervals, dependence-scenario seed variability, the synthetic clock contract, and the correlated-null Holm check. Neither experiment authorizes a merge, a historical read, or a change to DEC-470.
