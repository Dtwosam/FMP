# Phase 3 Backtesting Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic event-driven Phase 3 backtesting engine with realistic bid/ask execution, explicit costs, conservative stop/target handling, independent risk controls, auditable rejection records, and deterministic reporting artifacts.

**Architecture:** Keep Polars as the market-data layer but process trading state chronologically through explicit broker-independent contracts. Separate contracts, costs, risk, execution, orchestration, and reporting so later shadow/demo modes can reuse decision/risk/order semantics without importing historical-data logic.

**Tech Stack:** Python >=3.11, standard library dataclasses/enums/decimal/hashlib/json/pathlib, Polars 1.44.2, unittest.

**Spec:** `docs/superpowers/specs/2026-09-14-phase3-backtester-design.md`

## Global Constraints

- V1 instruments remain exactly EURUSD, GBPUSD, USDJPY.
- Phase 2 checkpoint remains `fmp-v1-phase2-normalized-data`; raw data is immutable.
- Every Phase 3 commit and PR title includes `[phase1-no-source]`.
- Do not invoke source acquisition, mutate `fmp-raw`, modify `docs/phase1-exact-gap-queue.json`, or start Phase 4.
- Python remains >=3.11 and no new package dependency is introduced.
- Account currency is USD.
- Default risk/trade is 0.25% current realized risk equity; hard maximum requested risk/trade is 0.50%; simultaneous open risk is 1.00%; daily realized-loss halt is 1.50% of UTC day-start realized risk equity.
- Decisions cannot execute on their decision bar; earliest fill is the next chronological bar for that symbol.
- LONG enters on ASK and exits on BID; SHORT enters on BID and exits on ASK.
- Stop wins when stop and target are both reachable in one bar and ordering is unknowable.
- Spread is represented by bid/ask quotes and is never added again as a synthetic cost.
- All explicit slippage is adverse to the trader.
- Same-timestamp processing is deterministic: position exits first, then new decisions ordered by stable `decision_id`.
- Repeated equivalent runs must produce byte-identical deterministic artifacts and identical SHA-256 digests.

---

## File Map

### New production files

- `src/fmp/contracts.py` — stable enums/dataclasses for decisions, risk assessments, order intents, trade/rejection/run records.
- `src/fmp/risk/__init__.py` — public risk exports.
- `src/fmp/risk/sizing.py` — USD loss-per-unit and integer-unit sizing for supported pairs.
- `src/fmp/risk/policy.py` — risk configuration, daily halt state, risk reservation/release, and approval/rejection logic.
- `src/fmp/backtest/__init__.py` — public backtest exports and `BACKTEST_ENGINE_VERSION`.
- `src/fmp/backtest/costs.py` — pip conversion, adverse slippage, commission, financing interfaces/implementations.
- `src/fmp/backtest/execution.py` — entry fills, executable-side stop/target reachability, gap handling, ambiguity policy, EOD close.
- `src/fmp/backtest/engine.py` — chronological deterministic state machine over bars and scripted decisions.
- `src/fmp/reporting/__init__.py` — public reporting exports.
- `src/fmp/reporting/backtest.py` — whole-run metrics plus stable JSON artifact writer/manifest.

### New tests

- `tests/test_phase3_contracts.py`
- `tests/test_phase3_costs.py`
- `tests/test_phase3_risk.py`
- `tests/test_phase3_execution.py`
- `tests/test_phase3_engine.py`
- `tests/test_phase3_reporting.py`
- `tests/test_phase3_acceptance.py`

### Documentation modified near completion

- `docs/project-state.md`
- `docs/decision-log.md`
- `docs/phase3-acceptance-evidence.md` only after real Phase 3 acceptance evidence exists.

---

### Task 1: Freeze Phase 3 contracts and input invariants

**Files:**
- Create: `src/fmp/contracts.py`
- Test: `tests/test_phase3_contracts.py`

**Interfaces:**
- Produces enums: `Direction`, `OrderSide`, `ExitReason`, `RejectionCode`.
- Produces dataclasses: `QuoteBar`, `Decision`, `RiskAssessment`, `OrderIntent`, `Position`, `TradeRecord`, `RejectionRecord`, `BacktestRun`.
- Produces `validate_quote_bars(bars: Sequence[QuoteBar]) -> None`.
- Later tasks consume these exact names.

