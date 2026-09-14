# Phase 4 Trend-Continuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the second Phase 4 baseline family, trend continuation, run its frozen development/validation benchmark on merged `main`, and record evidence without touching the final-test period.

**Architecture:** Reuse the existing Phase 4 loader, strategy contracts, adapter, reporting, and accepted Phase 3 backtester/risk engine. Add one pure trend-continuation strategy module, one six-point research-grid runner, one CLI, one source-free 18-cell workflow, then predeclare and separately close `EXP-20260914-002` from independently inspected merged-main artifacts.

**Tech Stack:** Python 3.11+, standard library, `unittest`, Polars through the existing research loader, GitHub Actions, and the existing deterministic Phase 4 benchmark writer.

**Spec:** `docs/superpowers/specs/2026-09-14-phase4-trend-continuation-design.md`

## Global Constraints

- Base implementation on verified `main` at `5ad5cac64a537107d8a1683101814bd1ce159083` or a later verified `[phase1-no-source]` descendant.
- Every post-Phase1 commit and PR title contains `[phase1-no-source]`.
- Never intentionally trigger Phase 1 acquisition, call Dukascopy, mutate `fmp-raw`, modify `docs/phase1-exact-gap-queue.json`, request OIDC, or call Supabase.
- Normal Phase 4 tooling exposes only `development` and `validation`; `final` fails before manifest or Parquet I/O.
- Keep accepted Phase 3 execution/risk semantics unchanged.
- Costs/risk stay fixed: historical BID/ASK, adverse slippage `{0.2, 0.5, 1.0}` pips per fill, zero commission, zero financing, requested risk `0.25%`, hard trade max `0.50%`, simultaneous max `1.00%`, daily halt `1.50%`.
- Strategy analysis uses complete closed midpoint bars only and preserves DEC-018 true-known timing.
- Phase 4 remains ACTIVE after this family; Phase 5 remains UNSTARTED; real-money trading remains locked.

---

### Task 1: Freeze trend-window configuration and SMA context

**Files:**
- Create: `src/fmp/strategies/trend_continuation.py`
- Create: `tests/test_phase4_trend_continuation.py`

**Interfaces:**

```python
@dataclass(frozen=True, slots=True)
class TrendContinuationConfig:
    trend_window_id: str
    target_r_multiple: float
    timeframe: str


def duration_to_bars(timeframe: str, hours: int) -> int: ...
```

- [ ] **Step 1: Write RED configuration/context tests**

Add `unittest` cases asserting:

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

Build exact midpoint-close sequences proving LONG context requires `fast_sma > slow_sma` plus rising slow SMA, SHORT is the inverse, equality is neutral, and a cadence gap inside either current or prior slow window makes that observation ineligible.

- [ ] **Step 2: Run RED test**

```bash
python -m unittest tests.test_phase4_trend_continuation -v
```

Expected: import failure for `fmp.strategies.trend_continuation`.

- [ ] **Step 3: Implement minimal helpers**

Use exact constants:

```python
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_TREND_WINDOWS = {"A": (2, 8), "B": (4, 16), "C": (8, 32)}
_ALLOWED_TARGET_R = frozenset({1.0, 1.5})
```

`duration_to_bars()` must require exact divisibility of `hours * 60` by timeframe width. Add midpoint OHLC helpers and an internal context helper that consumes only contiguous closed bars.

- [ ] **Step 4: Run GREEN test**

```bash
python -m unittest tests.test_phase4_trend_continuation -v
```

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

**Interface:**

```python
def generate_trend_continuation_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: TrendContinuationConfig,
) -> tuple[SignalCandidate, ...]: ...
```

- [ ] **Step 1: Add RED golden tests**

Cover all frozen strategy semantics:

1. LONG previous close `<= previous fast SMA`, current close `> current fast SMA`, LONG context => LONG candidate.
2. SHORT symmetric case.
3. Intrabar fast-SMA touch without close-cross => no directional candidate.
4. First qualifying directional signal only per London date.
5. No qualifying signal => exactly one deterministic `NO_TRADE` candidate for that session.
6. LONG stop = minimum midpoint low of current signal bar plus previous two closed bars.
7. SHORT stop = maximum midpoint high of the same three bars.
8. Targets equal signal midpoint close ± `1.0R` / `1.5R`.
9. Missing SMA-history cadence never shortens a window.
10. Missing one of the three stop bars makes that observation ineligible.
11. Winter/summer London DST maps 08:00–14:00 observation labels and exact 16:00 exit correctly.
12. Missing exact 16:00-local bar yields `Direction.NO_TRADE` with `INCOMPLETE_SESSION`.
13. `signal_known_timestamp_utc == observation_bar_timestamp_utc + timeframe_width`.
14. Candidate equality and `stable_json_bytes()` are deterministic.

