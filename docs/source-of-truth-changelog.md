# FMP Source-of-Truth Changelog

## 2026-08-22 — V1 baseline

- Froze forex-only V1 scope.
- Froze EUR/USD, GBP/USD, USD/JPY initial universe.
- Froze $0 development constraint.
- Froze canonical 1-minute bid/ask architecture and derived 5m/15m/1h bars.
- Defined phase order from data acquisition through optional live execution.
- Moved backtester ahead of baseline strategy research.
- Defined anti-leakage, experiment, promotion, risk, and change-control rules.
- Initialized GitHub repo identity as `Dtwosam/FMP`.


## 2026-09-22 — Phase 8A portfolio-research pivot

- Approved DEC-039 and `docs/superpowers/specs/2026-09-22-phase8a-portfolio-research-redesign.md`.
- Stopped EXP-20260922-011 before campaign registration; preserved its successful connector qualification and historical-reference artifacts as non-scored evidence.
- Split Phase 8 into 8A multi-pair/multi-strategy portfolio research and 8B multi-strategy live shadow.
- Reaffirmed the V1 universe as exactly EURUSD, GBPUSD, and USDJPY and required reuse of all accepted Dukascopy histories.
- Added immutable strategy-version and champion/challenger architecture with no hot-swapping into an active campaign.
- Clarified that 2024-01-01 through 2026-08-20 is no longer untouched for new post-Phase-7 strategies because Phase 7 already opened it.
- Added portfolio-level reporting, correlated USD exposure analysis, daily-return distribution reporting, and explicit high-return aspiration measurement without making 10% daily a guaranteed pass rule.
- Kept Phase 9 demo, broker mutation, live orders, and real-money execution locked.


## 2026-09-22 — DEC-042 frozen portfolio selection

- Added `docs/superpowers/specs/2026-09-22-phase8a-portfolio-selection.md`.
- Opened `EXP-20260922-014` for implementation of the frozen selection machinery.
- Limited the eligible strategy pool to already qualified immutable strategy versions and blocked `DISCOVERY`, `CHALLENGER`, and `RETIRED` records.
- Frozen pool size: 2 to 12 strategies; portfolio-set size: 1 to 6, with single-strategy sets retained only as controls.
- Frozen retrospective selection range: 2019-01-01 inclusive through 2026-08-21 exclusive.
- Frozen mandatory 0.2/0.5-pip profitability, expectancy, profit-factor, drawdown, trade-count, yearly-stability, concentration, and diversity gates.
- Frozen deterministic lexicographic ranking order; no post-result weights or threshold changes are permitted.
- Confirmed the current historical inventory has only one eligible strategy, so combination search remains blocked pending a separately predeclared challenger-discovery/qualification experiment.
- Phase 8B, demo orders, broker mutation, live orders, and real-money trading remain locked.


## 2026-09-22 — Phase 8A identity correction

- The repository already assigned `DEC-041` / `EXP-20260922-013` to the predeclared `opening_range_momentum` Challenger Round 1 before the portfolio-selection work was merged.
- A later portfolio-selection commit accidentally reused those identifiers. No portfolio combination search, ranking result, or benchmark was executed under the duplicate identity.
- Portfolio selection is corrected to `DEC-042` / `EXP-20260922-014`.
- The six-family rule-based challenger-discovery protocol is corrected to `DEC-043` / `EXP-20260922-015`.
- No EXP-015 Stage A/B/C historical run occurred before this correction.
- Original `DEC-041` / `EXP-20260922-013` opening-range-momentum evidence identity remains unchanged.

## 2026-09-27 — DEC-268 discovery-first research and iterative demo learning

- Changed future strategy discovery from a required six-family/baseline-first path to discovery-first analysis of repeated market behaviour.
- Preserved all six historical rule families and prior experiments as immutable benchmarks/evidence; they are no longer the required or complete strategy universe.
- Required bounded discovery protocols with frozen data ranges, measurements/features, future-outcome labels, minimum support, search budget, multiple-comparison/search-volume accounting, candidate-freeze rules, and later chronological validation.
- Required discovered patterns to become immutable strategy/model versions before later evaluation.
- Formalized demo as an iterative learning source: completed demo evidence may create a new challenger, but data used for tuning cannot also validate that revised version; every material revision requires a fresh later prospective window.
- Preserved immutable active campaigns and prohibited self-modification/hot-swapping.
- Recorded the already-consumed EXP-015 Stage A run as historical evidence only; no retry/replacement or automatic Stage B/C continuation is authorized.
- Kept Phase 8B, demo orders, broker mutation, live orders, real-money trading, and Phase 11 locked behind their existing gates.

## 2026-09-27 — DEC-270 EXP-061 bounded discovery-first protocol

