# Phase 6 Statistical / ML Filter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and execute the predeclared `EXP-20260915-007` candidate-level ML filter experiment for the two frozen USDJPY Phase 4 strategies, with deterministic leakage-safe evidence and no access to the final-test period.

**Architecture:** Add a focused `fmp.models` package between existing strategy candidates and the accepted Phase 3 decision/risk/backtest machinery. Build fit/selection/validation examples by exact candidate/feature timestamp identity, label directional candidates with unchanged Phase 3 BID/ASK stop/target/time-exit semantics, fit exactly two frozen scikit-learn classifiers on 2015-2018, select at most one fit-derived filter per strategy on 2019-2020, then evaluate that frozen filter once on 2021-2023. Reuse existing Phase 4 strategy generators, `candidate_to_decision`, `run_backtest`, and `compute_research_metrics`; do not duplicate or weaken execution/risk logic.

**Tech Stack:** Python 3.11+, Polars 1.44.2, scikit-learn 1.9.1, NumPy/SciPy transitively pinned by the environment evidence, stdlib dataclasses/hashlib/json/zoneinfo, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md`

## Global Constraints

- Experiment ID exactly `EXP-20260915-007`.
- Candidate A exactly USDJPY 15m session breakout, buffer 5 pips, target 1.5x frozen range.
- Candidate B exactly USDJPY 1h volatility breakout, range multiplier 2.0x, fixed 1.0R target.
- Fit period exactly 2015-01-01 through 2018-12-31 inclusive.
- Selection period exactly 2019-01-01 through 2020-12-31 inclusive.
- External validation exactly 2021-01-01 through 2023-12-31 inclusive.
- Final untouched test 2024-01-01 through 2026-08-20 remains unavailable to normal Phase 6 code.
- `fmp-feature-v1` remains frozen at checkpoint `fmp-v1-phase5-features` / `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`.
- Accepted USDJPY processed-manifest SHA-256 remains `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Accepted Phase 5 USDJPY 15m artifact: ID `10374600839`, ZIP SHA-256 `2e9b19935fc2699c94e5c3b91675c332892da9448e994438e479cf501e3c6215`.
- Accepted Phase 5 USDJPY 1h artifact: ID `10374645600`, ZIP SHA-256 `3db4d9d4fd4613c9e91f4c3fc1d815750038e33ea993608513066cec53aa617f`.
- Input columns are exactly the 48 frozen Phase 5 feature values plus `signal_direction`; no target-aware feature selection.
- Primary label exactly `target_before_stop`.
- Model families exactly L2 logistic regression and shallow `HistGradientBoostingClassifier` with the spec parameters and seed `20260915`.
- Fit-derived retained fractions exactly 0.75, 0.50, 0.25.
- No refit after 2019-2020 selection; validation uses the exact 2015-2018-fitted preprocessing/model/cutoff.
- Financial evaluation always uses unchanged Phase 3 BID/ASK execution, costs, and risk policy.
- No strategy parameter retuning, probability sizing, cross-pair/cross-timeframe joins, AutoML, neural nets, broker/live/demo paths, or real-money trading.
- All source-free PR/merge titles retain `[phase1-no-source]`.

---

### Task 1: Formalize the approved Phase 6 protocol before model code

**Files:**
- Modify: `docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md`
- Modify: `docs/decision-log.md`
- Modify: `docs/project-state.md`
- Create: `tests/test_phase6_protocol_state.py`
- Modify only stale state assertions in existing tests if the full suite proves they still expect `Phase 6 — UNSTARTED`.

**Interfaces:**
- Consumes: approved written spec and Phase 5 checkpoint state.
- Produces: DEC-031, `Phase 6 — ACTIVE`, immutable `EXP-20260915-007` protocol guardrails.