Use stable reason codes `CONTINUATION_LONG`, `CONTINUATION_SHORT`, `NO_CONTINUATION`, and `INCOMPLETE_SESSION`.

- [ ] **Step 2: Run RED tests**

```bash
python -m unittest tests.test_phase4_trend_continuation -v
```

Expected: failures for missing candidate-generation behavior.

- [ ] **Step 3: Implement candidate generation**

Rules are exact:

```python
# Eligible London-local observation labels: 08:00 <= label <= 14:00.
# Use only fully closed midpoint bars.
# First directional signal only per London date.
# Stop = 3-bar structural midpoint extreme.
# Target = frozen signal midpoint close +/- target_r_multiple * R.
# signal_known = observation label + timeframe width.
# latest_exit = exact 16:00 Europe/London on the same London date.
```

Sort deterministically, require exactly one symbol, reject duplicate `(timestamp_utc, symbol)` identities, and never perform fills, sizing, account state, or PnL here.

- [ ] **Step 4: Add next-bar gap integration test**

Use `candidate_to_decision()` and `run_backtest()` with a next executable reference entry beyond the frozen target or stop. Assert no position opens and Phase 3 returns `RejectionCode.INVALID_STOP_TARGET`. Do not repair the candidate after observing the gap.

- [ ] **Step 5: Run focused + Phase 3 regression tests**

```bash
python -m unittest tests.test_phase4_trend_continuation tests.test_phase3_engine tests.test_phase3_acceptance -v
```

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

```python
TREND_CONTINUATION_GRID = (
    ("A", 1.0), ("A", 1.5),
    ("B", 1.0), ("B", 1.5),
    ("C", 1.0), ("C", 1.5),
)
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)


def run_trend_continuation_grid(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    split_name: str,
    code_commit: str,
) -> dict[str, object]: ...
```

- [ ] **Step 1: Write RED grid/reuse/final-lock tests**

Mock `load_processed_bars()` and `generate_trend_continuation_candidates()` to prove loader called once, generator called six times, each config produces three cost rows, total rows = 18, candidate SHA is reused across the three slippage scenarios, `requested_risk_fraction == 0.0025`, risk/commission/financing identities are unchanged, and `split_name="final"` raises before loader invocation.

- [ ] **Step 2: Run RED test**

```bash
python -m unittest tests.test_phase4_trend_continuation_research -v
```

Expected: missing `fmp.research.trend_continuation`.

- [ ] **Step 3: Implement runner by composing common layers**

Use exact identities:

```python
TREND_CONTINUATION_FAMILY_ID = "trend_continuation"
TREND_CONTINUATION_STRATEGY_VERSION = "fmp-trend-continuation-v1"
RESULT_PROTOCOL = "fmp-phase4-trend-continuation-grid-v1"
STARTING_EQUITY_USD = 100_000.0
REQUESTED_RISK_FRACTION = 0.0025
```

Call `allowed_split()` before manifest reads, SHA the manifest bytes, call `load_processed_bars()`, generate/adapt candidates once per strategy config, run the accepted Phase 3 engine three times per config, call `compute_research_metrics()`, and retain every row.

- [ ] **Step 4: Run GREEN + reporting regression**

```bash
python -m unittest tests.test_phase4_trend_continuation_research tests.test_phase4_research_reporting -v
```

- [ ] **Step 5: Commit**

```bash
git add src/fmp/research/trend_continuation.py tests/test_phase4_trend_continuation_research.py
git commit -m "[phase1-no-source] Add trend continuation research grid"
```

---

### Task 4: Add source-free CLI with parser-level final lock

**Files:**
- Create: `scripts/phase4_trend_continuation.py`
- Create: `tests/test_phase4_trend_continuation_cli.py`

**CLI surface:**

