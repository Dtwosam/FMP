# Phase 4 Session-Breakout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first Phase 4 baseline-research slice: a leakage-safe research harness plus a predeclared London session-breakout family evaluated only on frozen development and validation periods through the accepted Phase 3 engine.

**Architecture:** Phase 4 adds pure strategy logic under `fmp.strategies` and research orchestration under `fmp.research`. Phase 3 remains the sole execution/risk/PnL authority; its only extension is a backward-compatible scheduled time exit at executable-side bar open. The research loader reads accepted Phase 2 processed Parquet only, filters by the frozen split, and exposes no normal final-test mode.

**Tech Stack:** Python >=3.11, stdlib `zoneinfo`, Polars 1.44.2, `unittest`, existing Phase 2 Parquet/manifests, existing Phase 3 event-driven backtester.

**Spec:** `docs/superpowers/specs/2026-09-14-phase4-baseline-research-design.md` plus authoritative amendments in `docs/superpowers/specs/2026-09-14-phase4-baseline-research-design-amendments.md`.

## Global Constraints

- Every Phase 4 commit message and PR title includes `[phase1-no-source]`.
- Do not modify `docs/phase1-exact-gap-queue.json`, Phase 1 acquisition logic, Supabase functions/config, or `fmp-raw`.
- No Dukascopy/source acquisition and no `id-token` permission in Phase 4 workflows.
- Frozen splits: development `[2015-01-01, 2021-01-01)`, validation `[2021-01-01, 2024-01-01)`, final `[2024-01-01, 2026-08-21)`.
- Development/validation tooling has no final-test mode or flag.
- First family only: session breakout on EURUSD, GBPUSD, USDJPY and 5m/15m/1h.
- Predeclared grid: buffer `0/2/5` pips x target-range multiple `0.5/1.0/1.5`; slippage `0.2/0.5/1.0` pips per fill.
- Risk remains Phase 3 defaults with requested risk `0.25%`; zero commission and zero financing are explicit for this intraday family.
- Strategy code never sizes positions or simulates fills.
- Phase 4 remains ACTIVE after this slice; do not create the Phase 4 checkpoint or start Phase 5.

---

### Task 1: Freeze research split and experiment contracts

**Files:**
- Create: `src/fmp/research/__init__.py`
- Create: `src/fmp/research/contracts.py`
- Test: `tests/test_phase4_research_contracts.py`

**Interfaces:**
- Produces `ResearchSplit`, `ExperimentSpec`, `DEVELOPMENT_SPLIT`, `VALIDATION_SPLIT`, `FINAL_TEST_SPLIT`, `allowed_split(name)`, and stable config hashing.
- Later tasks consume these exact split boundaries and experiment identity fields.

- [ ] **Step 1: Write RED contract tests**

```python
class Phase4ResearchContractTests(unittest.TestCase):
    def test_frozen_splits_are_non_overlapping_and_exact(self):
        self.assertEqual(DEVELOPMENT_SPLIT.start, date(2015, 1, 1))
        self.assertEqual(DEVELOPMENT_SPLIT.end_exclusive, date(2021, 1, 1))
        self.assertEqual(VALIDATION_SPLIT.start, date(2021, 1, 1))
        self.assertEqual(VALIDATION_SPLIT.end_exclusive, date(2024, 1, 1))
        self.assertEqual(FINAL_TEST_SPLIT.start, date(2024, 1, 1))
        self.assertEqual(FINAL_TEST_SPLIT.end_exclusive, date(2026, 8, 21))

    def test_normal_research_api_refuses_final_test(self):
        with self.assertRaisesRegex(ValueError, "final test"):
            allowed_split("final")

    def test_experiment_spec_hash_is_stable(self):
        self.assertEqual(spec.config_sha256(), spec.config_sha256())
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_phase4_research_contracts -v`
Expected: import failure because `fmp.research` does not exist.

- [ ] **Step 3: Implement minimal contracts**

Use frozen dataclasses and stable JSON bytes:

