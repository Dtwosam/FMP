# Phase 7 Walk-Forward Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement `EXP-20260915-008` as a deterministic, promotion-only Phase 7 evaluator that first applies the frozen 2024 out-of-sample gate and, only for Stage 1 survivors, evaluates seven fixed 2025-2026 walk-forward windows without weakening any existing Phase 4/6 final-test guard.

**Architecture:** Add a focused `fmp.walkforward` package whose contracts enumerate the only authorized Phase 7 candidates, scored ranges, warm-up rules, cost scenarios, and promotion gates. Reuse the existing frozen Phase 4 strategy generators, `candidate_to_decision`, accepted Phase 3 backtester, risk policy, and research metrics; do not duplicate strategy, execution, sizing, or cost logic. Keep Stage 1 and Stage 2 as separate manual GitHub Actions workflows, with Stage 2 requiring a verified Stage 1 PASS identity before any required 2025/2026 partition is opened.

**Tech Stack:** Python 3.11+ / GitHub Actions Python 3.12, Polars 1.44.2, existing FMP Phase 2/3/4 research stack, stdlib dataclasses/hashlib/json/pathlib, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-phase7-walk-forward-design.md`

## Global Constraints

- Experiment ID exactly `EXP-20260915-008`.
- Protocol decision exactly `DEC-033` once recorded in the source-of-truth decision log.
- Phase 6 checkpoint identity exactly `fmp-v1-phase6-models` / `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`.
- Accepted USDJPY Phase 2 processed-manifest SHA-256 exactly `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`.
- Accepted USDJPY Phase 2 artifact ID exactly `10327600628`; ZIP SHA-256 exactly `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`.
- Candidate A exactly USDJPY 15m `session_breakout`, `buffer_pips=5`, `target_range_multiple=1.5`.
- Candidate B exactly USDJPY 1h `volatility_breakout`, `range_multiplier=2.0`, `target_r=1.0`.
- No ML overlay, feature selection, estimator, score threshold, parameter tuning, rescue search, neighboring-parameter substitution, or candidate replacement is allowed.
- Stage 1 scored range exactly `[2024-01-01, 2025-01-01)`.
- Stage 1 warm-up may cover only the immediately preceding seven calendar days, no earlier than `2023-12-25T00:00:00Z`, and may never contribute a scored candidate, decision, trade, PnL, or metric observation.
- Stage 2 windows are exactly `2025-Q1`, `2025-Q2`, `2025-Q3`, `2025-Q4`, `2026-Q1`, `2026-Q2`, and `2026-partial-Q3` ending exclusively at `2026-08-21`.
- Every Stage 2 window starts at exactly `$100,000` and records `refit_status = NOT_APPLICABLE_FIXED_RULE`.
- Slippage scenarios are exactly `0.2`, `0.5`, and `1.0` pips per fill; 0.2 and 0.5 are gating, 1.0 is diagnostic only.
- Commission and financing remain zero; historical BID/ASK spread remains inherent in Phase 3 execution.
- Requested risk remains 0.25%; hard max per trade 0.50%; simultaneous open risk max 1.00%; daily realized-loss halt 1.50% of UTC day-start realized risk equity.
- Stage 1 requires, at both 0.2 and 0.5 pips: positive net return, positive expectancy, profit factor > 1.0, max drawdown <= 5%; completed trades >= 40 is checked at 0.2 only.
- Stage 2 aggregate at 0.2 requires positive net return, positive expectancy, profit factor > 1.0, at least 100 completed trades, max drawdown <= 5%.
- Stage 2 aggregate at 0.5 requires positive net return, positive expectancy, profit factor > 1.0, max drawdown <= 5%.
- Stage 2 stability at 0.2 requires at least four of seven windows with positive net PnL and no single positive window contributing more than 50% of total positive-window PnL.
- Aggregate max drawdown is the maximum independent-window drawdown, never a synthetic chained-equity drawdown.
- Existing `fmp.research` and `fmp.models` 2024+ guards remain unchanged and continue failing before manifest/Parquet I/O.
- Phase 7 exposes no generic `allow_final`, arbitrary date range, arbitrary strategy, arbitrary parameter, or arbitrary symbol/timeframe surface.
- Stage 2 must fail before required 2025/2026 data I/O unless a Stage 1 PASS artifact for the exact candidate/data/experiment identity is verified.
- Runtime clocks, hostnames, UUIDs, random ordering, temporary paths, and nondeterministic metadata are forbidden from evidence bytes.
- Phase 7 PASS only makes a candidate eligible for Phase 8 shadow design. It does not authorize broker integration, demo execution, live trading, or real-money trading.
- All source-free PR/merge titles retain `[phase1-no-source]`.

---

### Task 1: Record the approved Phase 7 protocol without opening final-test data

**Files:**
- Modify: `docs/superpowers/specs/2026-09-15-phase7-walk-forward-design.md`
- Modify: `docs/decision-log.md`
- Modify: `docs/project-state.md`
- Modify: `docs/experiment-log.md`
- Create: `tests/test_phase7_protocol_state.py`
- Modify only stale Phase 6 state assertions that still require `Phase 7 — UNSTARTED` after DEC-033 is recorded.

**Interfaces:**
- Consumes: approved Phase 7 written design and immutable Phase 6 checkpoint.
- Produces: `DEC-033`, `EXP-20260915-008` PLANNED registration, Phase 7 ACTIVE implementation state, and an explicit statement that final-test data remains untouched until guarded Phase 7 implementation is merged and intentionally dispatched.

- [ ] **Step 1: Write the failing protocol-state test.**

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Phase7ProtocolStateTests(unittest.TestCase):
    def test_dec033_activates_implementation_without_claiming_data_access(self) -> None:
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")
        experiments = (ROOT / "docs/experiment-log.md").read_text(encoding="utf-8")
        spec = (ROOT / "docs/superpowers/specs/2026-09-15-phase7-walk-forward-design.md").read_text(encoding="utf-8")

        self.assertIn("DEC-033 — Phase 7 walk-forward evaluation protocol", decision)
        self.assertIn("**Status:** APPROVED", spec)
        self.assertIn("EXP-20260915-008", experiments)
        self.assertIn("- Status: PLANNED", experiments)
        self.assertIn("**Current phase:** Phase 7", state)
        self.assertIn("**Phase status:** ACTIVE", state)
        self.assertIn("Final-test touched: NO", state)
        self.assertIn("guarded Phase 7", state)
        self.assertNotIn("## Phase 8 — ACTIVE", state)
```