- [ ] **Step 1: Write failing contract tests**

Create tests that instantiate the frozen records and assert enum string values. Include UTC validation, supported-symbol validation, positive finite executable prices, `ask >= bid` for each OHLC field, OHLC internal consistency, strictly increasing `(symbol, timestamp)` identities, duplicate rejection, and deterministic `decision_id` requirement.

Representative assertions:

```python
class Phase3ContractTests(unittest.TestCase):
    def test_direction_values_are_stable(self) -> None:
        self.assertEqual(Direction.LONG.value, "LONG")
        self.assertEqual(Direction.SHORT.value, "SHORT")
        self.assertEqual(Direction.NO_TRADE.value, "NO_TRADE")

    def test_quote_bar_rejects_non_utc_timestamp(self) -> None:
        with self.assertRaisesRegex(ValueError, "UTC"):
            QuoteBar(
                timestamp_utc=datetime(2026, 9, 14, 0, 0),
                symbol="EURUSD",
                bid_open=1.1000, bid_high=1.1010, bid_low=1.0990, bid_close=1.1005,
                ask_open=1.1002, ask_high=1.1012, ask_low=1.0992, ask_close=1.1007,
            )
```

- [ ] **Step 2: Run focused tests and observe RED**

Run:

```bash
python -m unittest tests.test_phase3_contracts -v
```

Expected: import/module failure because `fmp.contracts` does not exist.

- [ ] **Step 3: Implement minimal frozen contracts**

Use `@dataclass(frozen=True, slots=True)` and `str, Enum` values. Minimum semantic fields:

```python
class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NO_TRADE = "NO_TRADE"

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class ExitReason(str, Enum):
    STOP = "STOP"
    TARGET = "TARGET"
    END_OF_DATA = "END_OF_DATA"

class RejectionCode(str, Enum):
    NO_TRADE = "NO_TRADE"
    TIMING_CONTRACT = "TIMING_CONTRACT"
    INVALID_QUOTE = "INVALID_QUOTE"
    INVALID_STOP_TARGET = "INVALID_STOP_TARGET"
    PER_TRADE_RISK = "PER_TRADE_RISK"
    SIMULTANEOUS_RISK = "SIMULTANEOUS_RISK"
    DAILY_HALT = "DAILY_HALT"
    INVALID_SIZE = "INVALID_SIZE"
```

`QuoteBar` contains timestamp/symbol plus bid/ask OHLC. `Decision` contains `decision_id`, symbol, `decision_timestamp_utc`, direction, `earliest_executable_timestamp_utc`, requested risk fraction, stop, optional target, and reason metadata. `OrderIntent` contains the approved units and monetary risk. `Position` adds entry timestamp/price and reserved risk. `TradeRecord` stores entry/exit, gross/cost/net PnL, exit reason, ambiguity flag, and risk-equity before/after. `BacktestRun` stores deterministic identity plus tuples of trades/rejections/equity checkpoints and metrics mapping.

Validate only invariant facts in dataclass `__post_init__`; do not embed policy decisions such as risk caps in the contracts module.

- [ ] **Step 4: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_contracts -v
```

Expected: all contract tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/fmp/contracts.py tests/test_phase3_contracts.py
git commit -m "[phase1-no-source] Freeze Phase 3 trading contracts"
```

---

### Task 2: Implement pip conventions and explicit cost models

**Files:**
- Create: `src/fmp/backtest/__init__.py`
- Create: `src/fmp/backtest/costs.py`
- Test: `tests/test_phase3_costs.py`

**Interfaces:**
- Produces constant `BACKTEST_ENGINE_VERSION = "fmp-backtest-v1"`.
- Produces `pip_size(symbol: str) -> float`.
- Produces `apply_adverse_slippage(price: float, *, side: OrderSide, pips: float, symbol: str) -> float`.
- Produces protocol-like interfaces `CommissionModel.cost_usd(...)` and `FinancingModel.cost_usd(...)`.
- Produces `ZeroCommission`, `FixedCommissionPerMillion`, `ZeroFinancing`.

- [ ] **Step 1: Write failing cost tests**

