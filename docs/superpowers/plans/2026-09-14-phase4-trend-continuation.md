# Phase 4 Trend-Continuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the second Phase 4 baseline family, trend continuation, run its frozen development/validation benchmark on merged `main`, and record evidence without touching the final-test period.

**Architecture:** Reuse the existing Phase 4 loader, strategy contracts, adapter, reporting, and accepted Phase 3 backtester/risk engine. Add one pure trend-continuation strategy module, one six-point research-grid runner, one CLI, one source-free 18-cell workflow, then predeclare and separately close `EXP-20260914-002` from independently inspected merged-main artifacts.

**Tech Stack:** Python 3.11+, standard library, `unittest`, Polars via the existing research loader, GitHub Actions, deterministic JSON/hash reporting already present in `fmp.research.reporting`.

**Spec:** `docs/superpowers/specs/2026-09-14-phase4-trend-continuation-design.md`

## Global Constraints

- Base implementation on exact verified `main` at `5ad5cac64a537107d8a1683101814bd1ce159083` or its later verified no-source descendants.
- Every post-Phase1 commit and PR title contains `[phase1-no-source]`.
- Never intentionally trigger Phase 1 acquisition, call Dukascopy, mutate `fmp-raw`, modify `docs/phase1-exact-gap-queue.json`, request OIDC, or call Supabase.
- Normal Phase 4 tooling exposes only `development` and `validation`; `final` must fail before file I/O.
- Keep accepted Phase 3 execution/risk semantics unchanged unless an independently proven bug requires a separately reviewed architectural change.
- Use historical BID/ASK fills, slippage `{0.2, 0.5, 1.0}` pips, zero commission, zero financing, requested risk `0.25%`, max trade risk `0.50%`, max simultaneous risk `1.00%`, daily halt `1.50%`.
- Strategy analysis uses only complete closed midpoint bars and DEC-018 true-known timing.
- Phase 4 remains ACTIVE after this family; Phase 5 remains UNSTARTED; real-money trading remains locked.

---

### Task 1: Freeze trend-window configuration and SMA context

**Files:**
- Create: `src/fmp/strategies/trend_continuation.py`
- Create: `tests/test_phase4_trend_continuation.py`

**Interfaces:**
- Produces `TrendContinuationConfig(trend_window_id: str, target_r_multiple: float, timeframe: str)`.
- Produces `duration_to_bars(timeframe: str, hours: int) -> int`.
- Later tasks consume `generate_trend_continuation_candidates(...)` from the same module.

- [ ] **Step 1: Write RED configuration/context tests**

Add focused `unittest` cases that assert:

```python
self.assertEqual(duration_to_bars("5m", 2), 24)
self.assertEqual(duration_to_bars("15m", 8), 32)
self.assertEqual(duration_to_bars("1h", 32), 32)
TrendContinuationConfig(trend_window_id="B", target_r_multiple=1.5, timeframe="15m")
with self.assertRaises(ValueError):
    TrendContinuationConfig(trend_window_id="D", target_r_multiple=1.5, timeframe="15m")
with self.assertRaises(ValueError):
    TrendContinuationConfig(trend_window_id="A", target_r_multiple=2.0, timeframe="15m")
```

Also construct exact midpoint-close sequences proving:

- LONG context only when `fast_sma > slow_sma` and slow SMA is rising versus the prior bar;
- SHORT is the exact inverse;
- equality is neutral;
- any missing cadence inside the current/prior slow windows makes that observation ineligible.

- [ ] **Step 2: Run RED test**

Run:

```bash
python -m unittest tests.test_phase4_trend_continuation -v
```

Expected: import failure for `fmp.strategies.trend_continuation`.

- [ ] **Step 3: Implement minimal configuration/context helpers**

Create constants equivalent to:

```python
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_TREND_WINDOWS = {
    "A": (2, 8),
    "B": (4, 16),
    "C": (8, 32),
}
_ALLOWED_TARGET_R = frozenset({1.0, 1.5})
```

`duration_to_bars()` must require exact divisibility of `hours * 60` by timeframe width. Implement midpoint OHLC helpers and an internal context function that receives a contiguous bar sequence and returns LONG, SHORT, or neutral using only closed bars.