- [ ] **Step 2: Run RED.**

Run: `python -m unittest tests.test_phase7_protocol_state -v`

Expected: FAIL because DEC-033, EXP-008, and Phase 7 ACTIVE state do not yet exist.

- [ ] **Step 3: Apply the approved source-of-truth updates only.**

Record DEC-033 with the exact approved Stage 1/Stage 2 ranges and gates. Mark the design spec `APPROVED`. Register EXP-008 as PLANNED with `Final-test touched?: NO`. Set Phase 7 ACTIVE for implementation while stating that no 2024+ partition may be opened by existing tooling and no Phase 7 partition may be opened until the guarded implementation is merged and the corresponding manual workflow is deliberately dispatched.

- [ ] **Step 4: Run focused and repository-wide source-free verification.**

Run:

```bash
python -m unittest tests.test_phase7_protocol_state -v
python -m unittest discover -s tests -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m compileall -q src tests
```

Expected: PASS. Any stale state test may be updated only mechanically from `Phase 7 — UNSTARTED` to the new protocol state; Phase 6 checkpoint identity and all Phase 8+/broker/live locks must remain asserted.

- [ ] **Step 5: Commit the protocol activation.**

Commit message: `[phase1-no-source] Activate Phase 7 walk-forward protocol`

No runtime Phase 7 code and no 2024+ data access belongs in this commit.

---

### Task 2: Add exact Phase 7 contracts and candidate identities

**Files:**
- Create: `src/fmp/walkforward/__init__.py`
- Create: `src/fmp/walkforward/contracts.py`
- Create: `tests/test_phase7_contracts.py`

**Interfaces:**
- Produces `Phase7Window`, `FrozenPhase7Candidate`, `STAGE1_WINDOW`, `STAGE2_WINDOWS`, `FROZEN_CANDIDATES`, `SLIPPAGE_SCENARIOS`, `GATING_SLIPPAGE_SCENARIOS`, `EXPERIMENT_ID`, Phase 2/6 identity constants, and `allowed_phase7_window(name)`.
- No interface accepts free-form dates or free-form strategy parameters.