Cover:

```python
self.assertEqual(pip_size("EURUSD"), 0.0001)
self.assertEqual(pip_size("GBPUSD"), 0.0001)
self.assertEqual(pip_size("USDJPY"), 0.01)
self.assertAlmostEqual(
    apply_adverse_slippage(1.1000, side=OrderSide.BUY, pips=1.5, symbol="EURUSD"),
    1.10015,
)
self.assertAlmostEqual(
    apply_adverse_slippage(150.00, side=OrderSide.SELL, pips=2.0, symbol="USDJPY"),
    149.98,
)
```

Also assert negative slippage pips and unsupported symbols fail closed. Test zero models and deterministic fixed commission in USD per million units per side.

- [ ] **Step 2: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_costs -v
```

Expected: missing module/symbol failures.

- [ ] **Step 3: Implement cost primitives**

Rules:

```python
PIP_SIZES = {"EURUSD": 0.0001, "GBPUSD": 0.0001, "USDJPY": 0.01}

def apply_adverse_slippage(price, *, side, pips, symbol):
    delta = pips * pip_size(symbol)
    return price + delta if side is OrderSide.BUY else price - delta
```

`FixedCommissionPerMillion(usd_per_million_per_side: float)` returns `abs(units) / 1_000_000 * rate` for one execution side. Financing receives symbol/side/units/entry/exit timestamps and returns USD cost; `ZeroFinancing` returns exactly `0.0`.

- [ ] **Step 4: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_costs -v
```

- [ ] **Step 5: Commit**

```bash
git add src/fmp/backtest/__init__.py src/fmp/backtest/costs.py tests/test_phase3_costs.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 cost models"
```

---

### Task 3: Implement USD risk sizing and policy state

**Files:**
- Create: `src/fmp/risk/__init__.py`
- Create: `src/fmp/risk/sizing.py`
- Create: `src/fmp/risk/policy.py`
- Test: `tests/test_phase3_risk.py`

**Interfaces:**
- Produces `loss_usd_per_unit(symbol: str, entry_price: float, stop_price: float) -> float`.
- Produces `size_units(*, symbol: str, entry_price: float, stop_price: float, allowed_risk_usd: float) -> int`.
- Produces frozen `RiskConfig` with defaults `0.0025`, `0.005`, `0.01`, `0.015`.
- Produces mutable `RiskState` storing realized risk equity, UTC day-start basis/day realized PnL, halt state, and reserved monetary risk by position ID.
- Produces `assess_decision(...) -> RiskAssessment`, `reserve_risk(...)`, `release_risk(...)`, `record_realized_pnl(...)`, `roll_utc_day(...)`.

- [ ] **Step 1: Write failing sizing tests**

Hand calculations:

```python
# EURUSD: $25 risk, 10 pip stop -> 25,000 units
self.assertEqual(size_units(
    symbol="EURUSD", entry_price=1.1000, stop_price=1.0990, allowed_risk_usd=25.0
), 25000)

# USDJPY: loss/unit = 0.10 / 149.90 USD; floor sizing
expected = math.floor(25.0 / (abs(150.00 - 149.90) / 149.90))
self.assertEqual(size_units(
    symbol="USDJPY", entry_price=150.00, stop_price=149.90, allowed_risk_usd=25.0
), expected)
```

Also test invalid zero/negative stop distance, unsupported symbol, non-positive allowed risk.

- [ ] **Step 2: Write failing risk-policy tests**

Cover exact boundaries:

- 0.25% default on $10,000 => $25 approved risk.
- requested 0.50% is allowed; >0.50% rejects `PER_TRADE_RISK`.
- existing reserved $75 on $10,000 plus new $25 is allowed exactly at 1.00%; one cent above rejects `SIMULTANEOUS_RISK`.
- closing a position releases its exact reserved risk.
- realized risk equity changes only with realized net PnL.
- UTC day-start basis is snapshotted before that day's PnL.
- at <= -1.50% day loss new entries reject `DAILY_HALT`.
- next UTC date resets halt and snapshots current realized risk equity.