- [ ] **Step 4: Run GREEN test**

Run the focused test module and require all new configuration/context tests to pass.

- [ ] **Step 5: Commit**

```bash
git add src/fmp/strategies/trend_continuation.py tests/test_phase4_trend_continuation.py
git commit -m "[phase1-no-source] Add trend continuation context"
```

---

### Task 2: Implement deterministic pullback/resumption candidates

**Files:**
- Modify: `src/fmp/strategies/trend_continuation.py`
- Modify: `tests/test_phase4_trend_continuation.py`

**Interfaces:**
- Produces `generate_trend_continuation_candidates(bars: Sequence[QuoteBar], *, config: TrendContinuationConfig) -> tuple[SignalCandidate, ...]`.
- Reuses `SignalCandidate`, `Europe/London`, and exact Phase 4 true-known timing.

- [ ] **Step 1: Add RED golden strategy tests**

Build compact deterministic fixtures covering all spec requirements:

1. LONG previous close `<= previous fast SMA`, current close `> current fast SMA`, LONG trend context => LONG candidate.
2. SHORT symmetric case.
3. Intrabar high/low touching the fast SMA without the close-cross => no directional candidate.
4. Only first directional candidate per London calendar session.
5. No qualifying signal => one `NO_TRADE` candidate with stable reason.
6. LONG stop = minimum midpoint low of signal bar plus previous two bars.
7. SHORT stop = maximum midpoint high of the same three-bar window.
8. Targets equal signal midpoint close ± `1.0R` / `1.5R`.
9. Missing one cadence slot inside SMA history => no use of shortened window.
10. Missing one of the three stop bars => signal ineligible.
11. London winter and summer DST map 08:00–14:00 observation labels and exact 16:00 exit correctly.
12. Missing exact 16:00-local executable bar => fail-closed `NO_TRADE`/incomplete-session outcome.
13. `signal_known_timestamp_utc == observation_label + timeframe_width`.
14. Candidate generation and `stable_json_bytes()` are byte-deterministic.

Use stable reason codes such as `CONTINUATION_LONG`, `CONTINUATION_SHORT`, `NO_CONTINUATION`, and `INCOMPLETE_SESSION`; do not create a later-bar retry path.

- [ ] **Step 2: Run RED tests**

Run:

```bash
python -m unittest tests.test_phase4_trend_continuation -v
```

Expected: failures for missing candidate generator/behavior.

- [ ] **Step 3: Implement candidate generator**

Implementation rules:

```python
# trend windows are closed-bar midpoint SMA windows
# eligible London observation labels: 08:00 <= label <= 14:00
# first directional signal only per London date
# stop uses exactly current + previous 2 complete bars
# target is frozen from signal midpoint close and stop-derived R
# latest_exit_timestamp_utc is exact 16:00 Europe/London
```

Sort bars deterministically, reject duplicate identities, require exactly one symbol, and never compute BID/ASK fills or position sizing in this module.

- [ ] **Step 4: Add actual-entry gap integration test**

Use `candidate_to_decision()` plus `run_backtest()` with a next executable BID/ASK open beyond the frozen stop/target. Assert no position opens and the existing Phase 3 deterministic rejection reason is preserved. Do not modify strategy geometry after the gap.

- [ ] **Step 5: Run focused + Phase 3 regression tests**

```bash
python -m unittest tests.test_phase4_trend_continuation tests.test_phase3_engine tests.test_phase3_acceptance -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/fmp/strategies/trend_continuation.py tests/test_phase4_trend_continuation.py
git commit -m "[phase1-no-source] Add trend continuation signals"
```

---

### Task 3: Add the frozen six-point research grid

**Files:**
- Create: `src/fmp/research/trend_continuation.py`
- Create: `tests/test_phase4_trend_continuation_research.py`

**Interfaces:**
- Produces `TREND_CONTINUATION_GRID = (("A", 1.0), ("A", 1.5), ("B", 1.0), ("B", 1.5), ("C", 1.0), ("C", 1.5))`.
- Produces `SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)`.
- Produces `run_trend_continuation_grid(...same dataset/symbol/timeframe/split/code_commit surface as session breakout...) -> dict[str, object]`.