- [ ] **Step 1: Write failing contract tests for the complete authorized surface.**

```python
class Phase7ContractTests(unittest.TestCase):
    def test_stage1_and_stage2_windows_are_exact(self) -> None:
        from fmp.walkforward.contracts import STAGE1_WINDOW, STAGE2_WINDOWS

        self.assertEqual(STAGE1_WINDOW.start.isoformat(), "2024-01-01")
        self.assertEqual(STAGE1_WINDOW.end_exclusive.isoformat(), "2025-01-01")
        self.assertEqual(len(STAGE2_WINDOWS), 7)
        self.assertEqual(STAGE2_WINDOWS[0].name, "2025-Q1")
        self.assertEqual(STAGE2_WINDOWS[-1].end_exclusive.isoformat(), "2026-08-21")

    def test_candidate_surface_is_exactly_two_frozen_rules(self) -> None:
        from fmp.walkforward.contracts import FROZEN_CANDIDATES

        self.assertEqual(tuple(FROZEN_CANDIDATES), ("session_breakout", "volatility_breakout"))
        self.assertEqual(FROZEN_CANDIDATES["session_breakout"].parameters["buffer_pips"], 5)
        self.assertEqual(FROZEN_CANDIDATES["volatility_breakout"].parameters["range_multiplier"], 2.0)

    def test_arbitrary_window_is_rejected(self) -> None:
        from fmp.walkforward.contracts import allowed_phase7_window

        for forbidden in ("final", "2024-Q1", "custom", "development"):
            with self.assertRaises(ValueError):
                allowed_phase7_window(forbidden)
```

- [ ] **Step 2: Run RED.**

Run: `python -m unittest tests.test_phase7_contracts -v`

Expected: `ModuleNotFoundError: No module named 'fmp.walkforward'`.

- [ ] **Step 3: Implement immutable contracts.**

Use frozen dataclasses / mapping proxies. Define exactly:

```python
EXPERIMENT_ID = "EXP-20260915-008"
PHASE6_CHECKPOINT_SHA = "5d387b7ca93d04c498eb04c376e0dd92f1fe1953"
USDJPY_PROCESSED_MANIFEST_SHA256 = "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d"
USDJPY_PHASE2_ARTIFACT_ID = 10327600628
USDJPY_PHASE2_ZIP_SHA256 = "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
GATING_SLIPPAGE_SCENARIOS = (0.2, 0.5)
MAX_WARMUP_DAYS = 7
STARTING_EQUITY_USD = 100_000.0
REQUESTED_RISK_FRACTION = 0.0025
```

`allowed_phase7_window()` must resolve only the eight named Stage 1/Stage 2 windows and must never construct a caller-selected range.

- [ ] **Step 4: Run focused tests.**

Run: `python -m unittest tests.test_phase7_contracts -v`

- [ ] **Step 5: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 frozen contracts`

---

### Task 3: Add promotion-only processed-data loading with fail-before-I/O guards

**Files:**
- Create: `src/fmp/walkforward/data.py`
- Create: `tests/phase7_helpers.py`
- Create: `tests/test_phase7_data.py`
- Regression-only: `tests/test_phase4_research_data.py`, `tests/test_phase6_data.py` must continue passing unchanged unless an assertion must be strengthened.

**Interfaces:**
- Produces `LoadedPhase7Bars` with `bars`, `scored_bars`, `eligible_scored_dates`, `opened_partition_keys`, and `warmup_range`.
- Produces `load_phase7_bars(dataset_root, manifest_path, candidate_id, window_name, parquet_reader=pl.read_parquet) -> LoadedPhase7Bars`.
- The function derives allowed scored/warm-up ranges from contracts; it accepts no start/end arguments.

- [ ] **Step 1: Write fail-before-I/O tests.**

Instrument manifest and Parquet openers. Prove invalid candidate/window, excessive warm-up, post-endpoint range, and any contract mismatch raises before source reads.

```python
opened = []

def reader(path):
    opened.append(path)
    raise AssertionError("reader must not be called")

with self.assertRaises(ValueError):
    load_phase7_bars(
        dataset_root=root,
        manifest_path=manifest,
        candidate_id="session_breakout",
        window_name="custom-2024",
        parquet_reader=reader,
    )