- [ ] **Step 3: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_risk -v
```

- [ ] **Step 4: Implement sizing functions**

Use float inputs but validate `math.isfinite`. Return integer units via `math.floor`. USDJPY uses the frozen stop-price conversion denominator:

```python
if symbol in {"EURUSD", "GBPUSD"}:
    loss = abs(entry_price - stop_price)
elif symbol == "USDJPY":
    loss = abs(entry_price - stop_price) / stop_price
```

- [ ] **Step 5: Implement risk policy/state**

`RiskState.risk_equity_usd` starts at configured starting equity and changes only by realized net PnL. Daily halt logic calls `roll_utc_day(timestamp)` before assessments/realizations. A trade reserves the approved USD amount, not recomputed percentage risk.

`assess_decision` validates direction-specific stop geometry using the reference executable entry price supplied by the engine, applies requested/default risk fraction, enforces hard and simultaneous caps, then sizes units. If size is <=0 or sizing fails, return `INVALID_SIZE` rather than throwing from normal risk rejection paths.

- [ ] **Step 6: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_risk -v
```

- [ ] **Step 7: Commit**

```bash
git add src/fmp/risk tests/test_phase3_risk.py
git commit -m "[phase1-no-source] Add Phase 3 risk sizing and controls"
```

---

### Task 4: Implement executable-side fill and exit semantics

**Files:**
- Create: `src/fmp/backtest/execution.py`
- Test: `tests/test_phase3_execution.py`

**Interfaces:**
- Consumes `QuoteBar`, `Direction`, `OrderSide`, `OrderIntent`, `Position`, `ExitReason`.
- Consumes cost primitives from Task 2.
- Produces `entry_reference_price(bar, direction) -> float`.
- Produces `fill_entry(intent, bar, *, slippage_pips, commission_model) -> Position` plus entry commission result as needed by exact return type chosen in implementation.
- Produces `evaluate_exit(position, bar, *, slippage_pips, commission_model, financing_model) -> ExitFill | None`.
- Produces `close_end_of_data(position, bar, ...) -> ExitFill`.
- `ExitFill` is a small frozen internal/public dataclass in `execution.py` containing timestamp, price, reason, ambiguous flag, commission, financing.

- [ ] **Step 1: Write failing entry-side tests**

Assert a LONG next-bar entry uses `ask_open`, SHORT uses `bid_open`, then applies BUY-up / SELL-down slippage.

- [ ] **Step 2: Write failing stop/target tests**

Use hand-built `QuoteBar` fixtures to cover all required cases:

- LONG stop checks BID low and fills SELL at stop minus slippage.
- SHORT stop checks ASK high and fills BUY at stop plus slippage.
- LONG target checks BID high.
- SHORT target checks ASK low.
- both reachable => `STOP` and `ambiguous=True`.
- long bar opens below stop => exit at worse `bid_open`, not stop.
- short bar opens above stop => exit at worse `ask_open`, not stop.
- favorable target gap still fills declared target, not improved open.
- EOD LONG closes from BID; EOD SHORT from ASK.

- [ ] **Step 3: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_execution -v
```

- [ ] **Step 4: Implement execution semantics minimally**

Freeze side mapping:

```python
entry_side = OrderSide.BUY if direction is Direction.LONG else OrderSide.SELL
exit_side = OrderSide.SELL if direction is Direction.LONG else OrderSide.BUY
```

For each bar after entry, compute executable open/high/low on BID for LONG and ASK for SHORT. Evaluate adverse gap-through-stop first, then stop/target reachability. If both reachable choose stop. If only target reachable, reference price is target even if open is beyond it favorably. Apply adverse slippage exactly once to every simulated execution price.

- [ ] **Step 5: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_execution -v
```

- [ ] **Step 6: Commit**

```bash
git add src/fmp/backtest/execution.py tests/test_phase3_execution.py
git commit -m "[phase1-no-source] Add conservative Phase 3 execution semantics"
```

---

### Task 5: Implement chronological backtest state machine

**Files:**
- Create: `src/fmp/backtest/engine.py`
- Test: `tests/test_phase3_engine.py`

**Interfaces:**
- Produces frozen `BacktestConfig` with starting equity, slippage pips, `RiskConfig`, commission model, financing model, processed-manifest identity, timeframe, requested start/end, code commit, strategy/fixture configuration.
- Produces `run_backtest(*, bars: Sequence[QuoteBar], decisions: Sequence[Decision], config: BacktestConfig) -> BacktestRun`.
- Consumes Tasks 1-4.