```text
--dataset-root PATH
--manifest PATH
--symbol {EURUSD,GBPUSD,USDJPY}
--timeframe {5m,15m,1h}
--split {development,validation}
--out PATH
--code-commit SHA
```

- [ ] **Step 1: Write RED CLI tests**

Assert `--help` exposes only the fixed symbols/timeframes/splits, `--split final` exits during argument parsing, and the script imports only the research runner plus benchmark writer rather than any source/Supabase/OIDC path.

- [ ] **Step 2: Run RED test**

```bash
python -m unittest tests.test_phase4_trend_continuation_cli -v
```

- [ ] **Step 3: Implement CLI**

Create `argparse` choices exactly as above; call `run_trend_continuation_grid(...)`; persist with `write_benchmark_artifacts(...)`; print deterministic JSON containing the benchmark path and artifact manifest.

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

### Task 5: Add fixed 18-cell source-free workflow

**Files:**
- Create: `.github/workflows/phase4-trend-continuation.yml`
- Create: `tests/test_phase4_trend_continuation_workflow.py`

**Workflow contract:**

```yaml
name: phase4-trend-continuation
permissions:
  contents: read
  actions: read
jobs:
  benchmark:
    runs-on: ubuntu-latest
    timeout-minutes: 90
    strategy:
      fail-fast: false
```

Matrix = 3 accepted Phase 2 artifacts × 3 timeframes × 2 splits = 18 cells. Every benchmark artifact contains 18 rows = 6 configs × 3 slippage scenarios.

- [ ] **Step 1: Write RED workflow tests**

Freeze these accepted artifacts:

```text
EURUSD 10325737935 db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3
GBPUSD 10326096831 fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2
USDJPY 10327600628 6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72
```

Assert ZIP SHA verification occurs before `unzip`; no `id-token`, Supabase, Dukascopy, source acquisition, raw mutation, or final split exists; evidence verification requires protocol `fmp-phase4-trend-continuation-grid-v1`, exact `GITHUB_SHA`, and `len(configuration_rows) == 18`; upload uses `if-no-files-found: error`.

- [ ] **Step 2: Run RED workflow test**

```bash
python -m unittest tests.test_phase4_trend_continuation_workflow -v
```

- [ ] **Step 3: Implement workflow**

Use the same accepted artifact-download mechanism already used by the Phase 4 session-breakout workflow, but invoke `scripts/phase4_trend_continuation.py`, write under `.phase4-trend-continuation/`, verify the trend protocol/18 rows, and upload `phase4-trend-continuation-${symbol}-${timeframe}-${split}-${github.sha}`.

- [ ] **Step 4: Validate YAML and focused tests**

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
- Decision: `DEC-019 — Phase 4 trend-continuation baseline protocol`.
- Experiment: `EXP-20260914-002 — Trend continuation baseline`, status `PLANNED`.

- [ ] **Step 1: Write RED state tests**

Require DEC-019 to freeze 2h/8h, 4h/16h, 8h/32h windows; 1.0R/1.5R targets; 08:00–14:00 London labels; exact 16:00 exit; three-bar structural stop; 324 total rows; and unchanged DEC-018 split/cost/risk locks. Require EXP-002 to say `Final-test touched?: NO`, contain no result summary or conclusion, and remain `PLANNED`. Require project state to keep the session-breakout candidate frozen while marking trend continuation as the active second family.

- [ ] **Step 2: Run RED test**

```bash
python -m unittest tests.test_phase4_trend_continuation_state -v
```

- [ ] **Step 3: Write only the predeclaration**

Do not prefill trade counts, returns, candidate claims, PASS/FAIL, result summary, or conclusion.

- [ ] **Step 4: Run GREEN test**

```bash
python -m unittest tests.test_phase4_trend_continuation_state -v
```

- [ ] **Step 5: Commit**

```bash
git add docs/decision-log.md docs/experiment-log.md docs/project-state.md tests/test_phase4_trend_continuation_state.py
git commit -m "[phase1-no-source] Predeclare trend continuation experiment"
```

---

### Task 7: Full verification and guarded implementation merge

**Files:** none beyond branch review.

- [ ] **Step 1: Run full verification**

```bash
python -m unittest discover -s tests -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m compileall -q src scripts
```

- [ ] **Step 2: Open/update the draft implementation PR**