self.assertEqual(opened, [])
```

- [ ] **Step 2: Write exact partition-accounting tests.**

Synthetic manifests must prove Stage 1 opens only the monthly artifacts needed for the exact 2024 scored range plus allowed 2023 warm-up, never a 2025/2026 required partition. Stage 2 window tests must prove only the named forward window plus immediately preceding warm-up context is read. Path escape, wrong schema, wrong symbol, wrong manifest SHA, duplicate bar identity, malformed cadence, and missing required columns fail closed.

- [ ] **Step 3: Run RED.**

Run: `python -m unittest tests.test_phase7_data -v`

- [ ] **Step 4: Implement the isolated reader without modifying normal Phase 4/6 guards.**

Reuse only safe low-level schema/QuoteBar conversion behavior. Do not call `allowed_split("final")`, do not add `allow_final`, and do not change `_FINAL_TEST_START` / `FINAL_START` in existing modules.

The reader must separately tag source bars as warm-up or scored by timestamp. A warm-up bar may support strategy state but can never appear in `eligible_scored_dates` or scored metrics.

- [ ] **Step 5: Add regression proof that existing locks remain intact.**

Run:

```bash
python -m unittest tests.test_phase7_data tests.test_phase4_research_data tests.test_phase6_data -v
```

Expected: all PASS and existing Phase 4/6 final-test guard tests remain unchanged.

- [ ] **Step 6: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 guarded data reader`

---

### Task 4: Evaluate one frozen candidate in one approved window

**Files:**
- Create: `src/fmp/walkforward/evaluation.py`
- Create: `tests/test_phase7_evaluation.py`

**Interfaces:**
- Produces `WindowFinancialResult` containing candidate/window/cost identity, candidate counts, scored trade metrics, gross profit/loss, run identity, warm-up/opened-partition accounting, and `refit_status`.
- Produces `evaluate_phase7_window(*, loaded: LoadedPhase7Bars, candidate_id: str, window_name: str, code_commit: str, slippage_pips: float) -> WindowFinancialResult`.

- [ ] **Step 1: Write RED tests proving exact frozen strategy generation.**

Patch/spies must verify session breakout uses only `SessionBreakoutConfig(buffer_pips=5, target_range_multiple=1.5, timeframe="15m")` and volatility breakout uses only `VolatilityBreakoutConfig(range_multiplier=2.0, timeframe="1h")`; no grid function may be invoked.

- [ ] **Step 2: Write warm-up exclusion tests.**

Create synthetic bars where a valid setup exists only in warm-up and another after the boundary. Assert only the post-boundary candidate can become a scored decision/trade. Verify starting equity at every window boundary is exactly `$100,000`.

- [ ] **Step 3: Write Phase 3 reuse tests.**

Assert decisions are created through `candidate_to_decision`, execution through `run_backtest`, metrics through `compute_research_metrics`, and the frozen `RiskConfig()` / zero commission / zero financing contract is reflected in run identity.

- [ ] **Step 4: Run RED.**

Run: `python -m unittest tests.test_phase7_evaluation -v`

- [ ] **Step 5: Implement minimal evaluation.**

Generate strategy state from warm-up + scored bars, then filter candidate eligibility by signal-known/execution range so warm-up opportunities are not scored. Set:

```python
refit_status = "NOT_APPLICABLE_FIXED_RULE"
```

The backtest requested range must exactly match the scored window, not the warm-up start.

- [ ] **Step 6: Run focused and core execution regressions.**

Run:

```bash
python -m unittest tests.test_phase7_evaluation tests.test_phase3_engine tests.test_phase4_session_breakout tests.test_phase4_volatility_breakout -v
```

