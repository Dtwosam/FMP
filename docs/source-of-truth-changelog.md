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

## 2026-09-28 — DEC-318 EXP-062 one-shot dispatch source authorization

- Added a source-only one-shot historical dispatch authorization contract.
- Pinned the concrete DEC-317 runtime-freeze source and fingerprint.
- Requires zero historical-result attempts, an unconsumed slot, and target run #2 / attempt 1.
- Sets only the future dispatch source-contract flag true.
- Keeps actual historical dispatch and executor availability false.
- Keeps rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-319 EXP-062 read-only one-shot dispatch operator

- Added a current-main planner bound to DEC-318.
- Rechecks the frozen proof and historical-result run inventory.
- Exposes the future discovery command only as evidence while the slot is empty.
- Removes the command once run #2 exists.
- Adds no execute/advance mode and keeps actual dispatch/executor availability false.
- Keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-320 EXP-062 read-only dispatch-plan proof

- Added a first-run/attempt-1 push-to-main proof workflow for DEC-319.
- Pinned DEC-317/318/319 plus active discovery workflow and runtime requirements.
- Uses read-only GitHub permissions and API calls.
- Runs only the plan-only dispatch operator.
- Uploads only immutable historical-dispatch-plan.json.
- Adds no workflow submission path and keeps all downstream trading paths locked.

## 2026-09-28 — DEC-321 EXP-062 dispatch-plan reviewer

- Added a source-only reviewer for future DEC-320 runtime evidence.
- Pinned DEC-320/319/318/317 and the active discovery workflow.
- Requires exact first-run/attempt success, one successful job, and one non-expired artifact.
- Revalidates zero-attempt DEC-319 plan semantics and records raw/canonical hashes.
- Adds no dispatch or executor path and keeps downstream trading authority locked.

## 2026-09-28 — DEC-322 EXP-062 reviewed dispatch-plan freeze

- Added a deterministic source-only freeze builder for future DEC-321 reviewed evidence.
- Requires exact DEC-317/318/319/320 source identities and zero-attempt run #2 target semantics.
- Preserves real proof/artifact/plan identities and emits a canonical freeze fingerprint.
- Keeps actual dispatch, executor availability, execute mode, reserved data, and all downstream trading authority locked.

## 2026-09-28 — DEC-323 EXP-062 concrete dispatch-plan runtime evidence

- Bound the real DEC-320 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical historical-dispatch-plan hashes.
- Re-runs DEC-321 review and DEC-322 deterministic freezing against the raw evidence.
- Requires the exact DEC-322 freeze fingerprint.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Keeps actual dispatch/executor/execute mode, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-324 EXP-062 one-shot executor source contract

- Added a source-only one-shot historical executor contract.
- Pinned the concrete DEC-323 runtime-freeze source and fingerprint.
- Requires zero historical-result attempts, an unconsumed slot, and target run #2 / attempt 1.
- Sets only the future executor source-contract flag true.
- Keeps actual executor availability, execute mode, and historical dispatch false.
- Keeps rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-325 EXP-062 read-only historical executor preflight

- Added a current-main preflight bound to DEC-324.
- Rechecks the frozen proof and historical-result run inventory.
- Exposes the future discovery command only as evidence while the slot is empty.
- Removes the command once run #2 exists.
- Adds no execute/advance mode and keeps executor availability plus actual dispatch false.
- Keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-326 EXP-062 historical executor-preflight proof

- Added a first-run/attempt-1 push-to-main read-only proof workflow for DEC-325.
- Pinned DEC-323/324/325, active discovery workflow, preflight CLI, and runtime requirements.
- Fetches current main and EXP-062 manual-main run inventory through read-only GitHub API calls.
- Runs only the DEC-325 preflight planner and validates the run #2 / attempt 1 readiness state.
- Uploads only immutable historical-executor-preflight.json.
- Adds no dispatch/execute path and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-327 EXP-062 executor-preflight proof reviewer

- Added a source-only reviewer for future DEC-326 runtime evidence.
- Pinned DEC-326 workflow plus DEC-323 runtime freeze, DEC-324 executor contract, DEC-325 preflight/CLI, and active discovery workflow.
- Requires exact run #1 / attempt 1 success, one successful proof job, and one non-expired artifact.
- Revalidates the exact run #2 / attempt 1 DEC-325 preflight and records raw/canonical SHA-256 hashes.
- Adds no executor, dispatch, or execute mode and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-328 EXP-062 reviewed executor-preflight freeze

- Added a deterministic freeze builder for valid DEC-327 reviewed evidence.
- Requires exact proof run #1 / attempt 1 success, positive run/job/artifact ids, SHA-256 artifact/preflight identities, and target run #2 / attempt 1.
- Requires the exact DEC-323/324/325/326 source-blob map from DEC-327.
- Emits a canonical freeze fingerprint while preserving runtime evidence unchanged.
- Adds no executor, dispatch, or execute mode and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-329 EXP-062 concrete executor-preflight runtime evidence

- Bound the real DEC-326 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical executor-preflight hashes.
- Re-runs DEC-327 review and DEC-328 deterministic freezing against the raw evidence.
- Requires the exact DEC-328 freeze fingerprint.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Keeps executor availability, actual dispatch, execute mode, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-330 EXP-062 executor activation source contract

- Added a source-only one-shot historical executor activation contract.
- Pinned the concrete DEC-329 runtime-freeze source and fingerprint.
- Requires zero historical-result attempts, an unconsumed slot, and target run #2 / attempt 1.
- Sets only the future activation source-contract flag true.
- Keeps actual executor availability, execute mode, and historical dispatch false.
- Keeps rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.

## 2026-09-28 — DEC-331 EXP-062 read-only executor activation preflight

- Added a current-main activation preflight bound to DEC-330.
- Rechecks the frozen proof and historical-result run inventory.
- Exposes the future discovery command only as evidence while the slot is empty.
- Removes the command once run #2 exists.
- Adds no execute/advance mode and keeps executor availability plus actual dispatch false.
- Keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-332 EXP-062 executor activation-preflight proof

- Added a first-run/attempt-1 push-to-main read-only proof workflow for DEC-331.
- Pinned DEC-330/331, active discovery workflow, activation-preflight CLI, and runtime requirements.
- Fetches current main and EXP-062 manual-main run inventory through read-only GitHub API calls.
- Runs only the DEC-331 activation-preflight planner and validates the run #2 / attempt 1 readiness state.
- Uploads only immutable historical-executor-activation-preflight.json.
- Adds no dispatch/execute path and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-333 EXP-062 activation-preflight proof reviewer

- Added a source-only reviewer for future DEC-332 runtime evidence.
- Pinned DEC-332 workflow plus DEC-329 runtime freeze, DEC-330 activation contract, DEC-331 preflight/CLI, and active discovery workflow.
- Requires exact run #1 / attempt 1 success, one successful proof job, and one non-expired artifact.
- Revalidates the exact run #2 / attempt 1 DEC-331 preflight and records raw/canonical SHA-256 hashes.
- Adds no dispatch or execute mode and keeps reserved data plus all downstream trading paths locked.

## 2026-09-28 — DEC-334 EXP-062 historical terminal review contract

- Predeclared terminal success/failure criteria before the historical run exists.
- Requires exact run #2 / attempt 1 identity.
- Complete success requires exact 20-job / 20-artifact DEC-298 shape.
- Allows the GitHub unexpanded matrix placeholder only for compatible non-success runs.
- Makes every terminal outcome consume the one historical slot permanently.
- Keeps retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-28 — DEC-335 EXP-062 reviewed activation-preflight freeze

- Added a deterministic source-only freeze builder for a valid DEC-333 review.
- Preserves exact DEC-332 proof run/job/artifact identities and artifact digest.
- Preserves raw/canonical activation-preflight SHA-256 hashes and DEC-333 source blobs.
- Freezes target run #2 / attempt 1 and the historical command as evidence only.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no dispatch or execute mode and keeps reserved data plus all downstream trading paths locked.
- Keeps DEC-334 terminal-review criteria as a required gate before any executor reaches main.


## 2026-09-28 — DEC-336 EXP-062 concrete activation-preflight runtime evidence

- Bound the real DEC-332 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical activation-preflight hashes.
- Re-runs DEC-333 review and DEC-335 deterministic freezing against the raw evidence.
- Requires the exact DEC-335 freeze fingerprint.
- Pins the DEC-334 terminal-review contract before executor progression.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Keeps executor availability, actual dispatch, execute mode, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-28 — DEC-337 EXP-062 one-shot historical executor source

- Added a source-only contract for the eventual one-shot historical executor.
- Pinned the concrete DEC-336 runtime-freeze source and fingerprint.
- Requires a fresh DEC-331 empty-slot activation preflight and target run #2 / attempt 1.
- Keeps actual executor availability, dispatch authorization, and execute mode false.
- Keeps rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.
- Requires a repository-hosted source-contract proof before any dispatch-capable workflow.