- [ ] **Step 1: Write RED grid/lock/reuse tests**

Assert:

```python
self.assertEqual(len(TREND_CONTINUATION_GRID), 6)
self.assertEqual(SLIPPAGE_SCENARIOS, (0.2, 0.5, 1.0))
```

Mock `load_processed_bars()` and `generate_trend_continuation_candidates()` to prove:

- loader called exactly once;
- generator called exactly six times;
- each config produces exactly three cost rows;
- total rows = 18 per pair/timeframe/split artifact;
- candidate SHA is identical across the three slippage scenarios for each strategy config;
- all rows preserve requested risk `0.0025`, zero commission/financing, and unchanged `RiskConfig()` identity;
- `split_name="final"` raises before loader invocation.

- [ ] **Step 2: Run RED test**

```bash
python -m unittest tests.test_phase4_trend_continuation_research -v
```

Expected: missing `fmp.research.trend_continuation`.

- [ ] **Step 3: Implement research runner by composing existing common layers**

Mirror the accepted session-breakout runner structure, but use:

```python
TREND_CONTINUATION_FAMILY_ID = "trend_continuation"
TREND_CONTINUATION_STRATEGY_VERSION = "fmp-trend-continuation-v1"
RESULT_PROTOCOL = "fmp-phase4-trend-continuation-grid-v1"
```

Call `allowed_split()` before manifest reads; compute manifest SHA from persisted bytes; load with `load_processed_bars()`; generate candidates once/config; adapt once/config; run Phase 3 three times/config; call `compute_research_metrics()`; retain every row.

- [ ] **Step 4: Run GREEN + reporting regression**

```bash
python -m unittest tests.test_phase4_trend_continuation_research tests.test_phase4_research_reporting -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/fmp/research/trend_continuation.py tests/test_phase4_trend_continuation_research.py
git commit -m "[phase1-no-source] Add trend continuation research grid"
```

---

### Task 4: Add source-free CLI with final-test parser lock

**Files:**
- Create: `scripts/phase4_trend_continuation.py`
- Create: `tests/test_phase4_trend_continuation_cli.py`

**Interfaces:**
- CLI arguments exactly: `--dataset-root`, `--manifest`, `--symbol`, `--timeframe`, `--split`, `--out`, `--code-commit`.
- `--split` choices exactly `development`, `validation`.

- [ ] **Step 1: Write RED CLI tests**

Use subprocess/parser tests to assert:

- `--help` exposes only EURUSD/GBPUSD/USDJPY, 5m/15m/1h, development/validation;
- passing `--split final` exits during argument parsing before any dataset/manifest access;
- script imports `run_trend_continuation_grid` and `write_benchmark_artifacts` and contains no source/Supabase/OIDC code path.

- [ ] **Step 2: Run RED test**

```bash
python -m unittest tests.test_phase4_trend_continuation_cli -v
```

Expected: script missing.

- [ ] **Step 3: Implement minimal CLI**

Follow `scripts/phase4_session_breakout.py`; delegate all research semantics to `run_trend_continuation_grid()` and deterministic persistence to `write_benchmark_artifacts()`.

- [ ] **Step 4: Run GREEN test**

```bash
python -m unittest tests.test_phase4_trend_continuation_cli -v
```

- [ ] **Step 5: Commit**

```bash
git add scripts/phase4_trend_continuation.py tests/test_phase4_trend_continuation_cli.py
git commit -m "[phase1-no-source] Add trend continuation CLI"
```

---

### Task 5: Add fixed 18-cell source-free benchmark workflow

**Files:**
- Create: `.github/workflows/phase4-trend-continuation.yml`
- Create: `tests/test_phase4_trend_continuation_workflow.py`

**Interfaces:**
- Workflow name: `phase4-trend-continuation`.
- Matrix: 3 accepted Phase 2 artifacts × 3 timeframes × 2 splits = 18 cells.
- Each artifact benchmark contains 18 configuration rows = 6 configs × 3 slippage scenarios.

- [ ] **Step 1: Write RED workflow tests**