- [ ] **Step 7: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 window evaluation`

---

### Task 5: Implement pure Stage 1 and Stage 2 promotion gates

**Files:**
- Create: `src/fmp/walkforward/gates.py`
- Create: `tests/test_phase7_gates.py`

**Interfaces:**
- Produces `GateResult(passed: bool, criteria: Mapping[str, bool])`.
- Produces `stage1_gate(results_by_slippage) -> GateResult`.
- Produces `aggregate_windows(results) -> AggregateFinancialResult`.
- Produces `stage2_gate(results_by_slippage) -> GateResult`.

- [ ] **Step 1: Write boundary-complete Stage 1 tests.**

Cover exactly 39/40 trades, zero/positive return, zero/positive expectancy, PF exactly 1.0 versus >1.0, drawdown exactly 5% versus >5%, and independent failure at 0.2 or 0.5. Assert 1.0-pip results never affect Stage 1 PASS.

- [ ] **Step 2: Write aggregate construction tests.**

Use seven handcrafted windows and verify:

```python
aggregate.net_return == sum(window.net_return for window in windows)
aggregate.trade_count == sum(window.trade_count for window in windows)
aggregate.net_pnl_usd == sum(window.net_pnl_usd for window in windows)
aggregate.expectancy_usd == aggregate.net_pnl_usd / aggregate.trade_count
aggregate.max_drawdown_fraction == max(window.max_drawdown_fraction for window in windows)
```

Profit factor must be computed from summed gross profit and absolute summed gross loss using the existing Phase 3 zero-loss convention.

- [ ] **Step 3: Write Stage 2 stability boundary tests.**

Cover 3/7 versus 4/7 positive windows, concentration exactly 50% versus >50%, 99/100 trades, and independent 0.5-pip gate failures. Assert 1.0-pip evidence is diagnostic only.

- [ ] **Step 4: Run RED.**

Run: `python -m unittest tests.test_phase7_gates -v`

- [ ] **Step 5: Implement pure gate functions.**

No gate function may perform I/O, select a candidate, change parameters, or look at non-gating 1.0-pip results when computing `passed`.

- [ ] **Step 6: Run focused tests.**

Run: `python -m unittest tests.test_phase7_gates -v`

- [ ] **Step 7: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 promotion gates`

---

### Task 6: Build deterministic Stage 1 and Stage 2 evidence artifacts

**Files:**
- Create: `src/fmp/walkforward/artifacts.py`
- Create: `tests/test_phase7_artifacts.py`

**Interfaces:**
- Produces `write_stage1_evidence(...)` and `write_stage2_evidence(...)`.
- Stage 1 writes deterministic `stage1.json`, `result.json`, and `manifest.json`.
- Stage 2 writes deterministic `windows.json`, `result.json`, and `manifest.json`, preserving the verified Stage 1 identity.

- [ ] **Step 1: Write exact schema/identity tests.**

Assert every artifact records experiment ID, code commit, Phase 6 checkpoint SHA, Phase 2 manifest SHA, candidate ID/version/parameters, symbol/timeframe, risk/cost identity, scored range(s), actual warm-up range(s), opened monthly partitions, gate criteria, and deterministic constituent file SHA-256 values.

- [ ] **Step 2: Write determinism tests.**

Write identical evidence twice into different temporary directories and assert every file byte-for-byte equal. Scan serialized bytes to prove they contain no temp root, hostname, UUID-like runtime value, current timestamp, or nondeterministic ordering.

- [ ] **Step 3: Write Stage 1 decision tests.**

`result.json` must distinguish `STAGE1_PASS`, `STAGE1_REJECT`, and per-candidate status without converting a negative but valid experiment into an execution error.

- [ ] **Step 4: Write Stage 2 decision tests.**

Final result must distinguish `PHASE7_PROMOTE_TO_SHADOW_DESIGN` from `PHASE7_COMPLETE_REJECT`. A completed rejection is durable evidence, not a workflow failure.

- [ ] **Step 5: Run RED.**

Run: `python -m unittest tests.test_phase7_artifacts -v`

- [ ] **Step 6: Implement stable JSON and manifest hashing.**

Use sorted keys and canonical separators. Compute manifest constituent digests only after content files are finalized; do not include the manifest's own digest recursively.

- [ ] **Step 7: Run focused tests.**

Run: `python -m unittest tests.test_phase7_artifacts -v`

