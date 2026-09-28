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


## 2026-09-27 — DEC-289 EXP-061 historical one-shot executor

- Added a one-shot merged-main executor for the sole EXP-061 historical-result attempt.
- Re-downloads DEC-287 artifact `10935233025` at runtime, verifies ZIP/raw/canonical plan hashes, and re-runs the DEC-288 reviewed-proof freeze before any write.
- Requires two identical fresh DEC-286 live plans immediately before dispatch.
- Requires the live discovery inventory to contain only proof run `36319888985` as workflow run #1 / attempt 1.
- Authorizes exactly one `phase8a-exp061-discovery.yml` manual-main dispatch, expected to become workflow run #2 / attempt 1.
- Requires the DEC-289 executor itself to be the first and only main-push executor run and rejects executor reruns.
- After dispatch, verifies exactly one non-proof run exists and that it is run #2 / attempt 1 at the executor merged-main head.
- Treats the new historical run as consuming the sole slot immediately, regardless of later terminal outcome.
- Adds no historical rerun/retry/replacement path.
- Keeps reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-290 EXP-061 historical terminal review contract

- Predeclared terminal review for the sole EXP-061 historical run #2 before the result exists.
- Required exact manual-main workflow identity, run number 2, attempt 1, terminal completion, and exact executor head binding.
- Required exact 20-job / 20-artifact DEC-274 inventory for any successful run.
- Classified any terminal non-success as slot-consuming and permanently closed to rerun/retry/replacement.
- Allowed the exact skipped unexpanded GitHub matrix-template placeholder only in a non-success fail-closed shape and never alongside expanded cell jobs.
- Kept candidate compilation, promotion, reserved 2023-2026 access, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-292 EXP-061 historical failure freeze

- Frozen one-shot executor run `36335739823` and sole historical run `36335879839` at merged head `a7b3bc2d0b196da2631b64c19331efb3af12c98e`.
- Verified run #2 / attempt 1 is terminal failure and consumes the historical slot permanently.
- Bound executor artifact `10936194549` / digest `sha256:e7ffe1f08ce358eca210ef41397165196cb64bee31696a180c7fd02af8c68f1c`.
- Bound sole run artifact `10937316246` / digest `sha256:e9a898df51317250944ad0a111d01d96d2081d708ea80872ed11b5cee48d356f`.
- Recorded exact terminal shape: preflight success, 18 cell failures, aggregate skipped, zero cell/aggregate result artifacts.
- Diagnosed representative cross-pair failures as non-finite Phase-5 warm-up feature values reaching `FeatureObservation` without NaN-to-null normalization.
- Classified the defect as `NONFINITE_FEATURE_WARMUP_NOT_NORMALIZED`, not a negative market-pattern result.
- Closed EXP-061 with no rerun/retry/replacement and required a new experiment identity for repair.
- Kept reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-293 EXP-062 non-finite feature normalization repair

- Opened EXP-062 as a new identity; did not retry closed EXP-061.
- Preserved DEC-270 discovery/confirmation/validation/search semantics and exact historical date boundaries.
- Repaired only the market-learning adapter representation boundary.
- Converted numeric NaN/+inf/-inf continuous feature values to `None` in accordance with the frozen Phase-5 feature dictionary.
- Preserved existing nulls and finite values unchanged.
- Kept session flags strict booleans and outcome values strict finite numbers.
- Added no imputation, forward/backfill, clipping, zero-fill, or feature invention.
- Added focused regression tests for NaN, infinities, existing null, finite preservation, session strictness, and invalid non-numeric input.
- Opened no historical execution slot.
- Kept reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, and trading locked.


## 2026-09-27 — DEC-294 EXP-062 real-data adapter proof

- Added a push-to-main, read-only nine-cell proof against the exact accepted EXP-044 feature/outcome artifacts.
- Preserved the frozen EXP-061 adapter byte-for-byte and proved the isolated EXP-062 repair module instead.
- Reused the DEC-273 loader to open only 2015-2022 and require exactly 96 feature + 96 outcome monthly partitions per pair/timeframe.
- Counted raw numeric non-finite values across all 20 continuous features before adaptation.
- Required full repaired EXP-062 adaptation with exact feature/outcome row parity.
- Required the aggregate proof to contain all nine pair/timeframe cells and to observe at least one real non-finite value.
- Kept probe output outside the checkout and required the source worktree to remain clean.
- Added no miner call, historical result production, dispatch, reserved-data access, candidate compilation, promotion, Phase 8B, demo, broker/live, real-money, or trading authority.