Parse workflow text/YAML and assert exact immutable identities:

```text
EURUSD artifact 10325737935 / db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3
GBPUSD artifact 10326096831 / fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2
USDJPY artifact 10327600628 / 6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72
```

Also assert:

- permissions are exactly read-only `contents: read`, `actions: read`;
- no `id-token`, Supabase, Dukascopy, source fetch, raw write, or final split;
- ZIP SHA is verified before `unzip`;
- evidence verifier checks protocol `fmp-phase4-trend-continuation-grid-v1`, exact `GITHUB_SHA`, and `len(configuration_rows) == 18`;
- upload uses `if-no-files-found: error`.

- [ ] **Step 2: Run RED workflow tests**

```bash
python -m unittest tests.test_phase4_trend_continuation_workflow -v
```

Expected: workflow missing.

- [ ] **Step 3: Implement workflow**

Copy only the proven source-free mechanics from `phase4-session-breakout.yml`; change script/output/protocol/artifact name and row count. Keep `fail-fast: false` and a bounded timeout adequate for 5m development cells.

- [ ] **Step 4: Run workflow YAML + focused tests**

```bash
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m unittest tests.test_phase4_trend_continuation_workflow -v
```

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/phase4-trend-continuation.yml tests/test_phase4_trend_continuation_workflow.py
git commit -m "[phase1-no-source] Add trend continuation workflow"
```

---

### Task 6: Predeclare EXP-20260914-002 before result-producing merge

**Files:**
- Modify: `docs/decision-log.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Create: `tests/test_phase4_trend_continuation_state.py`

**Interfaces:**
- New approved decision: `DEC-019 — Phase 4 trend-continuation baseline protocol`.
- Experiment: `EXP-20260914-002 — Trend continuation baseline` with status `PLANNED`.

- [ ] **Step 1: Write RED source-of-truth tests**

Require exact pre-result facts:

- DEC-019 records 2h/8h, 4h/16h, 8h/32h windows; 1.0R/1.5R targets; 08:00–14:00 London signal labels; exact 16:00 London exit; three-bar structural stop; 324 total rows; unchanged DEC-018 split/cost/risk locks.
- EXP-002 is `PLANNED`, has no result summary or conclusion, and says `Final-test touched?: NO`.
- project state says Phase 4 ACTIVE, frozen session-breakout candidate retained, trend continuation is the active second family, Phase 5 UNSTARTED, real-money locked.

- [ ] **Step 2: Run RED state test**

```bash
python -m unittest tests.test_phase4_trend_continuation_state -v
```

- [ ] **Step 3: Write predeclaration only**

Do not prefill trade counts, returns, candidate claims, PASS/FAIL, or conclusions. Record the merged-main code SHA later from the benchmark artifact/result record.

- [ ] **Step 4: Run GREEN state test**

```bash
python -m unittest tests.test_phase4_trend_continuation_state -v
```

- [ ] **Step 5: Commit**

```bash
git add docs/decision-log.md docs/experiment-log.md docs/project-state.md tests/test_phase4_trend_continuation_state.py
git commit -m "[phase1-no-source] Predeclare trend continuation experiment"
```

---

### Task 7: Full pre-merge verification and guarded implementation merge

**Files:**
- No new implementation files; review all branch changes.

- [ ] **Step 1: Run complete local/CI-equivalent verification**

```bash
python -m unittest discover -s tests -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m compileall -q src scripts
```

Expected: all tests PASS.

- [ ] **Step 2: Open/update draft PR with marker present from creation**

Title must begin with `[phase1-no-source]`. Verify changed files exclude `docs/phase1-exact-gap-queue.json`, Supabase, raw paths, and Phase 1 acquisition implementation.

- [ ] **Step 3: Verify exact-head GitHub checks**

Require:

- `tests` SUCCESS;
- `phase3-acceptance` SUCCESS unchanged;
- Phase 1 golden/source-capable PR checks SKIPPED;
- no unresolved review comments;
- exact head SHA unchanged after verification.

- [ ] **Step 4: Ready and recheck source guards**