- [ ] **Step 8: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 deterministic evidence`

---

### Task 7: Add Stage 1 / Stage 2 CLI surfaces with explicit authorization checks

**Files:**
- Create: `src/fmp/walkforward/cli.py`
- Create: `scripts/phase7_final_gate.py`
- Create: `scripts/phase7_walk_forward.py`
- Create: `tests/test_phase7_cli.py`

**Interfaces:**
- Stage 1 CLI accepts dataset root, exact processed manifest path, candidate ID, output path, and code commit. It accepts no date arguments.
- Stage 2 CLI additionally requires a Stage 1 evidence directory or exact Stage 1 PASS record to verify before data loading.

- [ ] **Step 1: Write CLI parser tests proving there are no free-form date/parameter flags.**

Assert `--start`, `--end`, `--buffer-pips`, `--range-multiplier`, `--timeframe`, `--symbol`, and generic `--allow-final` are unrecognized.

- [ ] **Step 2: Write Stage 2 authorization tests.**

Before invoking any data loader, reject: missing Stage 1 evidence; Stage 1 REJECT; wrong experiment ID; wrong candidate ID; wrong Phase 2 manifest SHA; wrong Phase 6 checkpoint SHA; tampered constituent digest; malformed Stage 1 manifest; or Stage 1 output that does not cover exact 2024 Stage 1.

- [ ] **Step 3: Run RED.**

Run: `python -m unittest tests.test_phase7_cli -v`

- [ ] **Step 4: Implement minimal stage-specific CLIs.**

Stage 1 runs exactly one frozen candidate across all three cost scenarios and writes Stage 1 evidence. Stage 2 runs exactly all seven named windows for one verified Stage 1 survivor and writes Stage 2 evidence. Both require non-empty `code_commit`.

- [ ] **Step 5: Add an I/O-spy proof for Stage 2 fail-closed authorization.**

Tampered/failed Stage 1 evidence must leave the Phase 7 Parquet opener call list empty.

- [ ] **Step 6: Run focused tests.**

Run: `python -m unittest tests.test_phase7_cli -v`

- [ ] **Step 7: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 guarded CLIs`

---

### Task 8: Add the manual Stage 1 final-gate workflow

**Files:**
- Create: `.github/workflows/phase7-final-gate.yml`
- Create: `tests/test_phase7_final_gate_workflow.py`

**Interfaces:**
- Manual `workflow_dispatch` only.
- Matrix exactly `session_breakout` and `volatility_breakout`.
- Uses accepted Phase 2 USDJPY artifact `10327600628`, ZIP SHA `6ee632...`, manifest SHA `e47ee...`.

- [ ] **Step 1: Write workflow-structure tests.**

Assert manual-only trigger, `contents: read`, `actions: read`, exact two-candidate matrix, no Phase 5 artifacts, no Phase 1 acquisition action, no Supabase write secret, no broker credentials, and no arbitrary workflow inputs controlling dates/parameters.

- [ ] **Step 2: Write deterministic-evidence workflow tests.**

The YAML must execute Stage 1 twice per candidate into separate output roots, compare the complete file lists and every file byte-for-byte, inspect evidence coverage, and upload only the verified first copy.

- [ ] **Step 3: Run RED.**

Run: `python -m unittest tests.test_phase7_final_gate_workflow -v`

- [ ] **Step 4: Implement the workflow.**

Pattern the immutable Phase 2 download/checksum verification after `phase6-ml-filter.yml`. Add an inline evidence audit that fails if any scored range is outside 2024, any required opened partition is 2025+, warm-up starts before 2023-12-25, or immutable identities differ.

- [ ] **Step 5: Run workflow and YAML tests.**

Run:

```bash
python -m unittest tests.test_phase7_final_gate_workflow -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
```

Do **not** dispatch the workflow in this implementation task.