## 2026-09-28 — DEC-338 EXP-062 one-shot executor source proof

- Added a first-run/attempt-1 push-to-main proof workflow for DEC-337.
- Uses only contents/actions read permissions.
- Replays immutable DEC-332 artifact evidence through DEC-333 / DEC-335 / DEC-336.
- Rebuilds the fresh DEC-331 slot preflight from current main.
- Verifies DEC-337 source-only authorization while executor availability, dispatch, and execute mode remain false.
- Uploads only the source-contract JSON and never submits the historical workflow.
- Keeps reserved data plus all downstream trading paths locked.


## 2026-09-28 — DEC-339 EXP-062 source-proof reviewer

- Added a source-only reviewer for future DEC-338 runtime evidence.
- Pins the DEC-338 workflow, DEC-337 source, DEC-336 runtime freeze, DEC-334 terminal-review contract, and active discovery workflow.
- Requires exact run #1 / attempt 1 success, one successful proof job, and one non-expired artifact.
- Revalidates the source-contract content and records raw/canonical SHA-256 hashes.
- Adds no dispatch or execute mode and keeps reserved data plus all downstream trading paths locked.


## 2026-09-28 — DEC-340 EXP-062 reviewed source-proof freeze

- Added a deterministic source-only freeze builder for a valid DEC-339 review.
- Preserves exact DEC-338 proof run/job/artifact identities and artifact digest.
- Preserves raw/canonical source-contract hashes and DEC-339 review source blobs.
- Freezes DEC-336 runtime evidence, DEC-334 terminal criteria, and target run #2 / attempt 1.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no dispatch or execute mode and keeps reserved data plus all downstream trading paths locked.


## 2026-09-28 — DEC-341 EXP-062 concrete one-shot executor source-proof runtime evidence

- Bound the real DEC-338 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical DEC-337 source-contract hashes.
- Re-runs DEC-339 review and DEC-340 deterministic freezing against the raw evidence.
- Requires the exact DEC-340 freeze fingerprint.
- Pins the DEC-334 terminal-review contract before executor workflow progression.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Keeps executor availability, actual dispatch, execute mode, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-28 — DEC-342 EXP-062 one-shot executor workflow contract

- Added a source-only future one-shot historical executor workflow contract.
- Pinned the concrete DEC-341 runtime-freeze source and fingerprint.
- Requires zero historical-result attempts, an unconsumed slot, and target run #2 / attempt 1.
- Sets only the future workflow-source authorization true.
- Keeps actual executor availability, execute mode, and historical-result dispatch false.
- Keeps rerun/retry/replacement, reserved data, candidate/promotion, Phase 8B, demo/live, real-money, and trading locked.


## 2026-09-28 — DEC-343 EXP-062 read-only executor workflow preflight

- Added a current-main workflow preflight bound to DEC-342.
- Rechecks the frozen proof and historical-result run inventory.
- Exposes the future discovery command only as evidence while the slot is empty.
- Removes the command once run #2 exists.
- Adds no execute/advance mode and keeps executor availability plus actual dispatch false.
- Keeps reserved data plus all downstream trading paths locked.


## 2026-09-28 — DEC-344 EXP-062 workflow-preflight proof

- Added a first-run/attempt-1 push-to-main proof workflow for DEC-343.
- Uses only contents/actions read permissions.
- Pins exact DEC-342/343 source identities and active discovery workflow.
- Invokes only the read-only preflight plan surface.
- Verifies zero historical-result attempts and target run #2 / attempt 1.
- Uploads only the workflow-preflight JSON and never submits the historical workflow.
- Keeps executor availability, actual dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-28 — DEC-345 EXP-062 workflow-preflight proof reviewer

- Added source-only review of future DEC-344 runtime evidence.
- Pinned DEC-344/343/342 source identities and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates slot-available preflight content and records raw/canonical hashes.
- Adds no dispatch or execute mode and keeps downstream authority locked.


## 2026-09-28 — DEC-346 EXP-062 workflow-preflight proof freeze

- Added deterministic source-only freeze for valid DEC-345 review evidence.
- Preserves exact runtime identities, artifact digest, preflight hashes, and source map.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no dispatch or execute surface and keeps downstream authority locked.


## 2026-09-28 — DEC-347 EXP-062 concrete workflow-preflight proof runtime evidence

- Bound the real DEC-344 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical DEC-343 workflow-preflight hashes.
- Re-runs DEC-345 review and DEC-346 deterministic freezing against the raw evidence.
- Requires the exact DEC-346 freeze fingerprint.
- Pins the DEC-334 terminal-review contract.
- Confirms zero historical-result attempts and target run #2 / attempt 1.
- Keeps executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-28 — DEC-348 EXP-062 workflow-install contract

- Added source-only future one-shot historical executor workflow-install contract.
- Pinned DEC-347 runtime-freeze source and fingerprint.
- Fixed the expected future executor workflow path.
- Keeps workflow installed=false, executor available=false, dispatch=false, and execute mode=false.
- Keeps zero historical-result attempts and target run #2 / attempt 1.
- Keeps reserved data and all downstream trading paths locked.


## 2026-09-28 — DEC-349 EXP-062 read-only workflow-install preflight

- Added current-main workflow-install preflight bound to DEC-348.
- Requires the future executor workflow path to remain absent.
- Rechecks the frozen proof and historical-result run inventory.
- Provides only a plan surface; no install, execute, or advance command exists.
- Keeps install authorization, installed state, executor availability, dispatch, and execute mode false.
- Keeps reserved data and all downstream trading paths locked.


## 2026-09-28 — DEC-350 EXP-062 workflow-install preflight proof

- Added first-run/attempt-1 push-to-main proof workflow for DEC-349.
- Uses only contents/actions read permissions.
- Pins DEC-348/349 source identities and requires the future executor workflow path absent.
- Invokes only the read-only install-preflight plan surface.
- Verifies zero historical-result attempts and target run #2 / attempt 1.
- Uploads only the install-preflight JSON and never installs or dispatches anything.


## 2026-09-28 — DEC-351 EXP-062 workflow-install preflight proof reviewer

- Added source-only review of future DEC-350 runtime evidence.
- Pinned DEC-350/349/348 source identities and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates source-absent install-preflight content and records raw/canonical hashes.
- Adds no install, dispatch, or execute mode and keeps downstream authority locked.


## 2026-09-28 — DEC-352 EXP-062 workflow-install preflight proof freeze

- Added deterministic source-only freeze for valid DEC-351 review evidence.
- Preserves exact runtime identities, artifact digest, preflight hashes, and source map.
- Preserves future executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-28 — DEC-353 EXP-062 concrete workflow-install preflight proof runtime evidence

- Bound the real DEC-350 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical DEC-349 workflow-install-preflight hashes.
- Re-runs DEC-351 review and DEC-352 deterministic freezing against the raw evidence.
- Requires the exact DEC-352 freeze fingerprint.
- Pins the DEC-334 terminal-review contract.
- Confirms the future executor workflow path remains absent.
- Keeps install authorization, installed state, executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-28 — DEC-354 EXP-062 workflow-installation source contract

- Added source-only dormant executor workflow-installation contract.
- Pinned DEC-353 runtime-freeze source and fingerprint.
- Fixed dormant disabled-template path and reserved active workflow path.
- Keeps dormant template absent and active workflow uninstalled.
- Keeps executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-28 — DEC-355 EXP-062 dormant one-shot executor workflow source

- Added disabled one-shot historical executor template under `docs/superpowers/templates/`.
- Pinned DEC-354, dormant template, and active discovery workflow source identities.
- Template encodes one manual executor run and exactly one discovery workflow dispatch.
- Template resolves target run #2 / attempt 1 and writes an immutable receipt.
- No active executor workflow is installed.
- Install, executor, dispatch, execute, reserved-data, and trading authority remain locked.


## 2026-09-28 — DEC-356 EXP-062 dormant executor source proof

- Added first-run/attempt-1 push-to-main proof workflow for DEC-355.
- Uses only contents/actions read permissions.
- Pins DEC-354/355 source identities and dormant template blob.
- Requires active executor workflow path absent.
- Validates dormant source directly and uploads only a source JSON artifact.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-28 — DEC-357 EXP-062 dormant executor source-proof reviewer

- Added source-only review of future DEC-356 runtime evidence.
- Pinned DEC-356/355/354 source identities, dormant template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates dormant-source JSON and records raw/canonical hashes.
- Adds no install, dispatch, or execute mode and keeps downstream authority locked.


## 2026-09-28 — DEC-358 EXP-062 dormant executor source-proof freeze

- Added deterministic source-only freeze for valid DEC-357 review evidence.
- Preserves exact runtime identities, artifact digest, source hashes, and source map.
- Preserves dormant template source and active executor uninstalled state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-28 — DEC-359 EXP-062 concrete dormant-source proof runtime evidence