- [ ] **Step 1: Write the failing protocol-state test.**

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Phase6ProtocolStateTests(unittest.TestCase):
    def test_dec031_freezes_phase6_without_unlocking_later_gates(self) -> None:
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        spec = (ROOT / "docs/superpowers/specs/2026-09-15-phase6-statistical-ml-filter-design.md").read_text(encoding="utf-8")
        self.assertIn("DEC-031 — Phase 6 statistical / ML filter protocol — APPROVED", decision)
        self.assertIn("**Status:** APPROVED", spec)
        self.assertIn("EXP-20260915-007", spec)
        self.assertIn("**Current phase:** Phase 6", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("## Phase 5 — PASS", state)
        self.assertIn("## Phase 6 — ACTIVE", state)
        self.assertIn("2024-01-01", state)
        self.assertIn("locked", state.lower())
        self.assertNotIn("## Phase 7 — ACTIVE", state)
```

- [ ] **Step 2: Run RED.**

Run: `python -m unittest tests.test_phase6_protocol_state -v`

Expected: FAIL because DEC-031 and ACTIVE state do not yet exist.

- [ ] **Step 3: Apply only protocol/state documentation changes.**

Set the spec status to `APPROVED`; add DEC-031 with the exact split/model/threshold/promotion/final-lock contract; change project state to Phase 6 ACTIVE while preserving Phase 5 PASS and all later locks.

- [ ] **Step 4: Run the focused test and full repository suite.**

Run:

```bash
python -m unittest tests.test_phase6_protocol_state -v
python -m unittest discover -s tests -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m compileall -q src tests
```

Expected: focused test PASS; if old tests fail only because they still assert Phase 6 UNSTARTED, update those assertions mechanically without weakening Phase 5 checkpoint/final-test locks.

- [ ] **Step 5: Commit and verify PR #105.**

Commit message: `[phase1-no-source] Freeze Phase 6 ML filter protocol`

PR #105 must remain source-free and contain no model implementation. Require tests + Phase 3 acceptance green and both Phase 1 source-capable PR jobs skipped before squash merge.

---

### Task 2: Add the exact modeling dependency and Phase 6 contracts

**Files:**
- Modify: `pyproject.toml`
- Create: `src/fmp/models/__init__.py`
- Create: `src/fmp/models/contracts.py`
- Create: `tests/test_phase6_contracts.py`

**Interfaces:**
- Produces: `Phase6Split`, `allowed_phase6_split(name)`, `FrozenStrategySpec`, `FROZEN_STRATEGIES`, `ModelFamily`, `EXPERIMENT_ID`, checkpoint/data identity constants.

- [ ] **Step 1: Write failing contract tests.**

```python
class Phase6ContractTests(unittest.TestCase):
    def test_split_surface_is_only_fit_selection_validation(self):
        from fmp.models.contracts import allowed_phase6_split
        self.assertEqual(allowed_phase6_split("fit").start.isoformat(), "2015-01-01")
        self.assertEqual(allowed_phase6_split("selection").end_exclusive.isoformat(), "2021-01-01")
        self.assertEqual(allowed_phase6_split("validation").end_exclusive.isoformat(), "2024-01-01")
        for forbidden in ("final", "development", "2024"):
            with self.assertRaises(ValueError):
                allowed_phase6_split(forbidden)

    def test_two_frozen_strategies_are_exact(self):
        from fmp.models.contracts import FROZEN_STRATEGIES
        self.assertEqual(tuple(FROZEN_STRATEGIES), ("session_breakout", "volatility_breakout"))
        self.assertEqual(FROZEN_STRATEGIES["session_breakout"].timeframe, "15m")
        self.assertEqual(FROZEN_STRATEGIES["volatility_breakout"].timeframe, "1h")
```

- [ ] **Step 2: Run RED.**

Run: `python -m unittest tests.test_phase6_contracts -v`

Expected: `ModuleNotFoundError: No module named 'fmp.models'`.

- [ ] **Step 3: Add `scikit-learn==1.9.1` and minimal contracts.**

Core contract:

```python
EXPERIMENT_ID = "EXP-20260915-007"
FEATURE_SET_VERSION = "fmp-feature-v1"
PHASE5_CHECKPOINT_SHA = "e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0"
USDJPY_PROCESSED_MANIFEST_SHA256 = "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d"
FINAL_START = date(2024, 1, 1)

FIT_SPLIT = Phase6Split("fit", date(2015,1,1), date(2019,1,1))
SELECTION_SPLIT = Phase6Split("selection", date(2019,1,1), date(2021,1,1))
VALIDATION_SPLIT = Phase6Split("validation", date(2021,1,1), date(2024,1,1))
```

`FrozenStrategySpec` must freeze symbol/timeframe/family and parameters, with no user-supplied strategy parameter surface.

- [ ] **Step 4: Run focused tests and dependency import smoke.**

Run:

```bash
python -m unittest tests.test_phase6_contracts -v
python -c "import sklearn; assert sklearn.__version__ == '1.9.1'"
```

- [ ] **Step 5: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 model contracts`

---

### Task 3: Add exact-range processed-bar and Phase 5 feature readers

**Files:**
- Modify: `src/fmp/research/data.py` only to add an exact-`ResearchSplit` reader adapter while preserving existing Phase 4 behavior.
- Create: `src/fmp/models/data.py`
- Create: `tests/phase6_helpers.py`
- Create: `tests/test_phase6_data.py`

**Interfaces:**
- Produces:
  - `load_processed_bars_for_split(..., split: ResearchSplit) -> LoadedResearchBars`
  - `load_phase6_feature_frame(feature_root, feature_manifest_path, strategy, split, parquet_reader=pl.read_parquet) -> LoadedModelFeatures`
  - `generate_frozen_candidates(strategy_id, bars) -> tuple[SignalCandidate, ...]`
  - `join_directional_candidates_to_features(candidates, features) -> pl.DataFrame`

- [ ] **Step 1: Write fail-before-open reader tests.**

Instrument both processed and feature Parquet readers and prove any split/range reaching 2024 raises before the opener is called. Also test feature manifest version, symbol/timeframe, processed-manifest identity, checkpoint identity, path escape, size/SHA verification, sorted/unique keys, and exact 49 model input columns.

```python
with self.assertRaisesRegex(ValueError, "final-test|2024"):
    load_phase6_feature_frame(..., split=ResearchSplit("bad", date(2023,12,1), date(2024,2,1)), parquet_reader=reader)
self.assertEqual(opened, [])
```

- [ ] **Step 2: Run RED.**

Run: `python -m unittest tests.test_phase6_data -v`

- [ ] **Step 3: Refactor the Phase 4 bar reader through a narrow exact-split helper.**

`load_processed_bars()` continues to call `allowed_split(split_name)` exactly as before, then delegates to the new helper. The new helper rejects `split.end_exclusive > 2024-01-01` before manifest I/O.

- [ ] **Step 4: Implement the Phase 5 artifact reader and join.**

Feature rows must satisfy:

```python
feature["bar_start_utc"] == candidate.observation_bar_timestamp_utc
feature["available_at_utc"] == candidate.signal_known_timestamp_utc
feature["feature_set_version"] == "fmp-feature-v1"
feature["processed_manifest_sha256"] == USDJPY_PROCESSED_MANIFEST_SHA256
```

`signal_direction` is `+1` LONG and `-1` SHORT. `NO_TRADE` candidates are excluded from model rows but retained separately for financial baseline accounting.

- [ ] **Step 5: Add future-perturbation join test.**

Perturb feature rows strictly after a cutoff and assert earlier candidate/model rows remain byte/value identical.

- [ ] **Step 6: Run focused + Phase 4 data regression tests.**

Run:

```bash
python -m unittest tests.test_phase6_data tests.test_phase4_research_data -v
```

- [ ] **Step 7: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 leakage-safe data joins`

---

### Task 4: Implement deterministic `target_before_stop` labels

**Files:**
- Create: `src/fmp/models/labels.py`
- Create: `tests/test_phase6_labels.py`

**Interfaces:**
- Produces `LabelResult(candidate_id, label: int | None, reason_code: str, resolved_timestamp_utc: datetime | None)`.
- Produces `label_candidate(candidate, bars) -> LabelResult` and `label_candidates(candidates, bars) -> tuple[LabelResult, ...]`.

- [ ] **Step 1: Write exact execution-semantics tests.**

Cover LONG/SHORT target-first, stop-first, same-bar dual hit => 0, mandatory time exit => 0, missing next bar, invalid executable-side geometry, missing exact exit, and missing path before resolution.

```python
result = label_candidate(candidate, bars)
self.assertEqual(result.label, 0)
self.assertEqual(result.reason_code, "STOP_FIRST_AMBIGUOUS")
```

- [ ] **Step 2: Run RED.**

Run: `python -m unittest tests.test_phase6_labels -v`

- [ ] **Step 3: Implement label resolution by reusing accepted execution helpers.**

Use `entry_reference_price` for geometry and a one-unit synthetic `Position` with zero slippage/commission/financing only to call `evaluate_exit`; label semantics depend on authoritative BID/ASK reachability, not risk state or PnL. At a bar whose timestamp equals the frozen scheduled exit, time exit wins before intrabar stop/target evaluation, matching `run_backtest` ordering.

Do not call portfolio risk logic when constructing labels.

- [ ] **Step 4: Add label-leakage boundary assertions.**

Every `resolved_timestamp_utc` must be `>= signal_known_timestamp_utc` and `< 2024-01-01`. A label request that would require a 2024 bar fails closed.

- [ ] **Step 5: Run focused + Phase 3 execution regression tests.**

Run:

```bash
python -m unittest tests.test_phase6_labels tests.test_phase3_execution tests.test_phase3_engine -v
```

- [ ] **Step 6: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 target-before-stop labels`

---

### Task 5: Implement fit-only preprocessing and exact estimators

**Files:**
- Create: `src/fmp/models/preprocessing.py`
- Create: `src/fmp/models/estimators.py`
- Create: `tests/test_phase6_preprocessing.py`
- Create: `tests/test_phase6_estimators.py`

**Interfaces:**
- `fit_preprocessor(frame, *, standardize: bool) -> PreprocessorState`
- `transform_features(frame, state) -> np.ndarray`
- `build_estimator(ModelFamily) -> ClassifierMixin`
- `fit_estimator(family, X, y) -> FittedEstimator`
- `score_estimator(fitted, X) -> np.ndarray`
- `score_digest(candidate_ids, scores) -> str`

- [ ] **Step 1: Write preprocessing RED tests.**

Prove medians/scaler are fit-only by perturbing selection/validation values and asserting state equality. Prove all-null fit column fails. Prove booleans and infinities become deterministic numeric/null handling.

- [ ] **Step 2: Implement `PreprocessorState`.**

State records input column order, medians, null counts, and optional scaler mean/scale. Use `SimpleImputer(strategy="median")` behavior only through explicitly captured medians so evidence is transparent; standardization is only for logistic regression.

- [ ] **Step 3: Write estimator RED tests.**

Assert exact `get_params()` values from the spec, exact seed, two identical fits produce identical score digests, and no hidden model family exists.

- [ ] **Step 4: Implement exact two estimators.**

Logistic regression and histogram boosting parameters must match the spec byte-for-byte in evidence. Capture convergence warnings for logistic regression as a hard model failure.

- [ ] **Step 5: Run focused tests twice.**

Run:

```bash
python -m unittest tests.test_phase6_preprocessing tests.test_phase6_estimators -v
python -m unittest tests.test_phase6_preprocessing tests.test_phase6_estimators -v
```

- [ ] **Step 6: Commit.**

Commit message: `[phase1-no-source] Add deterministic Phase 6 estimators`

---

### Task 6: Implement fit-only cutoffs and classification diagnostics

**Files:**
- Create: `src/fmp/models/thresholds.py`
- Extend: `src/fmp/models/evaluation.py` (classification-only functions initially)
- Create: `tests/test_phase6_thresholds.py`
- Create: `tests/test_phase6_diagnostics.py`

**Interfaces:**
- `derive_fit_cutoffs(scores) -> tuple[ScoreCutoff, ScoreCutoff, ScoreCutoff]`
- `classification_diagnostics(labels, scores, candidate_ids) -> dict[str, object]`

- [ ] **Step 1: Write exact cutoff tests.**

For each retained fraction `r`, assert index `min(N - 1, ceil((1-r)*N))`, admission rule `score >= cutoff`, tie behavior, and no dependence on selection scores.

- [ ] **Step 2: Run RED, then implement cutoff derivation.**

Run: `python -m unittest tests.test_phase6_thresholds -v`

- [ ] **Step 3: Write diagnostics tests.**

Use hand-checkable labels/scores to verify ROC-AUC, average precision, Brier score, prevalence, min/max/mean/median, and deterministic reliability bins sorted by `(score, candidate_id)` with chunk sizes differing by at most one.

- [ ] **Step 4: Implement diagnostics using sklearn metrics and explicit binning.**

One-class label inputs raise instead of fabricating AUC.

- [ ] **Step 5: Run focused tests.**

Run: `python -m unittest tests.test_phase6_thresholds tests.test_phase6_diagnostics -v`

- [ ] **Step 6: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 score gates and diagnostics`

---

### Task 7: Add explicit candidate filtering and unchanged financial evaluation

**Files:**
- Create: `src/fmp/models/filtering.py`
- Extend: `src/fmp/models/evaluation.py`
- Create: `tests/test_phase6_filtering.py`
- Create: `tests/test_phase6_evaluation.py`

**Interfaces:**
- `filter_candidates(candidates, score_by_candidate_id, cutoff, model_id) -> tuple[SignalCandidate, ...]`
- `run_candidate_backtest(..., candidates, slippage_pips) -> FinancialResult`
- `selection_gate(filtered, baseline) -> GateResult`
- `validation_gate(filtered_02, baseline_02, filtered_05, baseline_05) -> GateResult`
- `select_one_variant(rows) -> SelectedVariant | None`

- [ ] **Step 1: Write mutation-safety filter tests.**

Admitted candidates compare equal field-for-field to originals. Rejected directional candidates become `NO_TRADE` with the same candidate ID/timestamps and explicit metadata containing model ID, score, cutoff, original direction, feature identity, and reason `ML_FILTER_REJECTED`; stops/targets are not adjusted.

- [ ] **Step 2: Implement filtering.**

Existing strategy-generated `NO_TRADE` candidates pass through unchanged and are never assigned model scores.

- [ ] **Step 3: Write financial evaluation RED tests using patched/synthetic candidates.**

Prove `run_candidate_backtest` calls `candidate_to_decision`, `run_backtest`, and `compute_research_metrics` with Phase 3 `RiskConfig`, zero commission/financing, requested risk 0.0025, and exact slippage.

- [ ] **Step 4: Implement baseline/filtered evaluation and gates.**

Selection requires all eight spec conditions. Validation requires all baseline conditions plus yearly improvement in at least two of 2021/2022/2023 and the 0.5-pip robustness gate. The 1.0-pip row is diagnostic only.

- [ ] **Step 5: Implement deterministic tie-breaking.**

Ranking order is net-return improvement, expectancy improvement, PF improvement, lower DD, higher trades, logistic before histogram, then retained fraction 0.75 before 0.50 before 0.25.

- [ ] **Step 6: Run focused + Phase 3 regression tests.**

Run:

```bash
python -m unittest tests.test_phase6_filtering tests.test_phase6_evaluation -v
python -m unittest tests.test_phase3_acceptance tests.test_phase3_risk tests.test_phase3_engine -v
```

- [ ] **Step 7: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 filtering evaluation`

---

### Task 8: Orchestrate one complete strategy cell and freeze selection before validation

**Files:**
- Extend: `src/fmp/models/evaluation.py`
- Create: `tests/test_phase6_pipeline.py`
- Create: `tests/test_phase6_leakage.py`

**Interfaces:**
- `run_phase6_strategy_cell(*, dataset_root, processed_manifest_path, feature_root, feature_manifest_path, strategy_id, out_dir, code_commit) -> dict[str, object]`

- [ ] **Step 1: Write pipeline-order RED test with instrumented loaders.**

The call order must prove:

1. load fit bars/features;
2. load selection bars/features;
3. fit both models exactly once each;
4. derive cutoffs from fit only;
5. evaluate six selection variants;
6. write `selection.json` atomically;
7. only after `selection.json` exists may the validation loader be called;
8. selected estimator/preprocessor object is reused with no second `fit` call.

```python
def validation_loader(*args, **kwargs):
    self.assertTrue((out_dir / "selection.json").is_file())
    return validation_fixture
```

- [ ] **Step 2: Implement the fit/selection orchestration.**

Generate exact frozen candidates separately per split; label only directional candidates; join only exact feature identities. Fit model/preprocessor once on fit. Score fit+selection; evaluate six variants at 0.2 pips against rule-only baseline and freeze at most one selection.

- [ ] **Step 3: Write the selection artifact before validation I/O.**

`selection.json` contains strategy identity, fit dataset digest, preprocessing state, model configs, fit/selection score digests, three cutoffs per model, all six selection financial rows/gates, tie-break trace, and `selected_variant` or `NO_ML_CHALLENGER`.

- [ ] **Step 4: Implement validation without refit.**

If no challenger was selected, do not open validation merely to hunt for a winner; record `NO_ML_CHALLENGER`. If selected, load validation once, transform with frozen preprocessor, score with the same fitted estimator, and evaluate 0.2/0.5/1.0 pips plus rule-only baselines.

- [ ] **Step 5: Add leakage tests.**

Perturb selection/validation data and prove fit preprocessing/model score digest/cutoffs unchanged. Patch estimator `.fit` and assert call count remains exactly two for the whole strategy cell (once per model family), including validation.

- [ ] **Step 6: Run focused tests.**

Run: `python -m unittest tests.test_phase6_pipeline tests.test_phase6_leakage -v`

- [ ] **Step 7: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 chronological pipeline`

---

### Task 9: Add deterministic evidence writer and source-free CLI

**Files:**
- Create: `src/fmp/models/artifacts.py`
- Create: `src/fmp/models/cli.py`
- Create: `scripts/phase6_ml_filter.py`
- Create: `tests/test_phase6_artifacts.py`
- Create: `tests/test_phase6_cli.py`

**Interfaces:**
- `write_phase6_artifacts(result, out_dir) -> dict[str, object]`
- CLI accepts only the fixed strategy cell and immutable input locations; it exposes no split/date/final option.

- [ ] **Step 1: Write deterministic artifact tests.**

Two identical results written to different directories must produce byte-identical `selection.json`, `result.json`, and `manifest.json`. Manifest records SHA/size for each artifact and the runtime versions required by the spec.

- [ ] **Step 2: Enforce evidence lock.**

Writer rejects any timestamp/path/split containing or reaching 2024+, any unapproved strategy/model ID, any wrong feature/checkpoint/processed identity, and non-finite JSON values.

- [ ] **Step 3: Write CLI surface tests.**

```python
help_text = subprocess.run([sys.executable, "scripts/phase6_ml_filter.py", "--help"], ...).stdout
self.assertIn("session_breakout", help_text)
self.assertIn("volatility_breakout", help_text)
self.assertNotIn("--split", help_text)
self.assertNotIn("--start", help_text)
self.assertNotIn("final", help_text.lower())
```

- [ ] **Step 4: Implement CLI.**

Arguments: `--dataset-root`, `--processed-manifest`, `--feature-root`, `--feature-manifest`, `--strategy`, `--out`, `--code-commit`. Strategy choices exactly the two frozen IDs.

- [ ] **Step 5: Run focused tests.**

Run: `python -m unittest tests.test_phase6_artifacts tests.test_phase6_cli -v`

- [ ] **Step 6: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 evidence CLI`

---

### Task 10: Add the exact two-cell authoritative workflow

**Files:**
- Create: `.github/workflows/phase6-ml-filter.yml`
- Create: `tests/test_phase6_workflow.py`

**Interfaces:** manual, source-free workflow with exactly two USDJPY strategy/timeframe cells.

- [ ] **Step 1: Write workflow RED tests.**

Require:

- `workflow_dispatch` only;
- `contents: read`, `actions: read`, no OIDC;
- exact Phase 2 USDJPY artifact ID/digest + processed manifest SHA;
- exact Phase 5 USDJPY 15m and 1h artifact IDs/digests;
- exactly two strategy cells;
- no 1m, no EURUSD/GBPUSD, no arbitrary split/date inputs;
- no Dukascopy/Supabase/raw/broker/live/demo path;
- two independent executions per cell and byte comparison;
- evidence upload.

- [ ] **Step 2: Run RED.**

Run: `python -m unittest tests.test_phase6_workflow -v`

- [ ] **Step 3: Implement workflow.**

For each cell, download and verify the accepted Phase 2 ZIP and matching accepted Phase 5 ZIP before unzip/read. Run `scripts/phase6_ml_filter.py` twice into separate directories with the same `GITHUB_SHA`, compare all deterministic evidence bytes/digests, assert no evidence timestamp/path reaches 2024, then upload one evidence directory.

- [ ] **Step 4: Run workflow/YAML/unit validation.**

Run:

```bash
python -m unittest tests.test_phase6_workflow -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

- [ ] **Step 5: Commit.**

Commit message: `[phase1-no-source] Add Phase 6 ML experiment workflow`

---

### Task 11: Pre-merge implementation verification and merge

**Files:** no new durable files unless review finds a defect.

- [ ] **Step 1: Compare implementation branch to the protocol-merged `main`.**

Require only planned dependency/model/tests/script/workflow changes. No Phase 4 strategy config changes, no Phase 3 risk/execution changes, no Phase 5 feature-semantic changes.

- [ ] **Step 2: Run complete verification on the exact durable head.**

Require repository tests, YAML validation, compile, unchanged Phase 3 acceptance; Phase 1 source-capable PR jobs must skip.

- [ ] **Step 3: Run `git diff --check origin/main...HEAD` using a temporary source-free checker if the harness still lacks a local clone.**

Delete the checker before merge and re-run clean-head CI.

- [ ] **Step 4: Squash merge implementation with expected head SHA and `[phase1-no-source]` title.**

- [ ] **Step 5: Post-merge verify exact merged SHA.**

Do not dispatch Phase 6 experiment until merged-main repository tests + unchanged Phase 3 acceptance are SUCCESS.

---

### Task 12: Execute and independently audit `EXP-20260915-007`

**Files:** no source changes during authoritative result generation.

- [ ] **Step 1: Manually dispatch `.github/workflows/phase6-ml-filter.yml` on exact verified merged `main`.**

If the connector still has no direct dispatch action, use the existing temporary branch-only dispatcher pattern, never merging the dispatcher.

- [ ] **Step 2: Require both strategy cells SUCCESS.**

Each cell must prove input ZIP identities, deterministic double execution, selection freeze before validation, and pre-2024 coverage.

- [ ] **Step 3: Download both evidence ZIPs and audit independently.**

Verify GitHub artifact digest, exact ZIP membership, inner manifest SHA/size, code commit, Phase 5 checkpoint/data identity, model configs, preprocessing fit-only state, fit/selection/validation score digests, cutoff formula, all six selection rows, selection gate/tie-break, zero refit evidence, validation cost rows if selected, final conclusion, and absence of any 2024+ path/timestamp/metric.

- [ ] **Step 4: Recompute promotion logic from evidence instead of trusting the result flag.**

Outcome may be `PROMOTE_ML_FILTER` for one/both strategies or `REJECT_ML_FILTER` for both. Do not retune after seeing results.

---

### Task 13: Record the Phase 6 experiment outcome and close/checkpoint Phase 6

**Files:**
- Create: `docs/phase6-ml-filter-evidence.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/decision-log.md`
- Modify: `docs/project-state.md`
- Create: `tests/test_phase6_acceptance_state.py`
- Later create/update checkpoint-state guard after tag creation.

**Interfaces:** DEC-032 records the outcome/acceptance only after independent evidence audit.

- [ ] **Step 1: Write acceptance-state RED test before evidence docs.**

The test must require `EXP-20260915-007`, authoritative run ID, both audited cells, `Final-test touched?: NO`, the actual promote/reject outcome, Phase 6 PASS, Phase 7 UNSTARTED, and checkpoint PENDING.

- [ ] **Step 2: Record evidence and DEC-032 without changing the predeclared protocol.**

Phase 6 PASS is permitted whether ML wins or is rejected, provided both cells completed correctly. Preserve failed variants and all negative evidence.

- [ ] **Step 3: Merge source-free closure PR after full regression and Phase 3 acceptance.**

- [ ] **Step 4: Create immutable checkpoint `fmp-v1-phase6-models` at the verified closure merge SHA.**

Use the same isolated tag-helper convention as Phase 4/5 if no direct tag action exists; verify the tag resolves directly to the closure commit.

- [ ] **Step 5: Record checkpoint in a separate source-free bookkeeping PR and reverify.**

Phase 7 remains UNSTARTED; the final-test period remains locked. No final-test access follows automatically from this checkpoint.