- [ ] **Step 6: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 final gate workflow`

---

### Task 9: Add the Stage 2 walk-forward workflow with Stage 1 evidence authorization

**Files:**
- Create: `.github/workflows/phase7-walk-forward.yml`
- Create: `tests/test_phase7_walk_forward_workflow.py`

**Interfaces:**
- Manual `workflow_dispatch` only.
- Requires explicit candidate and exact Stage 1 evidence artifact identity, but no date/parameter inputs.
- Downloads/verifies Stage 1 PASS evidence before invoking any Stage 2 CLI/data access.

- [ ] **Step 1: Write workflow authorization-order tests.**

Parse YAML/text and assert Stage 1 artifact download + digest/PASS verification occurs before the first Stage 2 command. The workflow must reject a candidate not represented by the verified PASS evidence.

- [ ] **Step 2: Write exact-window evidence audit tests.**

The workflow evidence verifier must require exactly seven windows with exact names/bounds and `refit_status = NOT_APPLICABLE_FIXED_RULE`. It must reject duplicates, gaps, reordered/renamed custom windows, coverage after `2026-08-20`, or missing diagnostic 1.0-pip results.

- [ ] **Step 3: Run RED.**

Run: `python -m unittest tests.test_phase7_walk_forward_workflow -v`

- [ ] **Step 4: Implement Stage 2 workflow.**

Execute the whole seven-window Stage 2 cell twice, compare complete deterministic evidence bytes, inspect immutable identities/window accounting/gates, then upload the verified first evidence package.

- [ ] **Step 5: Run workflow and YAML tests.**

Run:

```bash
python -m unittest tests.test_phase7_walk_forward_workflow -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
```

Do **not** dispatch the workflow until authoritative Stage 1 PASS evidence exists.

- [ ] **Step 6: Commit.**

Commit message: `[phase1-no-source] Add Phase 7 walk-forward workflow`

---

### Task 10: Verify the implementation PR before any 2024+ data is opened

**Files:**
- No new production file is required unless verification exposes a defect.
- May modify tests only to fix a verified implementation defect or stale state assertion.

**Interfaces:**
- Produces a merged-main implementation SHA eligible for the separate irreversible Stage 1 execution step.

- [ ] **Step 1: Run focused Phase 7 suite.**

Run:

```bash
python -m unittest \
  tests.test_phase7_protocol_state \
  tests.test_phase7_contracts \
  tests.test_phase7_data \
  tests.test_phase7_evaluation \
  tests.test_phase7_gates \
  tests.test_phase7_artifacts \
  tests.test_phase7_cli \
  tests.test_phase7_final_gate_workflow \
  tests.test_phase7_walk_forward_workflow -v
```

Expected: PASS with no external data access.

- [ ] **Step 2: Run complete source-free regression.**

Run:

```bash
python -m unittest discover -s tests -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m compileall -q src tests
```

- [ ] **Step 3: Re-run unchanged Phase 3 acceptance workflow on the implementation head.**

Require SUCCESS. This confirms Phase 7 additions did not alter accepted execution/risk semantics.

- [ ] **Step 4: Verify Phase 1 source-capable PR jobs are skipped.**

The implementation PR title must retain `[phase1-no-source]`. Confirm acquisition/golden/network source-capable workflows did not execute for the Phase 7 implementation head.

- [ ] **Step 5: Inspect the PR diff for lock weakening.**

Reject the PR if it modifies `allowed_split()` to permit `final`, weakens `fmp.research.data` 2024 guards, weakens `fmp.models` final guards, adds generic final-test/date bypasses, or introduces broker/demo/live/real-money code.

- [ ] **Step 6: Merge only after all checks are green and re-run merged-main regression.**

No Stage 1 dispatch occurs before the merged-main implementation SHA is verified.

---

### Task 11: Execute and audit the irreversible 2024 Stage 1 gate exactly once per candidate

**Files:**
- Create after results: `docs/phase7-stage1-evidence.md`
- Modify after results: `docs/experiment-log.md`
- Modify after results: `docs/project-state.md`
- Modify after results: `docs/decision-log.md` only for a new outcome decision; do not edit DEC-033 in place.
- Create: `tests/test_phase7_stage1_evidence_state.py`

**Interfaces:**
- Consumes verified merged-main Phase 7 implementation and frozen Phase 2 artifact.
- Produces audited Stage 1 PASS/REJECT evidence for each candidate and, only if at least one candidate passes, the authorization identity Stage 2 needs.

- [ ] **Step 1: Trigger `phase7-final-gate` manually on the exact verified merged-main implementation SHA.**

This is the first authorized Phase 7 opening of 2024 source partitions. Record workflow run ID and exact head SHA immediately.

- [ ] **Step 2: Require all matrix cells and deterministic checks to succeed.**

A workflow execution error is not a strategy rejection. Repair only deterministic implementation/orchestration defects without changing the frozen strategy, date, cost, or gate protocol; rerun on a new code SHA and preserve failed-run history.

- [ ] **Step 3: Independently audit every Stage 1 artifact.**

Verify GitHub ZIP digest, inner manifest/file digests, exact code/data/checkpoint identity, exact scored/warm-up/opened partitions, candidate parameters, risk/cost identity, and recompute every Stage 1 gate criterion from evidence.

- [ ] **Step 4: Write RED evidence-state test before documentation.**

Assert the docs record the authoritative run and candidate decisions, `Final-test touched?: YES — Stage 1 2024 only`, and that Stage 2 remains locked unless at least one exact candidate has audited `STAGE1_PASS` evidence.

- [ ] **Step 5: Record Stage 1 evidence and outcome in a new decision.**

Do not retune. If neither candidate passes, mark Phase 7 COMPLETE / REJECT, keep Phase 8 locked, and do not run Task 12. If one or both pass, record exact survivor identity/digest and keep Phase 7 ACTIVE for Stage 2.

- [ ] **Step 6: Run source-free regression and merge the evidence/state PR.**

Use `[phase1-no-source]` title. Re-run tests + Phase 3 acceptance; source-capable Phase 1 jobs must skip.

---

### Task 12: Execute Stage 2 only for audited Stage 1 survivors and close Phase 7

**Precondition:** At least one candidate has a merged, audited Stage 1 PASS outcome with exact evidence digest. If no candidate passes Stage 1, this task is forbidden.

**Files:**
- Create: `docs/phase7-walk-forward-evidence.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Modify: `docs/decision-log.md` with a new Phase 7 outcome/acceptance decision.
- Create: `tests/test_phase7_acceptance_state.py`
- Later checkpoint bookkeeping may create/update `tests/test_phase7_checkpoint_state.py`.