- Bound the real DEC-356 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical DEC-355 dormant-source hashes.
- Re-runs DEC-357 review and DEC-358 deterministic freezing against the raw evidence.
- Requires the exact DEC-358 freeze fingerprint.
- Pins the DEC-334 terminal-review contract.
- Confirms dormant template source only, active executor workflow uninstalled, zero historical-result attempts, and target run #2 / attempt 1.
- Keeps install, executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-28 — DEC-360 EXP-062 active executor workflow install contract

- Added source-only active workflow install contract bound to DEC-359.
- Pinned the exact dormant executor template blob.
- Reserved the active executor workflow path while requiring it to remain absent.
- Keeps install authorization, installed state, executor availability, dispatch, and execute mode false.
- Keeps zero historical-result attempts and target run #2 / attempt 1.
- Keeps reserved data and all downstream trading paths locked.


## 2026-09-28 — DEC-361 EXP-062 read-only active workflow install preflight

- Added current-main active workflow-install preflight bound to DEC-360.
- Pins exact dormant executor template source.
- Requires active executor workflow path absent.
- Rechecks the frozen proof and historical-result run inventory.
- Provides only a plan surface; no install, execute, advance, or dispatch command exists.
- Keeps install authorization, installed state, executor availability, dispatch, and execute mode false.
- Keeps reserved data and all downstream trading paths locked.


## 2026-09-28 — DEC-362 EXP-062 active workflow install preflight proof

- Added first-run/attempt-1 push-to-main proof workflow for DEC-361.
- Uses only contents/actions read permissions.
- Pins DEC-360/361 source identities, dormant template, discovery workflow, and planning runtime.
- Requires active executor workflow path absent.
- Invokes only the read-only active install-preflight plan surface.
- Verifies zero historical-result attempts and target run #2 / attempt 1.
- Uploads only the preflight JSON and never installs or dispatches anything.


## 2026-09-28 — DEC-363 EXP-062 active install-preflight proof reviewer

- Added source-only review of future DEC-362 runtime evidence.
- Pinned DEC-362/361/360 source identities, dormant template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates active-path-absent preflight content and records raw/canonical hashes.
- Adds no install, dispatch, or execute mode and keeps downstream authority locked.


## 2026-09-28 — DEC-364 EXP-062 active install-preflight proof freeze

- Added deterministic source-only freeze for valid DEC-363 review evidence.
- Preserves exact runtime identities, artifact digest, preflight hashes, source map, and dormant-template identity.
- Preserves active executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-28 — DEC-365 EXP-062 concrete active install-preflight proof runtime evidence

- Bound the real DEC-362 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical DEC-361 active workflow-install-preflight hashes.
- Re-runs DEC-363 review and DEC-364 deterministic freezing against the raw evidence.
- Requires the exact DEC-364 freeze fingerprint.
- Pins the DEC-334 terminal-review contract.
- Confirms active executor workflow path absent, zero historical-result attempts, and target run #2 / attempt 1.
- Keeps install, installed state, executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-28 — DEC-366 EXP-062 active workflow-installation contract

- Added source-only active workflow-installation contract bound to DEC-365.
- Pinned the exact dormant executor workflow template.
- Keeps the active workflow path absent.
- Keeps install authorization, installed state, executor availability, dispatch, and execute mode false.
- Keeps zero historical-result attempts and target run #2 / attempt 1.
- Keeps reserved data and all downstream trading paths locked.


## 2026-09-28 — DEC-367 EXP-062 active workflow-installation preflight

- Added read-only current-main preflight bound to DEC-366.
- Requires exact dormant-template identity and active workflow path absent state.
- Rechecks the frozen proof and historical-result run inventory.
- Provides only a plan surface; no install, execute, advance, or workflow-dispatch command exists.
- Keeps install, installed state, executor availability, dispatch, execute mode, reserved data, and downstream trading paths locked.


## 2026-09-28 — DEC-368 EXP-062 workflow-installation preflight proof

- Added first-run/attempt-1 push-to-main proof workflow for DEC-367.
- Uses only contents/actions read permissions.
- Pins DEC-366/367 source identities plus exact dormant-template identity.
- Invokes only the read-only installation-preflight plan surface.
- Verifies zero historical-result attempts and target run #2 / attempt 1.
- Uploads only the installation-preflight JSON and never installs or dispatches anything.


## 2026-09-28 — DEC-369 EXP-062 active installation-preflight proof reviewer

- Added source-only review of future DEC-368 runtime evidence.
- Pinned DEC-368/367/366 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates source-ready active-workflow-absent preflight content and records raw/canonical hashes.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-28 — DEC-370 EXP-062 active installation-preflight proof freeze

- Added deterministic source-only freeze for valid DEC-369 review evidence.
- Preserves exact runtime identities, artifact digest, preflight hashes, and source map.
- Preserves active executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-28 — DEC-371 EXP-062 concrete active workflow-installation proof runtime evidence

- Bound the real DEC-368 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical DEC-367 workflow-installation-preflight hashes.
- Re-runs DEC-369 review and DEC-370 deterministic freezing against the raw evidence.
- Requires the exact DEC-370 freeze fingerprint.
- Pins the DEC-334 terminal-review contract.
- Confirms active executor workflow path absent, zero historical-result attempts, and target run #2 / attempt 1.
- Keeps install, installed state, executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-28 — DEC-372 EXP-062 active install-authorization contract

- Added source-only future install-authorization contract for the active one-shot historical executor workflow.
- Pinned DEC-371 runtime-freeze source and fingerprint plus the dormant executor template.
- Keeps active workflow path absent.
- Keeps actual install authorization, installed state, executor availability, dispatch, and execute mode false.
- Keeps zero historical-result attempts and target run #2 / attempt 1.
- Keeps reserved data and all downstream trading paths locked.


## 2026-09-28 — DEC-373 EXP-062 read-only install-authorization preflight

- Added current-main install-authorization preflight bound to DEC-372.
- Requires the active executor workflow path to remain absent.
- Rechecks the frozen proof and historical-result run inventory.
- Provides only a plan surface; no install, execute, advance, or dispatch command exists.
- Keeps actual install authorization, installed state, executor availability, dispatch, and execute mode false.
- Keeps reserved data and all downstream trading paths locked.


## 2026-09-28 — DEC-374 EXP-062 install-authorization preflight proof

- Added first-run/attempt-1 push-to-main proof workflow for DEC-373.
- Uses only contents/actions read permissions.
- Pins DEC-372/373 source identities, dormant template, active discovery workflow, and planning runtime.
- Requires the active executor workflow path absent.
- Invokes only the read-only install-authorization preflight plan surface.
- Verifies zero historical-result attempts and target run #2 / attempt 1.
- Uploads only the authorization-preflight JSON and never installs or dispatches anything.


## 2026-09-29 — DEC-375 EXP-062 install-authorization proof reviewer

- Added source-only review of DEC-374 runtime evidence.
- Pinned DEC-374/373/372 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates install-authorization preflight content and records raw/canonical hashes.
- Adds no install, dispatch, or execute mode and keeps downstream authority locked.


## 2026-09-29 — DEC-376 EXP-062 install-authorization proof freeze

- Added deterministic source-only freeze for valid DEC-375 review evidence.
- Preserves exact runtime identities, artifact digest, preflight hashes, and source map.
- Preserves active executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-29 — DEC-377 EXP-062 concrete install-authorization proof runtime evidence

- Bound the real DEC-374 merged-main proof run/job/artifact identities.
- Verified the artifact ZIP SHA-256 independently against GitHub's artifact digest.
- Bound exact raw and canonical DEC-373 install-authorization-preflight hashes.
- Re-runs DEC-375 review and DEC-376 deterministic freezing against the raw evidence.
- Requires the exact DEC-376 freeze fingerprint.
- Pins the DEC-334 terminal-review contract.
- Confirms active executor workflow path absent, zero historical-result attempts, and target run #2 / attempt 1.
- Keeps install, installed state, executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-29 — DEC-378 EXP-062 active workflow install-decision contract

- Added source-only install-decision contract bound to DEC-377.
- Pinned DEC-377 runtime-freeze blob and fingerprint plus dormant-template identity.
- Requires the active executor workflow path to remain absent.
- Authorizes only install-decision source; actual install remains false.
- Keeps executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-29 — DEC-379 EXP-062 install-decision preflight

- Added current-main read-only preflight bound to DEC-378.
- Pins DEC-378 source identity and dormant executor template.
- Requires active executor workflow path absent and historical slot unused.
- Exposes only a plan surface; no install, execute, advance, or dispatch command exists.
- Keeps all downstream trading authority locked.


## 2026-09-29 — DEC-380 EXP-062 install-decision preflight proof