```python
@dataclass(frozen=True, slots=True)
class ResearchSplit:
    name: str
    start: date
    end_exclusive: date

DEVELOPMENT_SPLIT = ResearchSplit("development", date(2015,1,1), date(2021,1,1))
VALIDATION_SPLIT = ResearchSplit("validation", date(2021,1,1), date(2024,1,1))
FINAL_TEST_SPLIT = ResearchSplit("final", date(2024,1,1), date(2026,8,21))

def allowed_split(name: str) -> ResearchSplit:
    if name == "development": return DEVELOPMENT_SPLIT
    if name == "validation": return VALIDATION_SPLIT
    raise ValueError("final test is not available from the normal Phase 4 runner")
```

`ExperimentSpec` fields: `experiment_id`, `hypothesis`, `code_commit`, `processed_manifest_sha256`, `schema_version`, `family_id`, `strategy_version`, `symbol`, `timeframe`, `split_name`, `parameters`, `slippage_pips`, `commission_config`, `financing_config`, `risk_config`; `config_sha256()` hashes sorted UTF-8 JSON with `allow_nan=False`.

- [ ] **Step 4: Run GREEN + regression**

Run: `python -m unittest tests.test_phase4_research_contracts -v && python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "[phase1-no-source] Add Phase 4 research contracts"`

---

### Task 2: Add backward-compatible scheduled exits to Phase 3

**Files:**
- Modify: `src/fmp/contracts.py`
- Modify: `src/fmp/backtest/execution.py`
- Modify: `src/fmp/backtest/engine.py`
- Test: `tests/test_phase3_execution.py`
- Test: `tests/test_phase3_engine.py`

**Interfaces:**
- Add `ExitReason.TIME_EXIT`.
- Add frozen `ScheduledExit(decision_id: str, symbol: str, timestamp_utc: datetime)`.
- Add `close_time_exit(position, bar, *, slippage_pips, commission_model, financing_model) -> ExitFill`.
- Extend `run_backtest(..., scheduled_exits: Sequence[ScheduledExit] = ())` without changing behavior when the argument is omitted.

- [ ] **Step 1: Write RED execution tests** proving LONG uses BID open, SHORT uses ASK open, adverse slippage/commission apply, and reason is `TIME_EXIT`.

```python
fill = close_time_exit(position, exit_bar, slippage_pips=1.0,
                       commission_model=ZeroCommission(), financing_model=ZeroFinancing())
self.assertEqual(fill.reason, ExitReason.TIME_EXIT)
self.assertEqual(fill.reference_price, exit_bar.bid_open)  # LONG
```

- [ ] **Step 2: Write RED engine tests** proving scheduled exit happens at bar open before that bar's high/low stop/target evaluation, before same-timestamp new entries, and becomes a no-op if the position already closed earlier.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_phase3_execution tests.test_phase3_engine -v`
Expected: missing `TIME_EXIT`/`ScheduledExit`/`close_time_exit` failures.

- [ ] **Step 4: Implement minimal execution/engine changes**

Engine rule for each open position at timestamp `T`:

```python
scheduled = scheduled_by_decision.get(position.decision_id)
if scheduled is not None and scheduled.timestamp_utc == timestamp:
    finalize_position(position, close_time_exit(...))
    continue
exit_fill = evaluate_exit(position, bar, ...)
```

Validate unique `decision_id` schedules, matching symbol, UTC timestamp, and schedule not earlier than position eligibility. Preserve existing `run_backtest` output exactly when `scheduled_exits=()`.

- [ ] **Step 5: Run GREEN + full Phase 3 regression**

Run: `python -m unittest tests.test_phase3_execution tests.test_phase3_engine tests.test_phase3_acceptance -v && python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 6: Commit**

`git commit -m "[phase1-no-source] Add deterministic scheduled backtest exits"`

---

### Task 3: Implement the read-only processed-data split loader

**Files:**
- Create: `src/fmp/research/data.py`
- Test: `tests/test_phase4_research_data.py`

**Interfaces:**
- `load_processed_bars(*, dataset_root: Path, manifest_path: Path, symbol: str, timeframe: str, split_name: str) -> tuple[QuoteBar, ...]`
- Accept only `5m`, `15m`, `1h`; call `allowed_split`, so final test is structurally unavailable.

- [ ] **Step 1: Write RED tests with temporary Parquet/manifest fixtures** covering manifest-symbol mismatch, duplicate timestamps, split filtering, sorted output, invalid timeframe, and final-test refusal.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_phase4_research_data -v`
Expected: missing module failure.