- [ ] **Step 1: Write failing timing tests**

Provide bars at `00:00`, `00:01`, `00:02`. A decision stamped `00:00` with earliest executable `00:01` must fill only at `00:01`. A decision with earliest executable <= decision timestamp must produce `TIMING_CONTRACT` rejection or fail input validation according to the contract tests; it must never fill on `00:00`.

- [ ] **Step 2: Write failing deterministic event-order tests**

At one timestamp, create an existing position whose target closes and a new decision whose risk would be rejected unless the old position's reserved risk is released. Assert exit occurs first and new entry is approved. Create two simultaneous decisions with IDs `A` and `B`; assert decision order is lexicographic/stable by `decision_id` and repeat runs produce the same winner when the second exceeds risk capacity.

- [ ] **Step 3: Write failing rejection/NO_TRADE tests**

Assert `NO_TRADE` produces a `RejectionRecord`/decision record with code `NO_TRADE` and never becomes a position. Assert invalid stop geometry, daily halt, simultaneous cap, and invalid size are retained with their stable codes.

- [ ] **Step 4: Write failing realized-equity/daily-halt tests**

Construct a hand-calculable losing trade that crosses the 1.50% day threshold. Verify subsequent same-day decision rejection, existing positions remain untouched, and a next-UTC-day decision is eligible after reset using the new realized risk-equity basis.

- [ ] **Step 5: Write failing EOD close test**

Leave a position open on the last bar and assert a deterministic `END_OF_DATA` trade closes at the correct executable side with costs included.

- [ ] **Step 6: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_engine -v
```

- [ ] **Step 7: Implement chronological engine**

Algorithm:

```text
validate bars and decisions
index decisions by earliest executable timestamp + symbol
for each timestamp in chronological order:
    roll risk day
    evaluate/close existing positions first in stable position-id order
    release risk and record realized net PnL immediately on close
    evaluate decisions scheduled for this timestamp in decision_id order
      preserve NO_TRADE
      validate quote/stop/target/timing
      compute reference entry side price
      risk-assess and record rejection or create/reserve position
      after entry, evaluate same-bar stop/target using the just-opened position
at final bar:
    close remaining positions as END_OF_DATA in stable position-id order
compute reporting metrics and deterministic run identity
```

A newly opened position may stop/target on its entry bar after the entry open because those high/low observations occur after the open and ordering is unknowable; when both thresholds are reachable, stop wins.

- [ ] **Step 8: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_engine -v
```

- [ ] **Step 9: Commit**

```bash
git add src/fmp/backtest/engine.py tests/test_phase3_engine.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 backtest engine"
```

---

### Task 6: Implement deterministic metrics and artifact serialization

**Files:**
- Create: `src/fmp/reporting/__init__.py`
- Create: `src/fmp/reporting/backtest.py`
- Test: `tests/test_phase3_reporting.py`

**Interfaces:**
- Produces `compute_backtest_metrics(*, starting_equity_usd: float, trades: Sequence[TradeRecord], equity_checkpoints: Sequence[tuple[datetime, float]]) -> dict[str, object]`.
- Produces `write_backtest_artifacts(run: BacktestRun, out_dir: Path) -> dict[str, object]`.
- Manifest protocol: `fmp-phase3-backtest-artifacts-v1`.

- [ ] **Step 1: Write failing metric tests from hand-calculated trades**

Use closed-trade net PnLs `[100.0, -50.0, 25.0, -25.0]` from starting equity `$10,000` and assert:

- net PnL = 50;
- net return = 0.005;
- trade count = 4;
- win rate = 0.5;
- average win = 62.5;
- average loss = -37.5;
- expectancy = 12.5;
- gross profit = 125;
- gross loss magnitude = 75;
- profit factor = 125/75;
- longest winning and losing streak = 1.

Provide an explicit realized-equity checkpoint sequence and assert maximum drawdown in USD and fraction from prior realized-equity peak. Recovery factor is net profit / max drawdown USD when max drawdown >0, otherwise `None`.