- Added first-run/attempt-1 push-to-main proof for DEC-379.
- Uses only contents/actions read permissions.
- Pins DEC-378/379 source identities, dormant template, discovery workflow, and planning runtime.
- Invokes only the read-only install-decision preflight plan surface.
- Verifies zero historical-result attempts and target run #2 / attempt 1.
- Uploads only the decision-preflight JSON and never installs or dispatches anything.


## 2026-09-29 — DEC-381 EXP-062 install-decision proof reviewer

- Added source-only review of future DEC-380 runtime evidence.
- Pinned DEC-380/379/378 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates install-decision preflight content and records raw/canonical hashes.
- Adds no install, dispatch, or execute mode and keeps downstream authority locked.


## 2026-09-29 — DEC-382 EXP-062 install-decision proof freeze

- Added deterministic source-only freeze for valid DEC-381 review evidence.
- Preserves exact runtime identities, artifact digest, preflight hashes, and source map.
- Preserves active executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-29 — DEC-383 EXP-062 concrete install-decision proof runtime binding

- Bound successful DEC-380 run/job/artifact identities and artifact digest.
- Bound exact DEC-379 raw/canonical preflight hashes.
- Replays DEC-381 review and DEC-382 freeze and requires exact DEC-382 fingerprint.
- Independently requires artifact ZIP SHA-256 to match the GitHub artifact digest.
- Keeps active executor workflow absent and all install/executor/dispatch/trading authority locked.


## 2026-09-29 — DEC-384 EXP-062 install-execution authorization contract

- Added source-only install-execution authorization contract bound to DEC-383.
- Pinned DEC-383 runtime-freeze blob and fingerprint plus dormant-template identity.
- Requires the active executor workflow path to remain absent.
- Authorizes only install-execution authorization source; actual install remains false.
- Keeps executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-29 — DEC-385 EXP-062 install-execution authorization preflight

- Added current-main read-only preflight bound to DEC-384.
- Pins DEC-384 source identity and dormant executor template.
- Requires active executor workflow path absent and historical slot unused.
- Preserves install-authorization, install-decision, and install-execution authorization as source-only gates.
- Exposes only a plan surface; no install, execute, advance, or dispatch command exists.
- Keeps all downstream trading authority locked.


## 2026-09-29 — DEC-386 EXP-062 install-execution authorization preflight proof

- Added first-run/attempt-1 push-to-main proof for DEC-385.
- Uses only contents/actions read permissions.
- Pins DEC-384/385 source identities, dormant template, discovery workflow, and planning runtime.
- Invokes only the read-only execution-authorization preflight plan surface.
- Verifies all three source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the preflight JSON and never installs or dispatches anything.


## 2026-09-29 — DEC-387 EXP-062 execution-authorization proof reviewer

- Added source-only review of future DEC-386 runtime evidence.
- Pinned DEC-386/385/384 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates execution-authorization preflight content and records raw/canonical hashes.
- Adds no install, dispatch, or execute mode and keeps downstream authority locked.


## 2026-09-29 — DEC-388 EXP-062 install-execution authorization proof freeze

- Added deterministic source-only freeze for valid DEC-387 review evidence.
- Preserves exact DEC-386 runtime identities, artifact digest, DEC-385 preflight hashes, and source map.
- Preserves active executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-29 — DEC-389 EXP-062 concrete install-execution authorization proof runtime binding

- Bound successful DEC-386 run/job/artifact identities and artifact digest.
- Bound exact DEC-385 raw/canonical preflight hashes.
- Replays DEC-387 review and DEC-388 freeze and requires the exact DEC-388 fingerprint.
- Independently requires artifact ZIP SHA-256 to match the GitHub artifact digest.
- Keeps active executor workflow absent and all install/executor/dispatch/trading authority locked.


## 2026-09-29 — DEC-390 EXP-062 workflow install-execution contract

- Added source-only install-execution contract bound to DEC-389.
- Pinned DEC-389 runtime-freeze blob and fingerprint plus dormant-template identity.
- Corrected the predecessor head binding to the real DEC-386 merged head.
- Requires the active executor workflow path to remain absent.
- Authorizes only the install-execution contract source; actual install remains false.
- Keeps executor availability, dispatch, execute mode, reserved data, and all downstream trading paths locked.


## 2026-09-29 — DEC-391 EXP-062 workflow install-execution preflight

- Added current-main read-only preflight bound to DEC-390.
- Pins DEC-390 source identity and dormant executor template.
- Requires active executor workflow path absent and historical slot unused.
- Preserves all four source-only gates.
- Exposes only a plan surface; no install, execute, advance, or dispatch command exists.
- Keeps all downstream trading authority locked.


## 2026-09-29 — DEC-392 EXP-062 workflow install-execution preflight proof

- Added first-run/attempt-1 push-to-main proof for DEC-391.
- Uses only contents/actions read permissions.
- Pins DEC-390/391 source identities, dormant template, discovery workflow, and planning runtime.
- Invokes only the read-only install-execution preflight plan surface.
- Verifies all four source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the preflight JSON and never installs or dispatches anything.


## 2026-09-29 — DEC-393 EXP-062 install-execution proof reviewer

- Added source-only review of future DEC-392 runtime evidence.
- Pinned DEC-392/391/390 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates DEC-391 preflight content and records raw/canonical hashes.
- Preserves all four source-only gates and adds no install, dispatch, or execute mode.


## 2026-09-29 — DEC-394 EXP-062 install-execution proof freeze

- Added deterministic source-only freeze for valid DEC-393 review evidence.
- Preserves exact DEC-392 runtime identities, artifact digest, DEC-391 preflight hashes, and source map.
- Preserves all four source-only gates and active executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-29 — DEC-395 EXP-062 install-execution proof runtime freeze

- Bound the real successful DEC-392 merged-main proof evidence.
- Pinned exact proof head/run/job/artifact identities and GitHub artifact digest.
- Pinned raw/canonical DEC-391 preflight hashes.
- Revalidated DEC-393 review and DEC-394 freeze with fingerprint
  `9357b1c6591a801237acacf7cb7eab1f5302608770ad7b3033566bda39cb3548`.
- Preserves all four source-only gates and active executor workflow path absent state.
- Adds no install, dispatch, or execute surface; downstream authority remains locked.
- Next gate: source-only active executor workflow install-activation contract.


## 2026-09-29 — DEC-396 EXP-062 workflow install-activation contract

- Added a source-only workflow install-activation contract bound to corrected DEC-395.
- Pins DEC-395 blob/fingerprint and the dormant executor template.
- Preserves four predecessor source-only gates and adds only the install-activation source gate.
- Keeps actual install, dispatch, execute mode, reserved data, and downstream trading authority locked.


## 2026-09-29 — DEC-397 EXP-062 workflow install-activation preflight

- Added current-main read-only preflight bound to DEC-396.
- Pins DEC-396 source identity and dormant executor template.
- Requires active executor workflow path absent and historical slot unused.
- Preserves all five source-only gates.
- Exposes only a plan surface and keeps actual install/dispatch/execute authority locked.


## 2026-09-29 — DEC-398 EXP-062 workflow install-activation preflight proof

- Added first-run/attempt-1 push-to-main proof for DEC-397.
- Uses only contents/actions read permissions.
- Pins DEC-396/397 source identities, dormant template, discovery workflow, and planning runtime.
- Invokes only the read-only install-activation preflight plan surface.
- Verifies all five source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the activation-preflight JSON and never installs or dispatches anything.


## 2026-09-29 — DEC-399 EXP-062 install-activation proof reviewer

- Added source-only review of future DEC-398 runtime evidence.
- Pinned DEC-398/397/396 source identities, dormant executor template, and active discovery workflow.
- Requires exact successful proof run/job/artifact shape.
- Revalidates DEC-397 preflight content and records raw/canonical hashes.
- Preserves all five source-only gates and adds no install, dispatch, or execute mode.


## 2026-09-29 — DEC-400 EXP-062 install-activation proof freeze

- Added deterministic source-only freeze for valid DEC-399 review evidence.
- Preserves exact DEC-398 runtime identities, artifact digest, DEC-397 preflight hashes, and source map.
- Preserves all five source-only gates and active executor workflow path absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface and keeps downstream authority locked.


## 2026-09-29 — DEC-401 EXP-062 install-activation proof runtime binding

- Bound the real successful DEC-398 merged-main proof.
- Pinned exact run/job/artifact identities plus GitHub/ZIP digest.
- Pinned raw and canonical DEC-397 preflight hashes.
- Replays merged DEC-399 review and DEC-400 deterministic freeze.
- Requires exact DEC-400 fingerprint 441c508902f816faee66c58768552a7d3ab05f0b145193a3e6349f18c9062808.
- Preserves all five source-only gates while actual install, dispatch, execute mode, and downstream trading authority remain locked.


## 2026-09-29 — DEC-402 EXP-062 workflow-install source contract

