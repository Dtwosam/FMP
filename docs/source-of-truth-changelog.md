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

## 2026-09-27 — DEC-276 EXP-061 locked workflow installation

- Installed the reviewed DEC-275 workflow byte-for-byte at the reserved active GitHub Actions path.
- Frozen active and dormant workflow blob identity to `d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9`.
- Added repository validation that active and dormant workflow bytes remain identical.
- Kept ordinary dispatch, proof dispatch, historical-result dispatch, historical discovery/result execution, rerun/retry/replacement, reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.
- Preserved fail-closed gate ordering before any historical cell artifact download or aggregate evidence read.

## 2026-09-27 — DEC-277 EXP-061 gate-proof contract

- Frozen proof-only terminal semantics without authorizing a dispatch.
- Required manual-main attempt-1 workflow identity and fail-closed preflight conclusion.
- Required every materialized downstream job to be skipped while allowing GitHub to elide skipped matrix children.
- Allowed exactly one preflight artifact and forbade all cell/aggregate result artifacts.
- Required exact DEC-275 preflight source fingerprint and workflow-source payload.
- Kept the future historical-result slot unconsumed and all historical/result/trading permissions false.

## 2026-09-27 — DEC-278 EXP-061 read-only proof operator

- Added a read-only proof planner with no execute mode.
- Required exact caller-supplied main-head binding.
- Exposed one planned manual-main proof command only while no matching run exists.
- Removed the command and routed to review once any matching manual-main run exists.
- Kept proof dispatch, historical result execution, reserved-block access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.

## 2026-09-27 — DEC-279 EXP-061 one-shot proof-only executor

- Added a one-shot merged-main executor for exactly one EXP-061 proof dispatch.
- Required two identical fresh DEC-278 plans, exact current-main binding, and zero prior target proof runs.
- Pinned the active locked workflow and DEC-275/277/278/279 source identities before any GitHub write.
- Authorized only proof dispatch; historical-result dispatch/execution and the historical-result slot remain locked.
- Refused executor reruns and proof retry/replacement; no discovery-cell/aggregate execution command exists in the executor surface.
- Deferred all proof-result interpretation to DEC-277/DEC-280 terminal review.


## 2026-09-27 — DEC-280 EXP-061 reviewed gate-proof freeze

- Frozen successful DEC-279 executor run `36319870713` and sole proof run `36319888985` at merged main `041b7b2f5aac8821156fab346df8ab30f4be2a7b`.
- Verified the proof failed only at the separately-authorized execution gate after source preflight succeeded.
- Bound the exact three materialized jobs: failed preflight, skipped unexpanded matrix placeholder, and skipped aggregate.
- Recorded the DEC-277 reviewer/API compatibility edge without rewriting the predeclared proof contract or rerunning the proof.
- Bound sole preflight artifact `10932485842` and digest `sha256:0dfbf4c76874bb2b056a835ff0d7fdf2199ddda279e40a60924128a7ff29573d`.
- Revalidated the DEC-275 source fingerprint, exact workflow-source payload, accepted EXP-044 source identities, and nine pair/timeframe source bindings.
- Confirmed zero historical cell/aggregate result artifacts and no historical discovery execution.
- Kept proof rerun/retry/replacement, historical-result dispatch/execution, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-281 EXP-061 historical-run authorization

- Frozen a source-only one-slot contract for the future EXP-061 historical discovery-result attempt.
- Verified the exact manual-main EXP-061 inventory contains only frozen proof run `36319888985`.
- Excluded exactly that proof run from historical-result slot consumption.
- Declared the first later non-proof manual-main attempt to consume the slot immediately, regardless of terminal outcome.
- Rejected second historical attempts and any `run_attempt != 1` rerun.
- Bound the unchanged DEC-270 through DEC-280 discovery/proof/workflow source stack and exact current workflow/CLI/runtime blobs.
- Opened only the source-governance slot; historical dispatch/execution, result production, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading remain locked.


## 2026-09-27 — DEC-282 EXP-061 read-only historical operator

- Added an exact-main read-only planner for the single DEC-281 historical-result slot.
- Required the frozen DEC-280 proof run to remain intact and the caller-supplied expected main head to equal current main.
- Exposed the sole future `gh workflow run phase8a-exp061-discovery.yml --ref main` command only while no historical-result attempt exists.
- Removed the command and routed to review once any later historical-result run is present.
- Added no execute, advance, rerun, retry, or replacement mode.
- Kept historical dispatch/execution, discovery-result production, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-283 EXP-061 historical plan proof