## 2026-09-27 — DEC-295 EXP-062 adapter proof review contract

- Predeclared DEC-294 proof review before the real-data probe result exists.
- Required exact push-main attempt-1 workflow identity.
- Required all nine adapter-probe jobs plus aggregate to succeed for a valid success.
- Required exactly nine cell artifacts plus one aggregate artifact, all non-expired and commit-scoped.
- Rejected unexpected jobs/artifacts.
- Bound the clean DEC-294 workflow blob `4fbeb7836ef775b14918b49ed24da8c86928610c`.
- Kept all historical discovery/result, reserved-data, candidate, demo/live, real-money, and trading authorities locked.


## 2026-09-27 — DEC-296 EXP-062 adapter proof content review

- Predeclared content-level review for a successful DEC-294 proof before proof artifacts exist.
- Required the DEC-295 success-complete terminal shape.
- Required exactly nine validated pair/timeframe probe objects at one proof head.
- Deterministically recompiled the aggregate and required exact equality with persisted aggregate content.
- Reconciled total raw non-finite counts by continuous feature and cell.
- Defined successful meaning as adapter-repair verification only, with no mining or strategy/candidate claim.
- Kept historical discovery/result, reserved-data, candidate, promotion, Phase 8B, demo/live, real-money, and trading authorities locked.


## 2026-09-27 — DEC-297 EXP-062 adapter proof result freeze

- Frozen successful merged-main DEC-294 proof run `36348366166` at head `5e235938dc7e8eb467f59ca85ae4b6e1d5179475`.
- Verified exact 10-job / 10-artifact DEC-295 success shape.
- Independently downloaded and hashed all nine cell probe artifacts plus aggregate artifact.
- Verified all nine downloaded probe JSON objects exactly equal the aggregate proof's nine cells.
- Applied DEC-296 deterministic aggregate recompilation with no drift.
- Verified 3,576,519 feature rows, 7,152,783 outcome rows, and 6,763 real raw non-finite values normalized successfully.
- Reconciled non-finite totals as `realized_vol_1h=2683`, `realized_vol_8h=4070`, `realized_vol_24h=10`, all other continuous features zero.
- Classified the repair as verified on accepted real data without mining.
- Kept historical discovery/result production, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-27 — DEC-298 EXP-062 run and evidence contract

- Frozen distinct EXP-062 cell, aggregate, job, artifact, and future workflow identities without creating an executable workflow.
- Preserved the exact DEC-270 18-cell research universe and frozen EXP-061 miner/loader/result semantics.
- Wrapped frozen EXP-061 cell evidence under EXP-062 identity while preserving and revalidating the exact predecessor evidence fingerprint.
- Wrapped frozen EXP-061 aggregate evidence under EXP-062 identity while preserving and revalidating the exact predecessor aggregate fingerprint.
- Bound the verified DEC-293 repair and DEC-297 real-data proof into the EXP-062 protocol fingerprint.
- Preserved the exact future 20-job / 20-artifact success shape.
- Kept workflow source/dispatch, historical execution/result production, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-27 — DEC-299 EXP-062 dormant workflow source

- Frozen a disabled EXP-062 discovery workflow template without creating an active workflow.
- Added a dedicated EXP-062 CLI wired to the DEC-293 repaired adapter and DEC-298 evidence wrappers.
- Reused exact accepted EXP-044 feature/outcome sources through the frozen predecessor source validator.
- Kept the frozen EXP-061 miner and DEC-273 2015-2022 loader semantics unchanged.
- Placed the hard DEC-299 execution gate before any historical source or cell-result read.
- Preserved the exact future 18-cell / 20-job / 20-artifact topology.
- Kept workflow installation/dispatch, historical execution/result production, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-27 — DEC-300 EXP-062 locked workflow installation

- Installed the exact DEC-299 disabled workflow byte-for-byte at the reserved active EXP-062 discovery path.
- Verified dormant and active workflow blobs both equal `1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50`.
- Preserved the hard execution gate before any historical cell source or aggregate-result read.
- Kept workflow/proof/historical-result dispatch, historical execution/result production, rerun/retry/replacement, reserved 2023-2026 access, candidate compilation, promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-27 — DEC-301 EXP-062 gate proof contract