- Added a new source-only workflow-install contract bound to DEC-401.
- Preserved the historical DEC-360 contract module unchanged.
- Pinned DEC-401 runtime-freeze blob and fingerprint plus dormant-template identity.
- Adds only the final workflow-install source gate.
- Requires the active executor workflow path to remain absent.
- Keeps actual install, executor availability, dispatch, execute mode, reserved data, and downstream trading authority locked.


## 2026-09-29 — DEC-403 EXP-062 workflow-install source preflight

- Added current-main read-only preflight bound to DEC-402.
- Requires active executor workflow path absent and historical slot unused.
- Preserves all six source-only gates.
- Exposes only a plan surface; no install, execute, advance, or dispatch command exists.
- Keeps downstream trading authority locked.


## 2026-09-29 — DEC-404 EXP-062 workflow-install source-preflight proof

- Added first-run/attempt-1 push-to-main proof for DEC-403.
- Uses only contents/actions read permissions.
- Pins DEC-402/403 source identities, dormant template, discovery workflow, and planning runtime.
- Invokes only the read-only source-preflight plan surface.
- Verifies all six source-only gates, zero historical-result attempts, and target run #2 / attempt 1.
- Uploads only the source-preflight JSON and never installs or dispatches anything.


## 2026-09-29 — DEC-407 explicit DEC-404 proof recovery

- Recorded DEC-404 run #1 / attempt 1 as a genuine failed proof-wrapper run.
- Recorded that DEC-403 plan execution succeeded and only the wrapper verification failed.
- Identified the invalid wrapper field: `install_source_slot_verified_available`.
- Added exact run #2 / attempt 1 recovery semantics on the same read-only workflow.
- Pinned failed run `36613664506`, failed job `109561121322`, and failed head `0db04ae49b3533778b08afa31e9ef9a26576b80c`.
- Removed no runtime lock and added no installation or historical-dispatch authority.


## 2026-09-29 — DEC-408 recovery-proof reviewer

- Added strict source-only review for DEC-407 recovery run #2 / attempt 1.
- Pinned corrected recovery workflow, DEC-403 preflight/CLI, and DEC-402 contract.
- Removed the invalid historical assumption that DEC-403 emits an install-source slot field.
- Preserved failed DEC-404 run/job/head as immutable lineage.
- Added no install, dispatch, execute, reserved-data, or trading authority.


## 2026-09-29 — DEC-409 recovery-proof freeze

- Added deterministic source-only freeze for DEC-408 recovery reviews.
- Preserves failed DEC-404 and successful DEC-407 run provenance in one frozen object.
- Preserves exact recovery proof identities, artifact digest, DEC-403 hashes, and source map.
- Adds no installation, dispatch, execute-mode, reserved-data, or trading authority.


## 2026-09-29 — DEC-410 EXP-062 recovery runtime binding

- Added concrete runtime-evidence binding for successful DEC-407 recovery proof.
- Preserves failed DEC-404 run #1 and successful DEC-407 run #2 in one immutable lineage.
- Pins recovery run/job/artifact identities, ZIP digest, raw/canonical DEC-403 hashes, DEC-408 reviewer, DEC-409 freeze builder, and terminal-review contract.
- Requires exact DEC-409 deterministic freeze fingerprint.
- Keeps all six source-only gates true while actual install/dispatch/execute/trading authority remains false.


## 2026-09-29 — DEC-411 EXP-062 final workflow-install authorization contract

- Added source-only final authorization contract bound to DEC-410.
- Pins DEC-410 source blob and runtime-freeze fingerprint.
- Preserves the failed-run/recovery-run lineage transitively.
- Adds only the seventh source-only gate.
- Keeps actual install, executor, dispatch, execute, reserved-data, and trading authority locked.


## 2026-09-29 — DEC-412 EXP-062 final authorization preflight

- Added current-main read-only preflight bound to DEC-411.
- Requires active executor workflow path absent and historical slot unused.
- Preserves all seven source-only gates.
- Exposes only a plan surface; no install, execute, advance, or dispatch command exists.
- Keeps downstream trading authority locked.


## 2026-09-29 — DEC-413 EXP-062 final authorization preflight proof

- Added first-run/attempt-1 push-to-main proof for DEC-412.
- Uses only contents/actions read permissions.
- Pins DEC-411/412 source identities and planning dependencies.
- Invokes only the read-only final-authorization preflight plan surface.
- Verifies all seven source-only gates and keeps actual install/dispatch/execute authority false.
- Uploads only the final-authorization-preflight JSON.


## 2026-09-29 — DEC-414 EXP-062 final authorization proof reviewer

- Added source-only review of future DEC-413 runtime evidence.
- Pins DEC-413/412/411 source identities.
- Requires exact successful proof run/job/artifact shape.
- Revalidates DEC-412 preflight content and records raw/canonical hashes.
- Preserves all seven source-only gates and adds no install/dispatch/execute mode.


## 2026-09-29 — DEC-415 EXP-062 final authorization proof freeze

- Added deterministic source-only freeze for valid DEC-414 review evidence.
- Preserves exact DEC-413 runtime identities, artifact digest, DEC-412 preflight hashes, and source map.
- Preserves all seven source-only gates and active-workflow-absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface.


## 2026-09-29 — DEC-416 EXP-062 final authorization proof runtime binding

- Bound exact successful DEC-413 run/job/artifact identities.
- Verified artifact ZIP digest and raw/canonical DEC-412 preflight hashes.
- Re-runs DEC-414 review and DEC-415 deterministic freezing.
- Pins DEC-415 fingerprint `4a71a6b29ccea4d5415ce64ca84fc0c43988a2daf98cbe912f4654868b907ffa`.
- Preserves all seven source-only gates.
- Adds no workflow installation, dispatch, execute mode, or trading authority.


## 2026-09-29 — DEC-417 EXP-062 workflow-install action contract

- Added source-only install-action contract bound to DEC-416.
- Pins DEC-416 runtime-freeze blob and fingerprint plus dormant-template identity.
- Preserves seven predecessor source-only gates and adds the action-contract source gate.
- Requires the active executor workflow path to remain absent.
- Adds no workflow installation, dispatch, execute mode, reserved-data, or trading authority.


## 2026-09-29 — DEC-418 EXP-062 workflow-install action preflight

- Added current-main read-only preflight bound to DEC-417.
- Pins DEC-417 source identity and dormant executor template.
- Requires active executor workflow path absent and historical slot unused.
- Preserves all eight source-only gates.
- Exposes only a plan surface; no install, execute, advance, or dispatch command exists.


## 2026-09-29 — DEC-419 EXP-062 workflow-install action preflight proof

- Added first-run/attempt-1 push-to-main proof for DEC-418.
- Uses only contents/actions read permissions.
- Pins DEC-417/418 source identities, dormant template, discovery workflow, and planning runtime.
- Invokes only the read-only workflow-install action-preflight plan surface.
- Preserves all eight source-only gates and requires the historical slot unused.
- Uploads only the action-preflight JSON and never installs or dispatches anything.

## 2026-09-29 — DEC-420 EXP-062 workflow-install action proof reviewer

- Added source-only review of successful DEC-419 runtime evidence.
- Pins DEC-419/418/417 source identities.
- Requires exact successful proof run/job/artifact shape.
- Revalidates DEC-418 preflight content and records raw/canonical hashes.
- Preserves all eight source-only gates and adds no install/dispatch/execute mode.


## 2026-09-29 — DEC-421 EXP-062 workflow-install action proof freeze

- Added deterministic source-only freeze for valid DEC-420 review evidence.
- Preserves exact DEC-419 runtime identities, artifact digest, DEC-418 preflight hashes, and source map.
- Preserves all eight source-only gates and active-workflow-absent state.
- Emits a canonical freeze fingerprint for later concrete runtime binding.
- Adds no install, dispatch, or execute surface.

## 2026-09-29 — DEC-422 EXP-062 workflow-install action proof runtime binding

- Bound exact successful DEC-419 run/job/artifact identities.
- Verified artifact ZIP digest and raw/canonical DEC-418 preflight hashes.
- Re-runs DEC-420 review and DEC-421 deterministic freezing.
- Pins DEC-421 fingerprint `78bcceaf580672b97858ec972c590300316f8b7b369137ca96e957c39d1d9a5d`.
- Preserves all eight source-only gates.
- Adds no workflow installation, dispatch, execute mode, reserved-data, or trading authority.

## 2026-09-30 — DEC-423 EXP-062 active workflow mutation authorization

- Added explicit repository-mutation authorization bound to DEC-422.
- Pins the DEC-422 runtime-freeze blob/fingerprint and dormant executor template.
- Opens only workflow-install authorization.
- Does not install the workflow, dispatch historical discovery, or expose trading authority.

## 2026-09-30 — DEC-424 EXP-062 active workflow installation