- [ ] **Step 3: Implement loader**

Read manifest JSON, require `schema_version == "fmp-canonical-1m-v1"` and matching symbol. Select artifact entries whose keys start with `f"{timeframe}:"` and whose month overlaps the split. Read those Parquet files, filter `timestamp_utc` to `[split.start, split.end_exclusive)`, then filter `is_complete == True` before converting to `QuoteBar`. Filtering incomplete bars is an eligibility filter, not data repair; record the excluded count in a returned/diagnostic helper used by Task 7. Reject duplicate `(symbol,timestamp_utc)` identities and non-monotonic output.

- [ ] **Step 4: Run GREEN + regression**

Run: `python -m unittest tests.test_phase4_research_data -v && python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "[phase1-no-source] Add Phase 4 processed-data loader"`

---

### Task 4: Add strategy contracts and the timing-safe candidate adapter

**Files:**
- Create: `src/fmp/strategies/__init__.py`
- Create: `src/fmp/strategies/contracts.py`
- Create: `src/fmp/research/adapter.py`
- Test: `tests/test_phase4_strategy_contracts.py`

**Interfaces:**
- `StrategyConfig(family_id, strategy_version, timeframe, parameters, timezone_name)`.
- `SignalCandidate(candidate_id, symbol, observation_bar_timestamp_utc, signal_known_timestamp_utc, direction, stop_price, target_price, latest_exit_timestamp_utc, reason_code, metadata)`.
- `candidate_to_decision(candidate, *, next_bar_timestamp_utc, requested_risk_fraction=0.0025) -> tuple[Decision, ScheduledExit | None]`.

- [ ] **Step 1: Write RED tests** proving stable IDs/serialization, UTC validation, `signal_known_timestamp_utc > observation_bar_timestamp_utc`, `signal_known_timestamp_utc == next_bar_timestamp_utc`, and no execution on the observation-bar label.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_phase4_strategy_contracts -v`
Expected: missing `fmp.strategies` failure.

- [ ] **Step 3: Implement contracts/adapter**

The Phase 2 bar label is the period start. For timeframe width `W`, strategy code records `signal_known_timestamp_utc = observation_bar_timestamp_utc + W`. The adapter keeps Phase 3's approved convention by setting `Decision.decision_timestamp_utc` to the observation bar label and `earliest_executable_timestamp_utc` to the immediately following supplied bar label, while the candidate artifact retains the true known-at timestamp for audit. Reject any candidate where true known-at time differs from that next supplied label.

- [ ] **Step 4: Run GREEN + regression**

Run: `python -m unittest tests.test_phase4_strategy_contracts -v && python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "[phase1-no-source] Add Phase 4 strategy contracts"`

---

### Task 5: Implement London session breakout

**Files:**
- Create: `src/fmp/strategies/session_breakout.py`
- Test: `tests/test_phase4_session_breakout.py`

**Interfaces:**
- `SessionBreakoutConfig(buffer_pips: int, target_range_multiple: float, timeframe: str)` with only the predeclared grid accepted.
- `generate_session_breakout_candidates(bars: Sequence[QuoteBar], *, config: SessionBreakoutConfig) -> tuple[SignalCandidate, ...]`.

- [ ] **Step 1: Write RED deterministic/DST tests** for London local windows 00:00-08:00 range, 08:00-12:00 breakout observation, 16:00 flat; include winter and summer UTC mappings using `ZoneInfo("Europe/London")`.

- [ ] **Step 2: Add RED strategy tests** for midpoint OHLC, first-breakout-only behavior, exact 0/2/5 pip buffers for EURUSD and USDJPY, exact 0.5/1.0/1.5 target math, zero-width/no-break sessions as `NO_TRADE`, and stable candidate IDs.

Target rule from the authoritative amendment:

```python
if direction is Direction.LONG:
    target = signal_mid_close + config.target_range_multiple * range_width
else:
    target = signal_mid_close - config.target_range_multiple * range_width
```

Stop remains opposite frozen range boundary. `latest_exit_timestamp_utc` must equal the exact supplied 16:00 London-local bar label or the session emits an explicit no-trade/rejection candidate; do not shift the exit.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_phase4_session_breakout -v`
Expected: missing implementation failures.