After draft→ready, explicitly inspect the Phase 1 source-capable jobs and require their jobs to be SKIPPED before merge.

- [ ] **Step 5: Squash merge exact verified head**

Use a merge title containing `[phase1-no-source]` and pin the expected head SHA.

- [ ] **Step 6: Verify merged-main push**

Require `main` to resolve to the merge SHA, ordinary tests and Phase 3 acceptance to be green, and confirm no Phase 1 acquisition-capable push workflow triggered.

---

### Task 8: Run and independently validate the merged-main 18-cell benchmark

**Files:**
- No repository change until evidence is complete.

- [ ] **Step 1: Observe the merge-triggered `phase4-trend-continuation` workflow**

Require all 18 matrix jobs to complete SUCCESS. Do not rerun failed economic results; rerun only a demonstrably transient infrastructure failure without code/data/config change and record that fact.

- [ ] **Step 2: Download all 18 benchmark artifacts**

For every artifact independently verify:

- GitHub ZIP digest against downloaded bytes;
- exactly `benchmark.json` + `manifest.json`;
- manifest SHA/size against persisted benchmark bytes;
- merged-main code SHA;
- pair/timeframe/split identity;
- accepted Phase 2 processed manifest SHA/schema;
- exactly 18 ordered rows;
- candidate SHA reuse across 0.2/0.5/1.0-pip cost scenarios for each config;
- deterministic counts/metrics are finite and internally consistent.

Complete evidence set must contain exactly **324 rows**.

- [ ] **Step 3: Apply predeclared assessment rules**

For every pair/timeframe/config compare development vs validation at 0.2 pip, then inspect 0.5-pip and 1.0-pip stress, yearly breakdowns, drawdown, trade count, neighboring window/target support, and top-winner dependence. Do not choose by best development return alone.

- [ ] **Step 4: Freeze experiment outcome without final-test access**

Classify `EXP-20260914-002` as PASS, FAIL, or INCONCLUSIVE. If a serious candidate is retained, freeze its pair/timeframe/window/target exactly; otherwise record rejection/revision rationale. In every case keep `Final-test touched?: NO`.

---

### Task 9: Record trend-continuation evidence in a separate docs-only closure PR

**Files:**
- Create: `docs/phase4-trend-continuation-evidence.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Modify: `tests/test_phase4_trend_continuation_state.py`

**Interfaces:**
- Evidence must bind the full merged-main workflow run, exact code SHA, all artifact IDs/digests, 18/18 jobs, 324/324 rows, independent validation, and predeclared assessment result.

- [ ] **Step 1: Update state test from predeclaration to completed-evidence assertions**

Require experiment status/result/conclusion to match the inspected evidence while still asserting:

```text
Final-test touched?: NO
Phase 4 — ACTIVE
Phase 5 — UNSTARTED
Real-money trading remains locked
```

- [ ] **Step 2: Write durable evidence**

`docs/phase4-trend-continuation-evidence.md` must include experiment identity, run/merge SHA, artifact registry/digests, zero/nonzero validation-error summary, complete development/validation interpretation, cost sensitivity, yearly concentration, trade-count/drawdown notes, and the exact reason for PROMOTE/REJECT/REVISE/NEED_MORE_DATA.

- [ ] **Step 3: Update experiment log and project state**

Replace PLANNED with the evidence-supported terminal experiment status. Preserve the session-breakout candidate unchanged. Set next Phase 4 family to **mean reversion** after this family closes, but do not start it in the evidence PR.

- [ ] **Step 4: Verify docs-only closure PR**

Run full tests, Phase 3 acceptance, and Phase 1 skip guards. Confirm no final-test, source, raw, Supabase, Phase 5, broker/live, or real-money path appears.

- [ ] **Step 5: Merge exact green evidence head and verify main**

After merge, require ordinary main CI green and confirm no Phase 1 acquisition-capable push workflow triggered.

---

## Execution Boundary

Completing this plan closes only the **trend-continuation experiment slice**. It does not make Phase 4 PASS, create `fmp-v1-phase4-baselines`, access the final-test period, start Phase 5, or authorize live/real-money trading. The next admitted family after a clean trend-continuation closure is mean reversion.