**Interfaces:**
- Produces final per-candidate `PHASE7_PROMOTE_TO_SHADOW_DESIGN` or `PHASE7_COMPLETE_REJECT` evidence and Phase 7 acceptance status.

- [ ] **Step 1: Trigger `phase7-walk-forward` once for each audited Stage 1 survivor.**

Pass only the exact Stage 1 evidence artifact identity required by the workflow. The workflow must verify PASS before opening required 2025/2026 source partitions.

- [ ] **Step 2: Audit every Stage 2 artifact independently.**

Verify seven exact windows, all three costs, independent $100k starting equity, no refit, deterministic duplicate execution, exact warm-up/source accounting, aggregate arithmetic, window stability criteria, and immutable upstream identities.

- [ ] **Step 3: Write RED acceptance-state test before outcome docs.**

The test must require all final criteria and must distinguish promotion PASS from a correctly completed negative experiment.

- [ ] **Step 4: Record the final outcome without post-result changes.**

A candidate enters Phase 8 design eligibility only if every frozen Stage 2 gate passes. Otherwise it is rejected. No threshold, parameter, window, or cost rule may change after observation.

- [ ] **Step 5: Determine Phase 7 phase-level acceptance.**

Phase 7 is operationally complete once every Stage 1 survivor has a deterministic Stage 2 outcome. If at least one candidate passes the promotion gate, close Phase 7 as PASS and make Phase 8 the next phase but still UNSTARTED. If no candidate passes, record Phase 7 complete with no shadow candidate and keep Phase 8 locked pending an explicit new research decision rather than automatically starting a rescue search.

- [ ] **Step 6: Run full source-free regression and unchanged Phase 3 acceptance.**

Require all green before merging final evidence/state docs.

- [ ] **Step 7: Create immutable checkpoint only after verified merged-main closure.**

Create `fmp-v1-phase7-walk-forward` at the exact verified merged acceptance-closure commit, then record the checkpoint in source-of-truth docs with a separate RED→GREEN bookkeeping test/PR if that established repository pattern remains in force.

---

## Self-Review Checklist

Before execution, verify the following against the approved spec:

- [ ] Every approved Stage 1 and Stage 2 date boundary appears exactly once in contracts and has a test.
- [ ] No implementation task weakens existing Phase 4/6 final-test locks.
- [ ] No free-form final-test date or strategy-parameter surface exists.
- [ ] Warm-up context is readable only within the seven-day bound and never scoreable.
- [ ] Both fixed strategies reuse existing strategy generators and Phase 3 execution/risk logic.
- [ ] Stage 1 and Stage 2 gates match the approved strict inequalities/boundaries exactly.
- [ ] Stage 2 aggregate arithmetic does not chain independent window equity curves.
- [ ] Stage 2 cannot perform source I/O before verified Stage 1 PASS authorization.
- [ ] 1.0-pip results are always preserved and never secretly promoted to a hard gate.
- [ ] Evidence is deterministic and contains all immutable upstream identities.
- [ ] The irreversible 2024 Stage 1 run is separated from implementation verification.
- [ ] Phase 8/broker/demo/live/real-money remain locked throughout Phase 7.
- [ ] No `TBD`, `TODO`, placeholder implementation step, or unspecified error-handling instruction remains in this plan.