Title must contain `[phase1-no-source]` from creation. Confirm the diff excludes `docs/phase1-exact-gap-queue.json`, Supabase, raw paths, Phase 1 acquisition implementation, final-test access, Phase 5, broker/live, and real-money changes.

- [ ] **Step 3: Require exact-head PR checks**

Require `tests` SUCCESS, `phase3-acceptance` SUCCESS unchanged, both Phase 1 source-capable PR jobs SKIPPED, and no unresolved review comments.

- [ ] **Step 4: Ready and recheck Phase 1 guards**

After draft→ready, inspect the ready-triggered Phase 1 jobs and require their jobs to be SKIPPED.

- [ ] **Step 5: Squash merge the exact verified head**

Use an expected-head SHA and a merge title containing `[phase1-no-source]`.

- [ ] **Step 6: Verify merged `main`**

Require ordinary tests and Phase 3 acceptance green. Confirm no Phase 1 acquisition-capable push workflow triggered. It is acceptable if the already-source-free session-breakout benchmark also retriggers because its existing path filter covers shared strategy/research directories; do not interpret that as source activity.

---

### Task 8: Run and independently validate the merged-main 18-cell benchmark

**Files:** no repository write until evidence review is complete.

- [ ] **Step 1: Require all 18 trend-continuation matrix jobs SUCCESS**

Do not rerun an unfavorable economic result. Rerun only a demonstrably transient infrastructure failure without code/data/config change, and record that fact.

- [ ] **Step 2: Download all 18 artifacts and independently verify each**

For every ZIP verify:

- GitHub artifact digest against downloaded bytes;
- exactly `benchmark.json` and `manifest.json`;
- manifest SHA/size against persisted benchmark bytes;
- merged-main code SHA;
- pair/timeframe/split identity;
- accepted Phase 2 processed-manifest SHA/schema;
- exactly 18 ordered configuration rows;
- candidate SHA reuse across 0.2/0.5/1.0-pip costs for each config;
- finite/internal-consistent counts and metrics.

Complete evidence must total exactly **324 rows**.

- [ ] **Step 3: Apply only the predeclared assessment rules**

Compare development with validation at 0.2 pip; then inspect 0.5/1.0-pip stress, neighboring window/target stability, yearly concentration, trade count, drawdown, recovery, and top-winner dependence. Do not select by maximum development return.

- [ ] **Step 4: Freeze the outcome without final-test access**

Classify EXP-002 as PASS, FAIL, or INCONCLUSIVE. If retaining a serious candidate, freeze exact pair/timeframe/window/target. Always keep `Final-test touched?: NO`.

---

### Task 9: Record evidence in a separate docs-only closure PR

**Files:**
- Create: `docs/phase4-trend-continuation-evidence.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Modify: `tests/test_phase4_trend_continuation_state.py`

- [ ] **Step 1: Change the state test from predeclaration to completed-evidence assertions**

Require the observed experiment status/conclusion plus these invariant locks:

```text
Final-test touched?: NO
Phase 4 — ACTIVE
Phase 5 — UNSTARTED
Real-money trading remains locked
```

- [ ] **Step 2: Write durable evidence**

Record exact merged-main workflow run, code SHA, all 18 artifact IDs/digests, 18/18 job result, 324/324 rows, independent validation-error count, development/validation economics, cost sensitivity, yearly concentration, drawdown/trade-count/top-winner notes, and the exact PROMOTE/REJECT/REVISE/NEED_MORE_DATA reason.

- [ ] **Step 3: Update experiment log and project state**

Replace `PLANNED` with the evidence-supported terminal experiment status. Preserve the frozen session-breakout candidate unchanged. Set the next admitted family to **mean reversion**, but do not implement it in this closure PR.

- [ ] **Step 4: Verify and merge the docs-only closure PR**

Require full tests green, Phase 3 acceptance green, Phase 1 source-capable PR guards SKIPPED, exact diff scope, and no final-test/source/raw/Supabase/Phase5/live/real-money change. Squash merge with `[phase1-no-source]`, then verify merged-main tests and absence of any Phase 1 acquisition-capable push workflow.

---

## Execution Boundary

Completing this plan closes only the **trend-continuation experiment slice**. It does not make Phase 4 PASS, create `fmp-v1-phase4-baselines`, access the final-test period, start Phase 5, or authorize live/real-money trading. The next admitted family after a clean trend-continuation closure is mean reversion.