- Installed the active one-shot historical executor workflow from the exact pinned dormant template.
- Marks workflow installed and executor available.
- Keeps historical dispatch, execute mode, reserved-data access, and trading authority locked.
- Adds no automatic trigger; the workflow remains `workflow_dispatch` only.

## 2026-09-30 — DEC-425 EXP-062 installed executor dispatch preflight

- Added read-only current-main preflight for the installed executor.
- Requires exact active workflow blob, zero executor runs, and unused historical slot.
- Keeps dispatch, execute mode, reserved-data access, and trading authority locked.

## 2026-09-30 — DEC-426 EXP-062 installed executor dispatch-preflight proof

- Added repository-hosted read-only proof for DEC-425.
- Proof has actions read only and no workflow-dispatch trigger.
- Requires executor run count zero and historical-result slot unused.
- Adds no dispatch, execute mode, reserved-data, or trading authority.

## 2026-09-30 — DEC-427/428 EXP-062 dispatch-preflight proof review and freeze

- Added strict review of successful merged-main DEC-426 evidence.
- Added deterministic freeze of reviewed proof evidence.
- Preserves installed executor state and zero executor runs.
- Keeps dispatch, execute mode, reserved-data access, and trading authority locked.

## 2026-09-30 — DEC-429 EXP-062 dispatch-preflight proof runtime binding

- Bound exact successful DEC-426 runtime evidence.
- Verified artifact ZIP and raw/canonical DEC-425 hashes.
- Pins DEC-428 deterministic freeze fingerprint.
- Keeps executor run count zero and all dispatch/execute/trading authority locked.

## 2026-09-30 — DEC-430 EXP-062 one-shot executor dispatch authorization

- Added explicit one-shot executor dispatch authorization bound to DEC-429.
- Scope is exact first executor run and exact historical result run #2 / attempt 1.
- Does not trigger the workflow.
- Keeps general execute mode, reruns, reserved data, and trading authority locked.

## 2026-09-30 — DEC-431 EXP-062 one-shot dispatch action preflight

- Added plan-only current-main preflight for the authorized one-shot executor run.
- Requires both one-shot inventories to remain unused.
- Adds no execution surface and triggers no workflow.

## 2026-09-30 — DEC-432 EXP-062 one-shot dispatch action-preflight proof

- Added repository-hosted read-only proof for DEC-431.
- Proof uses actions read only and has no workflow-dispatch trigger.
- Confirms authorization and both unused one-shot slots without executing anything.

## 2026-09-30 — DEC-433/434 EXP-062 action-preflight proof review and freeze

- Added strict proof reviewer and deterministic freeze for DEC-432.
- Preserves one-shot authorization and both unused run slots.
- Adds no execution path or downstream trading authority.


## 2026-09-30 — DEC-435 EXP-062 one-shot dispatch action-preflight proof runtime binding

- Bound real DEC-432 run/job/artifact and exact ZIP/raw/canonical hashes.
- Bound the deterministic DEC-434 freeze fingerprint.
- Preserves explicit authorization only for executor run #1 / attempt 1.
- Executor run count and historical-result attempt count remain zero.
- General execute mode, rerun/retry/replacement, reserved data, and trading remain locked.


## 2026-09-30 — DEC-436 one-shot executor fail-closed recovery

- Preserved failed original executor run `36702494195` / job `109844958600`.
- Confirmed failure occurred before historical dispatch and produced no artifact.
- Preserved the original executor workflow blob unchanged.
- Added a separate manual-only recovery workflow with exact run #1 / attempt 1.
- Historical result target remains run #2 / attempt 1 with zero attempts consumed.
- Generic rerun/retry/replacement and all trading authority remain locked.


## 2026-09-30 — DEC-437/438 recovery receipt review and freeze

- Added strict reviewer for future DEC-436 recovery runtime evidence.
- Added deterministic freeze with canonical SHA-256 fingerprint.
- Pins recovery workflow/auth source plus original executor/discovery workflows.
- Requires discovery target head to match the recovery head.
- Adds no execution or trading authority.


## 2026-10-02 — Discovery-first research operating guardrail

- Refreshed `docs/project-state.md` to the current Phase 8A / DEC-467 / EXP-065 one-shot state.
- Added `docs/research-method-operating-guardrail.md` as the mandatory operating interpretation of DEC-268/DEC-270.
- Updated `AGENTS.md` so every research session must read the guardrail and distinguish the governing discovery-first framework from the current bounded sub-experiment.
- Clarified that EXP-065 pairwise interactions are one evidence-generating sub-experiment, not the FMP research method.
- Clarified that a negative narrow experiment rejects only its frozen representation/protocol and cannot be generalized into failure of discovery-first market learning.
- Added a mandatory successor-experiment mapping back to the broader discovery-first workflow.
- Changed no research thresholds, historical execution authority, reserved-data access, promotion, Phase 8B, demo/live, broker, real-money, or trading authority.
## 2026-10-02 — DEC-468 EXP-065 historical result frozen

- Froze the sole EXP-065 one-shot run `36905224184` at exact head `5faa733572576aa5a1c56176ac27c415eaaf6416`.
- Bound 20/20 successful jobs, 20/20 non-expired artifacts, aggregate artifact `11202316160`, exact artifact digest, raw JSON SHA-256, and canonical evidence fingerprint.
- Independently recomputed all 18 cell fingerprints and the aggregate fingerprint.
- Froze exact totals: 13,680 hypotheses / 13,680 evaluable / 0 qualifying / 0 deduplicated / 0 shortlisted / 0 frozen.
- Classified only the exact frozen EXP-065 pairwise-interaction protocol as negative; DEC-268 discovery-first market-pattern research remains the governing method.
- Kept the 2023-01-01 through 2026-08-20 reserve closed and all rerun/retry/replacement, candidate, promotion, Phase 8B, demo/live, broker, real-money, and trading authority false.
- Next gate is an explicit discovery-first successor-direction decision under `docs/research-method-operating-guardrail.md`, not another automatic transform/search.

## 2026-10-02 — DEC-469 annual pattern catalogue governing method

- Made year-by-year pattern cataloguing the mandatory operating form of DEC-268 discovery-first research.
- Requires each authorized historical year/segment to be independently catalogued and frozen before cross-year strategy synthesis.
- Requires all patterns surfaced by the frozen bounded grammar to be preserved, including non-qualifiers and negative/failure evidence.
- Requires canonical cross-year comparison of recurrence, support, effect direction/magnitude, after-cost economics, failure years, sign reversals, applicability, and concentration.
- Makes state transitions, pairwise interactions, clustering/models, and named rule families pattern types/tools inside the catalogue rather than the governing method.
- Requires Strategy V1 to be synthesized only from frozen cross-year evidence and frozen before prospective shadow/demo.
- Preserves fixed-version demo learning: completed demo evidence may build Strategy V2, but running Strategy V1 cannot self-modify; Strategy V2 requires later fresh prospective evidence.
- Records PR #617 as closed unmerged and therefore non-authoritative.
- Keeps 2023-2026 protected at this gate; a separate explicit access decision is required before those years join the catalogue.
- Adds no historical execution, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation, real-money, or trading authority.

## 2026-10-02 — DEC-470 annual catalogue protocol and full-collection scope

- Froze Catalogue V1 before historical execution.
- Explicitly authorized all collected 2015-2026 year-segments for the DEC-469 annual-catalogue / Strategy V1 research scope.
- Repurposed the former EXP-061 through EXP-065 2023-2026 reserve for this research path only; those years cannot later be claimed as untouched OOS for Strategy V1.
- Reused the accepted V1 market universe and existing full-history feature/outcome materialization; no new data or feature family was added.
- Froze strict prior-only annual tertile state encoding with a 300-row minimum.
- Froze 65 snapshot singles + 2,010 snapshot pairs + 410 exact-lag transitions = 2,485 conditions.
- Froze 89,460 directional hypotheses per annual segment and 1,073,520 nominal annual records across 12 segments.
- Required every annual record, including insufficient-support and negative evidence, to remain in the catalogue.
- Predeclared the cross-year recurrence/economics gate, rank order, Jaccard deduplication, and 270 global shortlist cap before results exist.
- Added no artifact read, historical execution/result, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker, real-money, or trading authority.

## 2026-10-02 — DEC-471 source-only annual catalogue miner

- Implemented Catalogue V1 in-memory annual mining without adding historical artifact access or execution.
- Enforced strict same-year prior-only continuous-state encoding with a 300-prior-row minimum.
- Enforced exact 60m/240m transition timestamps and same-segment outcome exits.
- Emits all 4,970 directional records per annual cell/horizon, including zero-support and negative evidence.
- Preserves base/stress means and medians, base win rate, canonical identities, annual identities, and event-set fingerprints.
- Contains no annual winner selection, reranking, cross-year result, Strategy V1 synthesis, promotion, or trading path.
- Next gate is the source-only annual catalogue evidence contract.