- [ ] **Step 2: Write failing deterministic artifact tests**

Write the same `BacktestRun` to two temp directories. Assert identical relative filenames and identical bytes/SHA for:

- `summary.json`
- `trades.jsonl`
- `rejections.jsonl`
- `metrics.json`
- `manifest.json`

Assert manifest records byte size/SHA-256 for the four data artifacts and does not hash itself recursively.

- [ ] **Step 3: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_reporting -v
```

- [ ] **Step 4: Implement metrics**

Use only deterministic arithmetic over stored trade/account state. Define zero-trade behavior explicitly: expectancy/win rate/averages/profit factor/recovery factor become `None` where denominator/sample does not exist; net PnL is `0.0`; net return is `0.0`; trade count is `0`.

- [ ] **Step 5: Implement stable serialization**

Mirror Phase 2 atomic-write discipline without importing Phase 2 private helpers: UTF-8, sorted JSON keys, stable separators/indent, `allow_nan=False`, terminal newline, ISO UTC timestamps with `Z`, no wall-clock `generated_at` in hashed payloads. JSONL records are ordered by stable IDs/timestamps and each line uses sorted keys.

- [ ] **Step 6: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_reporting -v
```

- [ ] **Step 7: Commit**

```bash
git add src/fmp/reporting tests/test_phase3_reporting.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 reporting"
```

---

### Task 7: Prove the full hand-calculated Phase 3 golden scenarios

**Files:**
- Create: `tests/test_phase3_acceptance.py`
- Modify only if a proven defect requires it: Phase 3 production files from Tasks 1-6.

**Interfaces:**
- Exercises public `run_backtest` plus reporting artifact writer.
- No strategy module is introduced; decisions are scripted fixtures.

- [ ] **Step 1: Add long bid/ask golden scenario**

Use zero slippage/commission and a LONG decision whose next bar has `ask_open=1.1002`, later target/close on BID at `1.1010`. Assert exact entry/exit sides, gross/net PnL, units, timestamps, and risk state.

- [ ] **Step 2: Add short bid/ask golden scenario**

Use SHORT `bid_open` entry and ASK exit with hand-calculated PnL.

- [ ] **Step 3: Add ambiguity and gap golden scenarios**

Explicitly cover stop+target same bar => stop, and gap-through-stop => worse open.

- [ ] **Step 4: Add JPY and non-JPY sizing golden scenarios**

Assert the same calculations from Task 3 through the complete engine rather than only sizing functions.

- [ ] **Step 5: Add risk-control golden scenarios**

Assert per-trade cap rejection, simultaneous-risk rejection, exit-before-entry release, daily halt, and next-day reset through `run_backtest`.

- [ ] **Step 6: Add cost golden scenario**

Use nonzero slippage and fixed commission. Hand-calculate entry/exit prices, gross PnL, total explicit costs, and net PnL.

- [ ] **Step 7: Add repeated-run equality test**

Run the exact same bars/decisions/config twice, compare dataclass-normalized output and artifact digests byte-for-byte.

- [ ] **Step 8: Run acceptance tests RED/GREEN as defects are resolved**

```bash
python -m unittest tests.test_phase3_acceptance -v
```

Do not weaken a golden expectation to match an implementation bug. Fix the smallest production defect and rerun.

- [ ] **Step 9: Commit**

```bash
git add tests/test_phase3_acceptance.py src/fmp/contracts.py src/fmp/risk src/fmp/backtest src/fmp/reporting
git commit -m "[phase1-no-source] Prove Phase 3 golden scenarios"
```

---

### Task 8: Update Phase 3 active-state and freeze the daily-risk interpretation

**Files:**
- Modify: `docs/project-state.md`
- Modify: `docs/decision-log.md`

**Interfaces:**
- Adds `DEC-016 — Phase 3 backtester semantics`.
- Records Phase 3 as ACTIVE, not PASS.

- [ ] **Step 1: Update decision log**

Record the newly frozen semantics without changing approved hard limits:

- UTC calendar day-start realized risk equity is the 1.50% daily-loss basis;
- new entries halt for the remainder of that UTC date after threshold is reached;
- exits process before entries at equal timestamps;
- decision IDs provide stable same-timestamp ordering;
- bid/ask execution and stop-wins ambiguity semantics are frozen for the Phase 3 engine;
- no real-money permission changes.