- Predeclared the first proof-only EXP-062 manual-main run as workflow run #1 / attempt 1.
- Required source-ready preflight failure at the locked execution gate.
- Required every materialized downstream job to be skipped.
- Accepted the exact skipped unexpanded GitHub matrix-template shape learned from EXP-061, but never mixed with expanded cells.
- Required exactly one preflight artifact and zero cell/aggregate result artifacts.
- Declared proof slot consumption false.
- Kept proof/historical dispatch, historical execution/result production, rerun/retry/replacement, reserved data, candidate, promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-27 — DEC-302 EXP-062 read-only proof operator

- Added an exact-main read-only planner for the DEC-301 proof-only run.
- Exposed the sole future proof command only while zero matching EXP-062 manual-main runs exist.
- Required any first matching run to remain workflow run #1 / attempt 1.
- Removed the command once a run exists and rejected multiple runs, duplicate ids, run-number/attempt drift, and main-head drift.
- Added no execute mode.
- Kept proof/historical dispatch, historical execution/result production, rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-27 — DEC-303 EXP-062 proof executor

- Added the sole one-shot executor for the proof-only EXP-062 gate run.
- Required executor workflow run #1 / attempt 1 and exact merged-main source pins.
- Required zero existing EXP-062 manual-main runs and two identical fresh DEC-302 plans immediately before dispatch.
- Allowed only the frozen EXP-062 proof command.
- Required the submitted proof to become workflow run #1 / attempt 1 at the executor head.
- Recorded proof submission without consuming a historical-result slot or claiming a historical result.
- Kept historical-result dispatch/execution, rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-27 — DEC-304 EXP-062 proof result review

- Added a read-only combined reviewer for DEC-301 terminal proof evidence and DEC-303 dispatch evidence.
- Required exact proof run #1 / attempt 1 fail-closed behavior on one shared merged-main head.
- Required source-ready preflight evidence, one preflight artifact, zero cell/aggregate result artifacts, and no historical discovery execution.
- Required DEC-303 to prove two identical fresh zero-run DEC-302 plans preceded the proof submission.
- Preserved historical-result slot consumption as false and added no slot-open authority.
- Kept historical-result dispatch/execution, rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-305 source-only EXP-062 proof freeze

- Added `exp062_proof_result_freeze.py` and focused tests.
- Freeze requires an exact DEC-304 reviewed fail-closed result and matching proof head.
- Freeze output is deterministic and carries a canonical SHA-256 fingerprint.
- No runtime proof identity is invented before evidence exists.
- Historical-result slot opening, historical execution, candidate compilation,
  Phase 8B, demo, broker/live, real-money, and trading remain false.


## 2026-09-28 — DEC-306 EXP-062 concrete runtime proof freeze

- Bound authoritative executor run `36358278933` and proof run `36358289723` on exact head `f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb`.
- Bound executor dispatch-evidence artifact `10944404609` and proof preflight artifact `10943489995` to their exact SHA-256 artifact digests.
- Frozen the exact three-job proof shape: failed preflight plus skipped matrix-placeholder and aggregate jobs.
- Bound raw and canonical SHA-256 hashes for executor, proof-run, proof-inventory, and preflight evidence.
- Bound exact DEC-305 freeze fingerprint `fadd6e512b95179fa682d05c8550c914db81e559d9c0ad8da0bedb03bb43a096`.
- Recorded redundant executor run `36360111479` as a fail-closed run #2 that stopped before dispatch and created no second proof.
- Kept historical slot opening/dispatch/execution, rerun/retry/replacement, reserved 2023-2026 data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-28 — DEC-307 EXP-062 source-only historical slot

- Added a source-governance contract for at most one future EXP-062 historical-result attempt.
- Excluded frozen proof run `36358289723` from slot consumption.
- Required the first later matching manual-main run to be run #2 / attempt 1; any such run consumes the slot immediately.
- Rejected multiple historical attempts, GitHub reruns, proof drift, and run-number drift.
- Pinned the DEC-306 runtime proof freeze plus unchanged research/workflow/proof source blobs.
- Kept historical dispatch/execution/result production, reserved 2023-2026 access, candidate/promotion, Phase 8B, demo/live, real-money, and trading false.


## 2026-09-28 — DEC-308 EXP-062 read-only historical operator

- Added an exact-main read-only planner for the single DEC-307 historical slot.
- Exposed the future EXP-062 dispatch command only as plan evidence while the slot is empty.
- Removed the command once a run #2 is present and rejected any second-run plan.
- Added no execute mode or dispatch authority.
- Kept historical execution/result production, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-28 — DEC-309 EXP-062 repository-hosted plan proof