## 2026-10-02 — DEC-472 annual catalogue evidence contract

- Froze canonical serialization and semantic validation for each 4,970-record annual Catalogue V1 cell.
- Added nested semantic replay so rehashed tampering of pattern identities or statistics still fails closed.
- Bound each cell to code, processed-source, feature/outcome manifest, feature/outcome evidence, protocol, miner, and payload identities.
- Froze the full 12 annual segments × 18 cells = 216-cell aggregate inventory.
- Froze the total nominal catalogue size at 1,073,520 directional annual records.
- Required full aggregate replay to use summaries from semantically validated cell payloads.
- Kept historical reads/execution/results, cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker mutation, real-money, and trading authority false.

## 2026-10-02 — DEC-473 source-only annual catalogue full-history loader

- Added the verified loader source for the exact 2015-01 through 2026-08 EXP-044 materialized history.
- Reuses accepted feature/outcome artifacts and evidence only; adds no new data or feature/outcome materialization.
- Exposes one DEC-469 annual segment at a time across all 12 frozen segments.
- Verifies selected artifact path containment, size, SHA-256, schema, row count, manifests, processed-source identity, and aggregate evidence bindings.
- Filters outcomes that cross the requested annual boundary before any future miner execution.
- Keeps historical artifact-read authorization, catalogue execution/results, cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker, real-money, and trading authority false.
- Next gate is the source-only annual segment adapter; no runtime/workflow or historical execution was installed by DEC-473.

## 2026-10-02 — DEC-474 source-only annual catalogue segment adapter

- Added a verified-bundle-only adapter from DEC-473 segment frames to DEC-471 observation inputs.
- Removed the old EXP-061 2022 range ceiling only for this new annual-catalogue path; no historical read/execution authority was opened.
- Preserved processed-source, feature/outcome manifest, evidence fingerprint, and selected-artifact identities in the adapted bundle.
- Preserved the accepted canonical observation identity and exact timeframe/horizon timestamp checks.
- Preserved DEC-293 non-finite continuous-feature normalization to null.
- Enforced annual segment availability and outcome-exit boundaries again at the adapter layer.
- Kept historical artifact reads/execution/results, cross-year results, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker, real-money, and trading authority false.
- Next gate is source-only annual catalogue runtime wiring.

## 2026-10-02 — DEC-475 locked annual catalogue runtime wiring

- Composed the source-only annual catalogue path from authorization gate through DEC-473 loader, DEC-474 adapter, DEC-471 miner, and DEC-472 cell evidence compiler.
- Required the hard gate before the first filesystem-backed historical read.
- Kept historical artifact-read, catalogue execution, and result-production authority false, so the composed path is unreachable against historical artifacts.
- Added no workflow, workflow dispatch, aggregate cross-year comparison, Strategy V1 synthesis, or trading path.
- Next gate is a source-only annual catalogue workflow plan.

## 2026-10-02 — DEC-476 annual catalogue workflow plan

- Froze one annual segment as the future workflow/run unit.
- Froze exactly 18 cell jobs plus preflight and annual freeze per segment.
- Preserved the full 216-cell collection as 12 separately frozen annual runs rather than one bulk execution.
- Required segment order from 2015 through the 2026 partial segment.
- Required prior annual freeze before the next segment becomes authoritative.
- Forbade cross-year comparison inside an annual run and forbade a single 216-cell execution.
- Installed no workflow and opened no artifact-read, execution, result, Strategy V1, promotion, or trading authority.
- Next gate is the source-only annual-segment freeze evidence contract.

## 2026-10-02 — DEC-477 annual segment freeze contract

- Added an independently verifiable same-year freeze over exactly 18 validated DEC-472 cell summaries.
- Bound exactly 89,460 directional records per annual segment.
- Canonicalized annual cell order and rejected missing, duplicate, cross-year, or mixed-code inputs.
- Recomputed annual evaluable, zero-support, and total-support counts from the bound cells.
- Kept next-segment execution and cross-year comparison explicitly unauthorized after a valid freeze.
- Added no historical read/execution, Strategy V1 synthesis, promotion, Phase 8B, demo/live, broker, real-money, or trading authority.
- Next gate is source-only annual catalogue workflow source.

## 2026-10-02 — DEC-478 dormant annual catalogue workflow source

- Added a disabled one-segment annual-catalogue workflow template and gated CLI source.
- Kept the reserved active `.github/workflows/phase8a-annual-pattern-catalogue.yml` path absent.
- Reused exact accepted EXP-044 source snapshots only; added no new market data.
- Froze exactly 18 cell jobs plus preflight and annual freeze per chosen annual segment.
- Enforced the sequential annual dependency: every segment after 2015 must validate the immediately prior successful annual run and DEC-477 freeze before any cell can start.
- Fixed the freeze download pattern to require the same annual-segment cell products.
- Required the execution gate before cell source downloads and before annual-freeze result reads.
- Added no workflow installation/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, or trading authority.
- Next gate is the source-only workflow installation contract.

## 2026-10-02 — DEC-479 annual catalogue workflow installation contract

- Froze the exact future file-creation mutation from the disabled DEC-478 template to the reserved active workflow path.
- Bound exact source-module, CLI, and dormant-template Git blobs.
- Required the active path to remain absent before installation.
- Forbade source/template/CLI changes during the future install action and required byte-for-byte equality afterward.
- Kept repository mutation, workflow install/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, and trading authority false.
- Next gate is a source-only read-only installation preflight.
## 2026-10-02 — DEC-480 read-only annual workflow installation preflight

- Added a read-only preflight over the exact DEC-479 install contract and DEC-478 dormant workflow source.
- Bound the proof plan to exact `main` head metadata and target-path absence.
- Added canonical fingerprints for both the full preflight and embedded install action.
- Added semantic rejection of rehashed authority escalation.
- Required top-level `install_sources` evidence to exactly match the semantically validated DEC-479 source-validation payload, rejecting rehashed source-evidence substitution.
- Added a `plan`-only CLI with no install, execution, dispatch, or advance surface.
- Kept repository mutation, workflow install/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, and trading authority false.
- Next gate is repository-hosted read-only preflight proof.

## 2026-10-02 — DEC-481 repository-hosted install-preflight proof contract

- Added the evidence contract for a future repository-hosted read-only DEC-480 proof.
- Bound exact preflight source, main head, proof run identity, preflight fingerprint, and install-action fingerprint.
- Required exact successful manual proof run on main with run attempt 1.
- Retained run event, branch, head SHA, attempt, completed status, and successful conclusion in the frozen proof and semantically revalidated them after fingerprint verification.
- Added canonical proof fingerprint plus semantic authority validation.
- Added no proof workflow yet and no annual workflow install/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, or trading authority.
- Next gate is source-only proof-workflow source.

## 2026-10-02 — DEC-482 dormant install-preflight proof workflow source

- Added a disabled read-only workflow template for producing DEC-480 preflight evidence.
- Bound exact DEC-481 proof-contract and DEC-480 preflight-CLI blobs.
- Pinned the dormant proof-workflow template itself to exact Git blob `0d6c93e2af04501f9ac2589fd24d6672b2b41910`, so any template byte drift fails closed.
- Kept the proof workflow reserved active path absent.
- Limited the dormant workflow to main metadata fetch, plan-only preflight execution, and artifact upload.
- Explicitly excluded annual cell/freeze execution, workflow dispatch commands, and repository mutation.
- Kept proof/annual workflow install/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, and trading authority false.
- Next gate is the source-only proof-workflow installation contract.

## 2026-10-02 — DEC-483 proof-workflow installation contract

- Froze the exact future file-creation mutation from the pinned DEC-482 dormant proof template to its reserved active workflow path.
- Bound exact DEC-482 proof-workflow source and dormant-template Git blobs.
- Revalidated DEC-482 transitive DEC-481 proof-contract and DEC-480 preflight-CLI dependencies.
- Required the active proof-workflow path to remain absent before installation.
- Added exact action-key-set and nested source/mutation semantic validation.
- Kept repository mutation, proof/annual workflow install/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, and trading authority false.
- Next gate is a source-only read-only proof-workflow installation preflight.
## 2026-10-02 — DEC-484 read-only proof-workflow installation preflight

- Added a read-only preflight over the exact DEC-483 proof-workflow install contract.
- Bound exact current-main metadata, target-path absence, and validated DEC-483 source evidence.
- Added canonical fingerprints for the full preflight and embedded install action.
- Added exact top-level key-set validation plus semantic rejection of rehashed nested target/source, source-report substitution, authority escalation, and extra fields.
- Added a plan-only CLI with no install, execute, dispatch, or advance surface.
- Kept repository mutation, proof/annual workflow install/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, and trading authority false.
- Terminated proof-workflow installation recursion: a proof workflow is not required to prove installation of itself.
- Added an explicit operator-authorization-required marker while keeping all actual install/dispatch/execution/trading authority false.
- Superseded the unopened provisional DEC-485/486 recursive-bootstrap branches; they are non-authoritative and must not be opened or merged.
- Next gate is explicit operator authorization for the exact DEC-483 read-only proof-workflow file creation.