- [ ] **Step 4: Implement minimal strategy** using midpoint only for analysis and no risk/fill logic.

- [ ] **Step 5: Run GREEN + full regression**

Run: `python -m unittest tests.test_phase4_session_breakout -v && python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 6: Commit**

`git commit -m "[phase1-no-source] Add session breakout baseline"`

---

### Task 6: Add research metrics and deterministic benchmark artifacts

**Files:**
- Create: `src/fmp/research/reporting.py`
- Test: `tests/test_phase4_research_reporting.py`

**Interfaces:**
- `compute_research_metrics(run: BacktestRun, *, starting_equity_usd: float, requested_risk_fraction: float) -> dict[str, object]`.
- `write_benchmark_artifacts(result: Mapping[str, object], out_dir: Path) -> dict[str, object]`.

- [ ] **Step 1: Write RED hand-calculated tests** for reward/risk values `trade.net_pnl_usd / (trade.risk_equity_before_usd * requested_risk_fraction)`, pair/timeframe/year breakdowns, trade/rejection/no-trade/time-exit counts, and cost-sensitivity rows.

- [ ] **Step 2: Write RED byte-determinism tests** requiring sorted JSON, `allow_nan=False`, atomic writes, manifest SHA-256/size records, and byte-identical repeated output.

- [ ] **Step 3: Run RED**

Run: `python -m unittest tests.test_phase4_research_reporting -v`
Expected: missing module failure.

- [ ] **Step 4: Implement metrics/writer** by reusing Phase 3 metrics rather than recomputing fills/PnL. Report Sharpe/Sortino only from an explicitly defined chronological daily realized-return series; if fewer than two non-null daily returns exist, serialize them as `null` rather than inventing a statistic.

- [ ] **Step 5: Run GREEN + regression**

Run: `python -m unittest tests.test_phase4_research_reporting -v && python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 6: Commit**

`git commit -m "[phase1-no-source] Add deterministic Phase 4 reporting"`

---

### Task 7: Implement the experiment grid runner

**Files:**
- Create: `src/fmp/research/session_breakout.py`
- Test: `tests/test_phase4_session_breakout_research.py`

**Interfaces:**
- `SESSION_BREAKOUT_GRID = ((0,0.5),(0,1.0),(0,1.5),(2,0.5),(2,1.0),(2,1.5),(5,0.5),(5,1.0),(5,1.5))`.
- `SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)`.
- `run_session_breakout_grid(..., split_name: str) -> dict[str, object]`.

- [ ] **Step 1: Write RED tests** asserting exactly 9 parameter configs x 3 slippage scenarios, same candidate generation reused across cost scenarios, `BacktestConfig` uses `ZeroCommission`, `ZeroFinancing`, `RiskConfig()` and requested risk 0.0025, all runs cite the same manifest/code/split identity, and `split_name="final"` fails before any Parquet read.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_phase4_session_breakout_research -v`
Expected: missing runner failure.

- [ ] **Step 3: Implement runner**

For each grid point: generate candidates once, adapt to decisions/schedules, then run three Phase 3 backtests differing only by slippage. Keep every losing/empty configuration. Produce sorted configuration rows keyed by `(buffer_pips, target_range_multiple, slippage_pips)` and include excluded-incomplete-bar counts and rejection reason counts.

- [ ] **Step 4: Run GREEN + regression**

Run: `python -m unittest tests.test_phase4_session_breakout_research -v && python -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "[phase1-no-source] Add session breakout research runner"`

---

### Task 8: Predeclare the split and first serious experiment in source of truth

**Files:**
- Modify: `docs/decision-log.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Test: `tests/test_phase4_research_state.py`

**Interfaces:**
- DEC-018 freezes the chronological split and final-test lock.
- `EXP-20260914-001` predeclares the session-breakout hypothesis, universe, exact 9-point grid, exact 3 slippage scenarios, zero commission/financing, and Phase 3 risk settings before merged-main results exist.