- Added a first-run/attempt-1 push-to-main read-only proof workflow for DEC-308.
- Pinned DEC-306/307/308 source identities and exact active discovery workflow/runtime requirements.
- Verified the historical slot plan on current main without executing its dispatch command.
- Restricted workflow permissions to contents/actions read and artifact output to historical-plan.json only.
- Kept historical dispatch/execution/result production, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.



## 2026-09-28 — DEC-310 EXP-062 historical-plan proof reviewer

- Added a source-only reviewer for the future DEC-309 plan proof.
- Pinned DEC-309 workflow plus DEC-308/307/306 source blobs.
- Required exact run #1 / attempt 1 success and one successful read-only plan job.
- Required one non-expired plan artifact and revalidated its downloaded JSON.
- Added raw and canonical plan SHA-256 identities.
- Added no historical dispatch/execution or downstream trading authority.

## 2026-09-28 — DEC-311 EXP-062 concrete historical-plan proof freeze

- Frozen DEC-309 plan-proof run `36403342301` / job `108866149073` on merged head `95c193343a905acd40daf0eea5d27d55fd2537e1`.
- Bound sole artifact `10960559187` and digest `sha256:07679d85ea3ee0a9373bbd78363ab98eb973377ace6d68828528f91188ff3cf8`.
- Independently verified the artifact ZIP SHA-256 against the GitHub digest.
- Bound plan raw SHA-256 `ac34769d589dbcc18a056d1ebaf960b6881f943f221d771e80216df32d313672`.
- Bound plan canonical SHA-256 `d6cd04c0c29a2e82da12e687ce56ae80387f7ad3c9727b23018ee548684e62a6`.
- Re-runs DEC-310 review before freezing and pins the DEC-310 reviewer source blob.
- Confirms zero historical-result attempts and an unconsumed source-authorized slot.
- Keeps dispatch/execution/result production, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-312 EXP-062 historical execution authorization

- Added a new execution-authorization layer bound to the concrete DEC-311 plan freeze.
- Routed the public EXP-062 CLI execution gate through DEC-312.
- Pinned the activated CLI and unchanged workflow/runtime/research source stack.
- Authorized historical execution/result production only for workflow run #2 / attempt 1.
- Required exact repository, workflow, event, main ref, runtime SHA, and distinct positive run id.
- Kept historical-result dispatch false and added no executor.
- Kept rerun/retry/replacement, reserved 2023-2026 data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-313 EXP-062 read-only historical execution operator

- Added an exact-main planner for the DEC-312 one-shot historical runtime.
- Requires the frozen proof to remain workflow run #1 / attempt 1.
- Targets only future workflow run #2 / attempt 1.
- Exposes the future discovery command as plan evidence only while the slot is empty.
- Removes the command immediately when run #2 is present.
- Adds no execute mode or dispatch authority.
- Keeps rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-314 EXP-062 historical execution-plan proof

- Added a first-run/attempt-1 push-to-main read-only proof workflow for DEC-313.
- Pinned DEC-311/312/313, active discovery workflow, activated CLI, and runtime requirements.
- Fetches current main and EXP-062 manual-main run inventory through read-only GitHub API calls.
- Runs only the DEC-313 planner and validates the run #2 / attempt 1 plan.
- Uploads only immutable historical-execution-plan.json.
- Adds no dispatch/execute path and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-315 EXP-062 execution-plan proof reviewer

- Added a source-only reviewer for future DEC-314 runtime evidence.
- Pinned DEC-314 workflow plus DEC-313 operator/CLI, DEC-312 authorization, activated CLI, active discovery workflow, and DEC-311 freeze.
- Requires exact run #1 / attempt 1 success, one successful proof job, and one non-expired artifact.
- Revalidates the exact run #2 / attempt 1 DEC-313 plan and records raw/canonical SHA-256 hashes.
- Adds no dispatch or execute mode and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-316 EXP-062 reviewed execution-plan freeze

- Added a deterministic freeze builder for valid DEC-315 reviewed evidence.
- Requires exact proof run #1 / attempt 1 success, positive run/job/artifact ids, SHA-256 artifact/plan identities, and target run #2 / attempt 1.
- Requires the exact DEC-311/312/313/314 source-blob map from DEC-315.
- Emits a canonical freeze fingerprint while preserving runtime evidence unchanged.
- Adds no dispatch or execute mode and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-317 EXP-062 concrete historical execution-plan evidence

- Bound the real DEC-314 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical historical-execution-plan hashes.
- Re-runs DEC-315 review and DEC-316 deterministic freezing against the raw evidence.
- Requires the exact DEC-316 freeze fingerprint.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Keeps historical dispatch/execute mode, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.