## 2026-10-03 — DEC-485 annual-catalogue preflight proof workflow installation

- Installed the active read-only proof workflow from the exact frozen dormant template.
- Active and dormant workflow Git blobs are both `0d6c93e2af04501f9ac2589fd24d6672b2b41910`.
- Added an installed-state receipt bound to DEC-484 source blob `ab434212007f3777fa4436a51268438ea44be6dd`.
- Records the single-file installation authorization as consumed and future repository mutation as locked.
- Keeps proof-workflow dispatch, annual-workflow install/dispatch, historical execution/results, cross-year results, Strategy V1 synthesis, promotion, and trading authority false.
- Splits CI current installed-state verification from the historical pre-install snapshot.
- Next gate is separate explicit proof-workflow dispatch authorization before any run.
## 2026-10-03 — DEC-486 proof-workflow dispatch preflight

- Added a read-only current-main preflight for the installed annual-catalogue proof workflow.
- Pins DEC-485 receipt and the exact active proof-workflow blob.
- Requires zero prior proof-workflow runs.
- Exposes only a plan CLI and no dispatch/run/execute surface.
- Keeps proof dispatch, annual workflow install/dispatch, historical execution/results, Strategy V1, promotion, and trading authority false.
## 2026-10-03 — DEC-487 first proof-workflow dispatch authorization

- Added explicit authorization for exactly one first manual proof-workflow dispatch.
- Pins DEC-486 preflight and the exact active proof-workflow blob.
- Scope is run #1 / attempt 1 only; rerun/retry/replacement remain false.
- Does not trigger the workflow.
- Keeps repository mutation, annual workflow install/dispatch, historical execution/results, Strategy V1, promotion, and trading authority false.
## 2026-10-03 — DEC-488 future proof-workflow run reviewer

- Added a strict read-only reviewer for the future first proof-workflow run.
- Pins DEC-487 authorization, DEC-481 proof contract, and exact active workflow.
- Requires first-run/attempt-1 success, successful job, unexpired exact-name artifact, and semantically valid preflight JSON.
- Records raw/canonical payload identities and embeds the validated repository-hosted proof.
- Adds no dispatch, annual-workflow, historical-execution, Strategy V1, or trading authority.
## 2026-10-03 — DEC-489 deterministic proof-run evidence freeze

- Added a deterministic freeze over a valid DEC-488 proof-run review.
- Pins the exact DEC-488 reviewer source.
- Preserves concrete evidence identities and emits one canonical freeze fingerprint when real evidence is supplied.
- Does not claim a runtime run before one exists.
- Adds no further proof dispatch, annual workflow, historical execution, Strategy V1, or trading authority.
## 2026-10-03 — DEC-490 concrete proof-workflow runtime evidence

- Bound the exact successful proof run/job/artifact identities.
- Recorded artifact ZIP and raw/canonical preflight SHA-256 identities.
- Recomputed and pinned DEC-480, DEC-481, DEC-489, and DEC-490 fingerprints.
- Marked the one-shot proof-dispatch authorization consumed.
- Kept further proof dispatch, repository mutation, annual workflow install/dispatch, historical execution, Strategy V1, and trading authority false.
## 2026-10-03 — DEC-491 annual workflow installed

- Recorded the consumed explicit annual-workflow installation authorization.
- Verified the active annual workflow is byte-identical to the frozen dormant template.
- Preserved manual-only trigger, read-only permissions, and all three execution gates.
- Marked the annual workflow installed/available.
- Kept workflow dispatch, annual catalogue execution/results, Strategy V1, promotion, and trading authority false.
## 2026-10-03 — DEC-492 2015 annual execution preflight

- Added a read-only preflight for the first 2015 annual-catalogue run.
- Pins the installed annual workflow, DEC-491 receipt, and DEC-475 locked runtime.
- Requires exact current main and zero prior annual-workflow runs.
- Encodes the 2015 no-predecessor invariant and expected run #1 / attempt 1.
- Adds no dispatch, historical execution/result, Strategy V1, promotion, or trading authority.
## 2026-10-03 — DEC-493 first 2015 execution authorization

- Recorded explicit authorization for annual segment 2015, run #1, attempt 1 only.
- Threaded the segment-scoped authorization through the existing runtime gate without opening the DEC-475 default path.
- Runtime now resolves the GitHub workflow-dispatch segment plus run number/attempt and rejects later segments or retries.
- Keeps 2016+, cross-year results, Strategy V1, promotion, and all trading authority false.
## 2026-10-03 — DEC-494 first 2015 dispatch preflight

- Added the read-only final preflight for the authorized first 2015 annual-catalogue run.
- Pins DEC-493 authorization/runtime and the exact installed annual workflow.
- Requires exact current main, zero prior annual-workflow runs, 2015, and run #1 / attempt 1.
- Adds no dispatch command and no later-year, Strategy V1, promotion, or trading authority.

## 2026-10-03 — DEC-495/496 first-2015 failure and upload repair

- Bound failed run `37126711695` as the consumed first 2015 attempt.
- Confirmed failure occurred after successful preflight validation and before any annual cell execution.
- Identified upload-artifact hidden-directory filtering as the failure mechanism.
- Repaired exactly three hidden artifact upload sites with `include-hidden-files: true`.
- Preserved the pre-repair workflow as a historical snapshot.
- Kept rerun, retry, replacement, 2016+, Strategy V1, promotion, and trading authority false.

## 2026-10-03 — DEC-497 2015 replacement-run preflight

- Added a read-only preflight for a possible replacement 2015 run.
- Requires the exact consumed failed run as the sole prior annual workflow run.
- Pins the DEC-495 failure receipt, DEC-496 upload repair, and repaired workflow.
- Expects replacement run #2 / attempt 1.
- Adds no replacement execution, 2016+, Strategy V1, promotion, or trading authority.

## 2026-10-03 — DEC-498 2015 replacement execution authorization

- Converted the standing autonomous-build instruction into a one-run replacement authorization.
- Authorized only 2015 run #2 / attempt 1 after the consumed failed first run.
- Threaded that exact identity through the live annual-catalogue runtime.
- Preserved the DEC-493 first-run runtime as an exact historical snapshot.
- Kept run #1 retry, run #3+, 2016+, Strategy V1, promotion, and all trading authority false.

## 2026-10-03 — DEC-499 final 2015 replacement dispatch preflight

- Added the final read-only launch preflight for the authorized repaired 2015 replacement run.
- Requires the single consumed failed run as the exact prior workflow inventory.
- Pins DEC-498 authorization, the live replacement runtime, and repaired workflow.
- Expects run #2 / attempt 1 and adds no embedded dispatch command.
- Keeps run #3+, 2016+, Strategy V1, promotion, and all trading authority false.

## 2026-10-03 — DEC-500 2015 replacement-run reviewer

- Added a semantic reviewer for the successful repaired 2015 replacement run.
- Requires exact run #2 / attempt 1, 20 successful jobs, and 20 unexpired artifacts.
- Validates the final DEC-477 annual-freeze evidence and freeze ZIP digest.
- Emits a canonical review fingerprint while keeping all later-year and trading authority false.

## 2026-10-03 — DEC-501 deterministic 2015 replacement-run freeze

- Added a deterministic freeze over the DEC-500 runtime review.
- Preserves exact run/job/artifact and DEC-477 annual-freeze identities.
- Emits one canonical freeze fingerprint.
- Keeps 2016+, Strategy V1, promotion, and all trading authority false.

## 2026-10-03 — DEC-502 concrete 2015 runtime evidence binding

- Added a canonical binding compiler over a valid DEC-501 runtime freeze.
- Requires exact concrete run/job/artifact inventory rather than placeholder identities.
- Preserves DEC-500 review, DEC-501 freeze, and DEC-477 annual-freeze identities.
- Emits one canonical binding fingerprint.
- Keeps 2016+, Strategy V1, promotion, and all trading authority false.

## 2026-10-03 — DEC-503 read-only 2016 execution preflight

- Added the first year-transition preflight over a concrete DEC-502 binding.
- Requires the exact failed-run + successful-replacement 2015 workflow history.
- Binds 2016 to predecessor 2015 and the successful 2015 freeze run id.
- Expects annual workflow run #3 / attempt 1 next.
- Adds no execution, Strategy V1, promotion, or trading authority.

## 2026-10-03 — DEC-504 source-only 2016 execution authorization

- Added a canonical authorization receipt over a valid DEC-503 preflight.
- Scopes authorization to 2016 run #3 / attempt 1 with predecessor 2015.
- Keeps live runtime installation and runtime gate activation false.
- Adds no 2017+, Strategy V1, promotion, or trading authority.