- [ ] **Step 2: Update project state**

Set:

```text
Current phase: Phase 3 — Backtesting Engine
Phase status: ACTIVE
Next milestone: implement and verify the deterministic Phase 3 golden acceptance suite
```

Keep Phase 2 checkpoint/evidence intact and explicitly state Phase 4 has not started.

- [ ] **Step 3: Commit**

```bash
git add docs/project-state.md docs/decision-log.md
git commit -m "[phase1-no-source] Record Phase 3 backtester semantics"
```

---

### Task 9: Full regression verification and PR safety review

**Files:**
- No intended new files unless verification uncovers a defect.

**Interfaces:**
- Proves the implementation branch is ready for PR review, not Phase 3 PASS.

- [ ] **Step 1: Run all focused Phase 3 tests**

```bash
python -m unittest \
  tests.test_phase3_contracts \
  tests.test_phase3_costs \
  tests.test_phase3_risk \
  tests.test_phase3_execution \
  tests.test_phase3_engine \
  tests.test_phase3_reporting \
  tests.test_phase3_acceptance -v
```

Expected: zero failures/errors.

- [ ] **Step 2: Run full repository suite**

```bash
python -m unittest discover -s tests -v
```

Expected: zero failures/errors.

- [ ] **Step 3: Compile source/tests**

```bash
python -m compileall -q src tests
```

Expected exit code 0.

- [ ] **Step 4: Inspect branch diff**

Verify:

- only Phase 3 source/tests/docs/spec/plan files changed;
- `docs/phase1-exact-gap-queue.json` is absent;
- no `.github/workflows/phase1-*` source-capable workflow is modified;
- no Supabase/raw/cloud mutation path is added;
- no strategy/Phase 4 implementation appears.

- [ ] **Step 5: Open PR with safety marker from creation time**

Title:

```text
[phase1-no-source] Phase 3 deterministic backtesting engine
```

PR body states Phase 3 remains ACTIVE pending real acceptance artifact inspection and checkpoint review.

- [ ] **Step 6: Require fresh green CI on exact PR head before merge**

Confirm `tests` succeeds and all Phase 1 source-capable PR workflows skip. Merge only the exact verified head with squash title/message containing `[phase1-no-source]`.

- [ ] **Step 7: Verify post-merge main CI and source non-trigger**

After merge, confirm `main` points to the squash commit, the push `tests` workflow succeeds, and no Phase 1 acquisition-capable workflow triggers.

---

### Task 10: Produce and inspect Phase 3 acceptance artifacts before closure

**Files:**
- Create after evidence exists: `docs/phase3-acceptance-evidence.md`
- Modify after evidence exists: `docs/project-state.md`
- Modify after evidence exists: `docs/decision-log.md`

**Interfaces:**
- Closure checkpoint: `fmp-v1-phase3-backtester`.
- This task begins only after the merged engine has produced inspectable deterministic acceptance artifacts.

- [ ] **Step 1: Run a deterministic acceptance fixture on merged main**

Use a small hand-calculable scripted fixture that exercises long, short, costs, one ambiguity, one risk rejection, and daily-halt/reset semantics. Persist the run through `write_backtest_artifacts`.

- [ ] **Step 2: Independently inspect artifacts**

Verify summary/trades/rejections/metrics/manifest contents, SHA/size matches, hand-calculated PnL, reason codes, event order, and repeated-run digest equality.

- [ ] **Step 3: Review Phase 3 acceptance gate line-by-line**

Compare evidence against `docs/build-order.md` and the Phase 3 design acceptance section. Any unmet criterion keeps Phase 3 ACTIVE.

- [ ] **Step 4: Record acceptance evidence only if every gate passes**

Create `docs/phase3-acceptance-evidence.md` with immutable run/code/config/data identities and verified artifact digests.

- [ ] **Step 5: Create checkpoint and formal PASS in separate closure change**

Only after evidence review passes, create checkpoint `fmp-v1-phase3-backtester`, update project state/decision log to PASS, and keep Phase 4 explicitly unstarted until the next approved slice.