- Opened EXP-20260927-061 as the first concrete DEC-268 discovery-first market-state pattern experiment.
- Frozen 18 EURUSD/GBPUSD/USDJPY × 5m/15m/1h × 60m/240m cells.
- Frozen exactly 20 leakage-safe continuous state dimensions plus one deterministic session dimension.
- Bounded patterns to one or two predicates, at most 74,700 LONG/SHORT directional hypotheses globally.
- Frozen chronology to 2015-2017 discovery, 2018 confirmation, 2019-2022 validation, while keeping 2023-2026 closed to EXP-061.
- Added hard 180-pattern confirmation and 54-pattern validation caps with immutable discovery ranking and near-duplicate removal.
- Defined economic/support gates using 0.5-pip primary and 1.0-pip stress outcomes.
- Kept source access, result execution, candidate compilation, reserved-block access, Phase 8B, demo, broker/live, real-money, and trading locked.

## 2026-09-27 — DEC-271 EXP-061 deterministic in-memory miner core

- Implemented strict in-memory feature/outcome row contracts for EXP-061.
- Implemented discovery-window-only state calibration and bounded one/two-dimension pattern enumeration.
- Implemented frozen discovery support/economic gates, ranking, and Jaccard near-duplicate removal.
- Implemented 2018 pass/fail confirmation preserving discovery rank and at most three frozen hypotheses per cell/horizon.
- Implemented frozen 2019-2022 validation with no retuning.
- Added synthetic end-to-end tests, including proof that catastrophic 2023 rows cannot alter EXP-061 output.
- Kept historical source access/result execution, 2023-2026 reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.

## 2026-09-27 — DEC-272 EXP-061 market-learning adapter/evidence

- Reused existing EXP-044 market-learning feature/outcome schemas as DEC-271 inputs.
- Added deterministic feature/outcome observation identity and exact processed-manifest matching.
- Restricted adapter input to 2015-2022 and rejected any outcome target reaching reserved 2023+ history.
- Added canonical tamper-detectable per-cell evidence for discovery, confirmation, and validation results.
- Added focused tests for valid adaptation, reserved-history rejection, source-identity mismatch, evidence determinism, tamper detection, and all execution/trading locks.
- Kept artifact loading, historical result execution, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.

## 2026-09-27 — DEC-273 EXP-061 verified range-limited loader

- Added exact aggregate-evidence fingerprint and requested-cell manifest verification for EXP-061 source inputs.
- Selected exactly 96 monthly feature and outcome partitions per pair/timeframe: 2015-01 through 2022-12.
- Prevented selection/opening of 2023+ monthly partitions and filtered any late-2022 target whose exit reaches 2023 before adaptation.
- Verified selected current artifact paths, sizes, SHA-256 digests, schemas, and row counts.
- Bound feature/outcome evidence, feature/outcome manifests, and Phase 2 processed-manifest identity end to end.
- Kept historical discovery/result execution, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.

## 2026-09-27 — DEC-274 EXP-061 non-executing run contract

- Frozen exact future workflow identity, manual-main attempt-1 semantics, and explicit 18-cell inventory.
- Frozen 20 unambiguous job names and 20 commit-scoped artifact names.
- Added deterministic 18-cell aggregate-evidence compiler and independent aggregate validator.
- Required exact Phase 2 sources, exact cell manifest identities, singular feature/outcome aggregate evidence identities, and cross-horizon manifest consistency.
- Added global 180 discovery-shortlist / 54 frozen / 54 accepted caps and exact count reconciliation.
- Frozen non-success semantics to no rerun/retry/replacement by default.
- Kept workflow source/dispatch, historical result execution, reserved 2023-2026 data, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.

## 2026-09-27 — DEC-275 EXP-061 dormant workflow/CLI source

- Frozen the future EXP-061 workflow text outside the active GitHub Actions directory.
- Pinned exact accepted EXP-044 feature/outcome run identities plus 9+9 cell artifacts and aggregate evidence artifacts.
- Preserved explicit DEC-274 runtime cell names through an 18-entry matrix with an explicit job-name expression.
- Added a locked CLI with source-preflight, status, cell, and aggregate interfaces.
- Required the execution gate before any historical artifact/evidence read in cell and aggregate paths.
- Pinned Python 3.12.14 and Polars 1.44.2 runtime.
- Added regression tests proving the active workflow path is absent and all execution/trading authorities remain false.
- Kept workflow installation/dispatch, historical discovery/result execution, reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.

## 2026-09-27 — DEC-276 EXP-061 guarded workflow installation

- Installed the exact reviewed DEC-275 EXP-061 workflow bytes at the reserved active GitHub Actions path.
- Required active and dormant workflow sources to be byte-for-byte identical at blob `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`.
- Preserved the closed historical execution gate before all cell/result-producing work.
- Distinguished workflow presence from dispatch/result authorization.
- Added install-contract and regression tests proving byte identity, gate ordering, and continued execution/trading locks.
- Consumed no EXP-061 historical run slot.
- Kept dispatch, historical discovery/result execution, reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading unauthorized.