- Added a repository-hosted, push-to-main, read-only proof for the exact DEC-282 historical-slot plan.
- Pinned the DEC-280 reviewed proof, DEC-281 historical authorization, DEC-282 operator/CLI, active locked EXP-061 workflow, and pinned runtime identities.
- Required exact merged-main checkout, current-main binding, and a clean worktree after non-editable dependency installation.
- Read current main and EXP-061 run inventory through read-only GitHub API calls.
- Invoked only the DEC-282 `plan` command and required the frozen proof run to be the sole prior manual-main EXP-061 run.
- Required zero historical-result attempts, an unconsumed slot, and the exact future dispatch command as plan evidence only.
- Uploaded only one immutable historical-plan artifact.
- Kept historical dispatch/execution, result production, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-284 EXP-061 reviewed historical plan proof

- Frozen successful merged-main DEC-283 proof run `36323674455` at head `7fd3a9e878bf2760850037548e93dc1e8173c0c1`.
- Bound the sole non-expired plan artifact `10932743232` and digest `sha256:a71585da8c7e858d7ed309cf52965c5a0fbb7ef42b65e28a18933792eeb9460a`.
- Independently verified the downloaded artifact ZIP against the same SHA-256 digest.
- Bound the exact raw and canonical `historical-plan.json` SHA-256 identities.
- Verified the plan reports DEC-282/DEC-281, exact frozen proof run `36319888985`, zero historical-result attempts, and an unconsumed historical-result slot.
- Preserved the future workflow command as evidence only; no dispatch or execution authority was added.
- Kept rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-285 EXP-061 historical execution authorization

- Added a new runtime authorization layer without modifying the frozen DEC-275 workflow-source module or the active workflow YAML.
- Routed the public EXP-061 CLI execution gate through DEC-285 and recorded DEC-285 authorization in preflight evidence.
- Bound reviewed DEC-284 source plus the unchanged protocol/miner/adapter/loader/run-contract/workflow/runtime identities.
- Confirmed the old proof is workflow run number 1 / attempt 1 and authorized historical runtime only for workflow run number 2 / attempt 1.
- Required exact repository, workflow, event, main ref, runtime SHA, and distinct positive run-id identity.
- Rejected run number 1, run number 3+, any rerun attempt, proof-run id reuse, and proof-head reuse.
- Authorized historical discovery/result production only inside that exact runtime identity while keeping workflow dispatch false.
- Kept retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.
- Recorded DEC-281 current-source validation as intentionally superseded by the activated CLI while preserving DEC-281 run-inventory semantics.


## 2026-09-27 — DEC-286 EXP-061 historical execution operator

- Added a read-only exact-main operator for the DEC-285 one-shot historical runtime.
- Required the frozen proof to remain workflow run number 1 / attempt 1.
- Frozen the only future target identity as workflow run number 2 / attempt 1.
- Exposed the single future `gh workflow run phase8a-exp061-discovery.yml --ref main` command only while the historical slot is empty.
- Removed the command and routed to review once the run #2 historical attempt is present.
- Rejected proof-run-number drift, run number 3+, reruns, second historical attempts, and main-head drift.
- Added no execute, dispatch, retry, rerun, or replacement mode.
- Kept reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-287 EXP-061 historical execution plan proof

- Added a repository-hosted, push-to-main, read-only proof for the exact DEC-286 run-#2 execution plan.
- Pinned DEC-284 reviewed-plan, DEC-285 runtime authorization, DEC-286 operator/CLI, activated EXP-061 CLI, active discovery workflow, and pinned runtime identities.
- Required exact merged-main checkout and a clean worktree after non-editable dependency installation.
- Read current main and workflow-dispatch inventory through read-only GitHub API calls.
- Invoked only the DEC-286 `plan` command.
- Required proof run `36319888985` to remain workflow run #1, zero historical-result attempts, and target run #2 / attempt #1.
- Persisted only one immutable historical execution-plan artifact.
- Added no dispatch or execute path and kept retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-288 EXP-061 reviewed historical execution plan proof

- Frozen successful merged-main DEC-287 proof run `36329787371` at head `958a0b830bb867d1c11e2a82be7fc301a6a75474`.
- Bound the sole non-expired execution-plan artifact `10935233025` and digest `sha256:bb81bd8f0cb1adfc0054db4f5c16f13808793c520d443a0f05a89a90f92a415d`.
- Independently verified the downloaded artifact ZIP against the same SHA-256 digest.
- Bound raw `historical-execution-plan.json` SHA-256 `2ca76921e17096b444202573a950825244e07c27e0f476cecfb510ad5e0a95e5` and canonical SHA-256 `86b37433e183bfd9199822da0212b79fe11950461206335fc53e6f783210a74e`.
- Verified the plan reports DEC-286/DEC-285, fail-closed proof run `36319888985` as workflow run #1, zero historical-result attempts, and an unconsumed slot.
- Frozen the only future target as workflow run #2 / attempt #1.
- Preserved the future workflow command as evidence only; historical-result dispatch and execute mode remain false.
- Kept rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.