- [ ] **Step 1: Write RED state tests** that parse the docs and require exact split dates/grid/slippage values, `Final-test touched?: NO`, Phase 4 status ACTIVE, Phase 3 PASS, Phase 5 unstarted, and real-money lock unchanged.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_phase4_research_state -v`
Expected: missing DEC/experiment Phase 4 records.

- [ ] **Step 3: Update docs**

For the planned experiment's code identity use the explicit statement: `Code commit: merged-main workflow head SHA recorded by the experiment artifact; copied into the result record after execution.` Do not invent a SHA before merge. Status is `PLANNED`; conclusion is not pre-filled.

- [ ] **Step 4: Run GREEN + regression**

Run: `python -m unittest tests.test_phase4_research_state -v && python -m unittest discover -s tests -v && python -m compileall -q src tests`
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "[phase1-no-source] Predeclare Phase 4 research experiment"`

---

### Task 9: Add the source-free merged-main experiment workflow and inspect evidence

**Files:**
- Create: `scripts/phase4_session_breakout.py`
- Create: `.github/workflows/phase4-session-breakout.yml`
- Test: `tests/test_phase4_session_breakout_cli.py`
- Test: `tests/test_phase4_session_breakout_workflow.py`

**Interfaces:**
- CLI accepts only `--dataset-root`, `--manifest`, `--symbol`, `--timeframe`, `--split {development,validation}`, `--out`, `--code-commit`; there is no final-test option.
- Workflow runs only source-free research; permissions are `contents: read` and `actions: read`, with no `id-token`.

- [ ] **Step 1: Write RED CLI/workflow guards** requiring the fixed symbols/timeframes/splits, no final mode, no Supabase/Dukascopy/source acquisition strings, no `fmp.data.cli fetch`, no raw writes, and artifact upload with `if-no-files-found: error`.

- [ ] **Step 2: Run RED**

Run: `python -m unittest tests.test_phase4_session_breakout_cli tests.test_phase4_session_breakout_workflow -v`
Expected: missing script/workflow failures.

- [ ] **Step 3: Implement CLI** that runs `run_session_breakout_grid` and writes deterministic benchmark artifacts.

- [ ] **Step 4: Implement workflow**

Use a matrix over 3 symbols x 3 timeframes x 2 splits. Download only the accepted Phase 2 processed artifact for the matrix symbol from GitHub Actions using the immutable accepted artifact IDs/digests recorded in `docs/project-state.md`; verify the downloaded ZIP SHA-256 before extraction. Run the CLI with `GITHUB_SHA`, then upload one benchmark artifact per matrix cell. Trigger on `push` to `main` only when Phase 4 strategy/research/runner/workflow files change, plus `workflow_dispatch` for reproducible reruns. Do not expose a final-test input.

- [ ] **Step 5: Run GREEN locally/PR CI**

Run: `python -m unittest discover -s tests -v && python -m compileall -q src tests`
Expected: PASS; Phase 1 source-capable PR workflows SKIPPED under the title marker.

- [ ] **Step 6: Commit and merge only the exact green head**

Commit: `git commit -m "[phase1-no-source] Add source-free Phase 4 benchmark workflow"`.
Create PR title with `[phase1-no-source]` from creation time. Review changed files, keep `docs/phase1-exact-gap-queue.json` absent, ready the exact green head, re-check Phase 1 guards, and squash merge with `[phase1-no-source]`.

- [ ] **Step 7: Verify merged-main evidence**

Require post-merge `tests` success and the `phase4-session-breakout` matrix success. Confirm no Phase 1 acquisition-capable push workflow triggered. Download every development/validation benchmark artifact, recompute ZIP/file digests and benchmark calculations independently, and verify all run identities use the merge SHA and frozen processed-manifest identities.

- [ ] **Step 8: Record experiment outcome without touching final test**

On a new docs-only `[phase1-no-source]` branch, update `EXP-20260914-001` from `PLANNED` to the evidence-supported `PASS`, `FAIL`, or `INCONCLUSIVE`, record exact code/artifact identities and all benchmark results including losing configurations, and state `Final-test touched?: NO`. Update `docs/project-state.md` with Phase 4 still ACTIVE and the next family/research question. Merge only after fresh green CI/source guards.

## Completion gate for this plan

This plan is complete only when the session-breakout implementation is merged, development/validation evidence is independently inspected and durably logged, final-test data remains untouched, Phase 3 regressions stay green, and Phase 4 remains ACTIVE for the next sequential baseline family. Do not create `fmp-v1-phase4-baselines` from this first-family slice alone.
