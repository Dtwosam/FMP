# Phase 3 Backtesting Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic event-driven Phase 3 backtesting engine with realistic bid/ask execution, explicit costs, conservative stop/target handling, independent risk controls, auditable rejection records, and deterministic reporting artifacts.

**Architecture:** Keep Polars as the market-data/storage layer, but process trading state chronologically through explicit broker-independent contracts. Separate contracts, costs, risk, execution, reporting, and orchestration so later shadow/demo modes can reuse decision/risk/order semantics without depending on historical-data internals.

**Tech Stack:** Python >=3.11, standard library dataclasses/enums/hashlib/json/math/pathlib/tempfile/os, Polars 1.44.2, unittest.

**Spec:** `docs/superpowers/specs/2026-09-14-phase3-backtester-design.md`

## Global Constraints

- V1 instruments remain exactly `EURUSD`, `GBPUSD`, `USDJPY`.
- Phase 2 checkpoint remains `fmp-v1-phase2-normalized-data`; raw data is immutable.
- Every Phase 3 commit and PR title includes `[phase1-no-source]`.
- Do not invoke source acquisition, mutate `fmp-raw`, modify `docs/phase1-exact-gap-queue.json`, or start Phase 4.
- Python remains >=3.11 and no new package dependency is introduced.
- Account currency is USD.
- Default risk/trade is 0.25% current realized risk equity; hard maximum requested risk/trade is 0.50%; simultaneous open risk is 1.00%; daily realized-loss halt is 1.50% of UTC day-start realized risk equity.
- Decisions cannot execute on their decision bar; the declared earliest executable timestamp must equal the first supplied bar for that symbol strictly after the decision timestamp.
- LONG enters on ASK and exits on BID; SHORT enters on BID and exits on ASK.
- Stop wins when stop and target are both reachable in one bar and ordering is unknowable.
- Spread is represented by executable bid/ask references and is never added again as a synthetic spread charge.
- Slippage is modeled only by degrading execution prices; its USD cost is measured as the difference between reference-price PnL and slipped-price PnL, never deducted twice.
- All explicit slippage is adverse to the trader.
- Same-timestamp processing is deterministic: existing-position exits first, then new decisions ordered by stable `decision_id`.
- End-of-data positions close on the final bar's executable CLOSE side: BID close for LONG, ASK close for SHORT.
- Repeated equivalent runs must produce byte-identical deterministic artifacts and identical SHA-256 digests.

---

## File Map

### New production files

- `src/fmp/contracts.py` — stable enums/dataclasses and bar/decision invariant validation.
- `src/fmp/risk/__init__.py` — public risk exports.
- `src/fmp/risk/sizing.py` — USD PnL/loss-per-unit and integer-unit sizing for supported pairs.
- `src/fmp/risk/policy.py` — risk configuration, UTC day state, reservation/release, approval/rejection.
- `src/fmp/backtest/__init__.py` — public backtest exports and `BACKTEST_ENGINE_VERSION`.
- `src/fmp/backtest/costs.py` — pip conventions, adverse slippage, commission, financing configuration.
- `src/fmp/backtest/execution.py` — entry fills, executable-side stop/target handling, gap/ambiguity/EOD semantics.
- `src/fmp/reporting/__init__.py` — public reporting exports.
- `src/fmp/reporting/backtest.py` — deterministic metrics and artifact serialization.
- `src/fmp/backtest/engine.py` — chronological deterministic state machine over bars and scripted decisions.

### New tests

- `tests/test_phase3_contracts.py`
- `tests/test_phase3_costs.py`
- `tests/test_phase3_risk.py`
- `tests/test_phase3_execution.py`
- `tests/test_phase3_reporting.py`
- `tests/test_phase3_engine.py`
- `tests/test_phase3_acceptance.py`

### Documentation modified after behavior is proven

- `docs/project-state.md`
- `docs/decision-log.md`
- `docs/phase3-acceptance-evidence.md` only after merged-main acceptance artifacts are independently inspected.

---

## Task 1: Freeze contracts and input invariants

**Files:**
- Create: `src/fmp/contracts.py`
- Test: `tests/test_phase3_contracts.py`

**Interfaces:**
- Produces enums: `Direction`, `OrderSide`, `ExitReason`, `RejectionCode`.
- Produces dataclasses: `QuoteBar`, `Decision`, `RiskAssessment`, `OrderIntent`, `Position`, `TradeRecord`, `RejectionRecord`, `EquityCheckpoint`, `BacktestRun`.
- Produces `validate_quote_bars(bars: Sequence[QuoteBar]) -> None` and `validate_decisions(decisions: Sequence[Decision]) -> None`.
- Later tasks consume these exact names.

- [ ] **Step 1: Write the failing contract tests**

Create `tests/test_phase3_contracts.py` using `unittest`. Freeze enum values and dataclass invariants. Include UTC-awareness, supported symbols, finite positive prices, side OHLC consistency, ask-not-below-bid for each OHLC field, no duplicate `(symbol, timestamp)` bar identity, global bar input sorted by `(timestamp_utc, symbol)`, and unique non-empty `decision_id` values.

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
                bid_open=1.1000,
                bid_high=1.1010,
                bid_low=1.0990,
                bid_close=1.1005,
                ask_open=1.1002,
                ask_high=1.1012,
                ask_low=1.0992,
                ask_close=1.1007,
            )
```

Also assert `Decision.earliest_executable_timestamp_utc > decision_timestamp_utc` whenever direction is LONG/SHORT. `NO_TRADE` still requires a stable `decision_id` but may omit stop/target/risk fields.

- [ ] **Step 2: Run the focused test and confirm RED**

```bash
python -m unittest tests.test_phase3_contracts -v
```

Expected: import/module failure because `fmp.contracts` does not exist.

- [ ] **Step 3: Implement the contract layer**

Use `@dataclass(frozen=True, slots=True)` and `str, Enum`.

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

Minimum frozen fields:

```text
QuoteBar:
  timestamp_utc, symbol,
  bid_open/high/low/close,
  ask_open/high/low/close

Decision:
  decision_id, symbol, decision_timestamp_utc, direction,
  earliest_executable_timestamp_utc | None,
  requested_risk_fraction | None,
  stop_price | None, target_price | None,
  reason_code | None, reason_text | None

RiskAssessment:
  approved, approved_risk_usd, approved_units,
  rejection_code | None, explanation

OrderIntent:
  decision_id, symbol, direction, units,
  reserved_risk_usd, stop_price, target_price,
  decision_timestamp_utc, earliest_executable_timestamp_utc

Position:
  position_id, decision_id, symbol, direction, units,
  entry_timestamp_utc,
  entry_reference_price, entry_price,
  entry_slippage_cost_usd, entry_commission_usd,
  stop_price, target_price, reserved_risk_usd

TradeRecord:
  trade_id, decision_id, symbol, direction, units,
  entry_timestamp_utc, exit_timestamp_utc,
  entry_reference_price, exit_reference_price,
  entry_price, exit_price,
  stop_price, target_price,
  exit_reason, intrabar_ambiguous,
  gross_pnl_usd, slippage_cost_usd,
  commission_cost_usd, financing_cost_usd,
  net_pnl_usd,
  risk_equity_before_usd, risk_equity_after_usd

RejectionRecord:
  decision_id, symbol, decision_timestamp_utc,
  evaluated_timestamp_utc, code, explanation

EquityCheckpoint:
  timestamp_utc, realized_risk_equity_usd

BacktestRun:
  run_identity: Mapping[str, object]
  trades: tuple[TradeRecord, ...]
  rejections: tuple[RejectionRecord, ...]
  equity_checkpoints: tuple[EquityCheckpoint, ...]
  metrics: Mapping[str, object]
```

`gross_pnl_usd` means PnL from executable BID/ASK **reference prices before configured slippage**. `slippage_cost_usd` is the non-negative degradation from reference-price PnL to slipped execution-price PnL. Therefore:

```text
net_pnl_usd = gross_pnl_usd
              - slippage_cost_usd
              - commission_cost_usd
              - financing_cost_usd
```

Validate invariant facts in dataclass `__post_init__`; risk caps and execution policy belong in later modules.

- [ ] **Step 4: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_contracts -v
```

- [ ] **Step 5: Commit**

```bash
git add src/fmp/contracts.py tests/test_phase3_contracts.py
git commit -m "[phase1-no-source] Freeze Phase 3 trading contracts"
```

---

## Task 2: Implement pip, PnL, and explicit cost primitives

**Files:**
- Create: `src/fmp/backtest/__init__.py`
- Create: `src/fmp/backtest/costs.py`
- Test: `tests/test_phase3_costs.py`

**Interfaces:**
- Produces `BACKTEST_ENGINE_VERSION = "fmp-backtest-v1"`.
- Produces `pip_size(symbol: str) -> float`.
- Produces `apply_adverse_slippage(price: float, *, side: OrderSide, pips: float, symbol: str) -> float`.
- Produces protocol-like classes `CommissionModel` and `FinancingModel`, each with `to_config() -> Mapping[str, object]` for deterministic run identity.
- Produces `ZeroCommission`, `FixedCommissionPerMillion`, `ZeroFinancing`.

- [ ] **Step 1: Write failing pip/slippage tests**

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

Assert unsupported symbols, non-finite prices, and negative slippage pips fail closed.

- [ ] **Step 2: Write failing commission/financing tests**

Freeze one-side commission semantics:

```python
model = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
self.assertAlmostEqual(model.cost_usd(units=100_000), 3.0)
self.assertEqual(ZeroCommission().cost_usd(units=100_000), 0.0)
self.assertEqual(ZeroFinancing().cost_usd(...), 0.0)
```

`to_config()` must return deterministic JSON-serializable mappings, e.g. `{"model": "zero_commission"}` and `{"model": "fixed_per_million_per_side", "usd_per_million_per_side": 30.0}`.

- [ ] **Step 3: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_costs -v
```

- [ ] **Step 4: Implement the cost primitives**

```python
PIP_SIZES = {
    "EURUSD": 0.0001,
    "GBPUSD": 0.0001,
    "USDJPY": 0.01,
}

def apply_adverse_slippage(price, *, side, pips, symbol):
    delta = pips * pip_size(symbol)
    return price + delta if side is OrderSide.BUY else price - delta
```

Financing receives symbol, direction, units, entry timestamp, and exit timestamp and returns a non-negative USD cost. Phase 3 only implements `ZeroFinancing`; venue-specific rollover tables are out of scope.

- [ ] **Step 5: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_costs -v
```

- [ ] **Step 6: Commit**

```bash
git add src/fmp/backtest/__init__.py src/fmp/backtest/costs.py tests/test_phase3_costs.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 cost models"
```

---

## Task 3: Implement USD PnL/risk sizing and risk-policy state

**Files:**
- Create: `src/fmp/risk/__init__.py`
- Create: `src/fmp/risk/sizing.py`
- Create: `src/fmp/risk/policy.py`
- Test: `tests/test_phase3_risk.py`

**Interfaces:**
- Produces `pnl_usd(*, symbol: str, direction: Direction, units: int, entry_price: float, exit_price: float) -> float`.
- Produces `loss_usd_per_unit(symbol: str, entry_price: float, stop_price: float) -> float`.
- Produces `size_units(*, symbol: str, entry_price: float, stop_price: float, allowed_risk_usd: float) -> int`.
- Produces frozen `RiskConfig(default_risk_fraction=0.0025, max_risk_fraction=0.005, max_simultaneous_risk_fraction=0.01, daily_loss_halt_fraction=0.015)`.
- Produces mutable `RiskState` storing starting equity, realized risk equity, UTC day-start basis/day realized PnL, halt state/time, and reserved USD risk keyed by `position_id`.
- Produces `assess_decision(...) -> RiskAssessment`, `reserve_risk(...)`, `release_risk(...)`, `record_realized_pnl(...)`, `roll_utc_day(...)`.

- [ ] **Step 1: Write failing PnL/sizing tests**

Freeze conversion rules:

```python
# USD-quoted pair PnL
self.assertAlmostEqual(
    pnl_usd(
        symbol="EURUSD", direction=Direction.LONG,
        units=10_000, entry_price=1.1000, exit_price=1.1010,
    ),
    10.0,
)

# USDJPY quote PnL is JPY and converts to USD at executable exit price.
expected = (150.10 - 150.00) * 10_000 / 150.10
self.assertAlmostEqual(
    pnl_usd(
        symbol="USDJPY", direction=Direction.LONG,
        units=10_000, entry_price=150.00, exit_price=150.10,
    ),
    expected,
)

# EURUSD: $25 allowed risk, 10-pip stop -> 25,000 units.
self.assertEqual(size_units(
    symbol="EURUSD", entry_price=1.1000, stop_price=1.0990,
    allowed_risk_usd=25.0,
), 25_000)

# USDJPY frozen sizing conversion denominator is stop price.
expected_units = math.floor(25.0 / (abs(150.00 - 149.90) / 149.90))
self.assertEqual(size_units(
    symbol="USDJPY", entry_price=150.00, stop_price=149.90,
    allowed_risk_usd=25.0,
), expected_units)
```

Also test SHORT PnL, invalid/non-positive stop distance, unsupported symbol, non-positive risk, and non-finite inputs.

- [ ] **Step 2: Write failing risk-policy boundary tests**

Cover exact boundaries:

```text
$10,000 realized risk equity:
- default 0.25% => $25 approved risk
- exactly 0.50% requested => allowed
- >0.50% requested => PER_TRADE_RISK
- $75 reserved + new $25 => exactly 1.00%, allowed
- $75.01 reserved + new $25 => SIMULTANEOUS_RISK
```

Also assert:

- release removes exact reserved amount;
- risk equity changes only by realized **net** PnL;
- UTC day-start basis snapshots realized risk equity before that day's realized PnL;
- daily halt activates when day realized PnL <= `-0.015 * day_start_basis`;
- a new UTC date clears halt and snapshots current realized risk equity;
- existing positions are not force-closed by `RiskState`.

- [ ] **Step 3: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_risk -v
```

- [ ] **Step 4: Implement PnL and sizing**

```python
def pnl_usd(*, symbol, direction, units, entry_price, exit_price):
    signed_quote_pnl = (
        (exit_price - entry_price) * units
        if direction is Direction.LONG
        else (entry_price - exit_price) * units
    )
    if symbol in {"EURUSD", "GBPUSD"}:
        return signed_quote_pnl
    if symbol == "USDJPY":
        return signed_quote_pnl / exit_price
    raise ValueError(...)
```

Sizing uses absolute stop loss per unit. USDJPY sizing uses the frozen stop-price denominator from the design.

- [ ] **Step 5: Implement risk policy/state**

`assess_decision` receives the directional decision, a **reference executable entry price before slippage**, current timestamp, `RiskConfig`, and `RiskState`. It validates direction-specific stop geometry, applies requested/default risk fraction, enforces hard cap and simultaneous reserved-risk cap, sizes integer units, and returns `INVALID_SIZE` for normal sizing failures instead of raising.

Risk reservation stores the approved **USD amount** and releases the exact same amount on close; it is not recomputed from changed equity later.

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

## Task 4: Implement executable-side entry/exit semantics

**Files:**
- Create: `src/fmp/backtest/execution.py`
- Test: `tests/test_phase3_execution.py`

**Interfaces:**
- Consumes Task 1 contracts, Task 2 costs, Task 3 `pnl_usd`.
- Produces frozen `ExitFill` in `execution.py`:

```text
ExitFill:
  timestamp_utc,
  reference_price,
  execution_price,
  reason,
  intrabar_ambiguous,
  exit_slippage_cost_usd,
  exit_commission_usd,
  financing_cost_usd
```

- Produces `entry_reference_price(bar: QuoteBar, direction: Direction) -> float`.
- Produces `fill_entry(intent: OrderIntent, bar: QuoteBar, *, slippage_pips: float, commission_model: CommissionModel) -> Position`.
- Produces `evaluate_exit(position: Position, bar: QuoteBar, *, slippage_pips: float, commission_model: CommissionModel, financing_model: FinancingModel) -> ExitFill | None`.
- Produces `close_end_of_data(position: Position, bar: QuoteBar, ...) -> ExitFill`.

- [ ] **Step 1: Write failing entry-side tests**

Assert LONG reference entry is `ask_open`, SHORT reference entry is `bid_open`, then BUY-up/SELL-down slippage is applied exactly once. Assert returned `Position` stores reference price, slipped price, entry commission, and entry slippage cost.

The entry slippage USD cost is:

```python
entry_slippage_cost = max(
    0.0,
    pnl_usd(
        symbol=symbol,
        direction=direction,
        units=units,
        entry_price=reference_entry,
        exit_price=synthetic_reference_exit,
    )
    - pnl_usd(
        symbol=symbol,
        direction=direction,
        units=units,
        entry_price=slipped_entry,
        exit_price=synthetic_reference_exit,
    ),
)
```

Implementation may use an algebraically equivalent direct formula, but tests compare exact economic effect. For USDJPY, conversion uses the same deterministic price basis as `pnl_usd`.

- [ ] **Step 2: Write failing stop/target/gap tests**

Hand-build bars to cover:

- LONG stop uses BID low and SELL execution.
- SHORT stop uses ASK high and BUY execution.
- LONG target uses BID high.
- SHORT target uses ASK low.
- both thresholds reachable => `STOP`, `intrabar_ambiguous=True`.
- LONG executable BID open below stop => reference exit is worse `bid_open`.
- SHORT executable ASK open above stop => reference exit is worse `ask_open`.
- favorable target gap => reference exit stays declared target, never improved open.
- END_OF_DATA LONG reference exit is final `bid_close`; SHORT uses final `ask_close`.

- [ ] **Step 3: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_execution -v
```

- [ ] **Step 4: Implement entry semantics**

```python
entry_side = (
    OrderSide.BUY if intent.direction is Direction.LONG else OrderSide.SELL
)
reference = bar.ask_open if intent.direction is Direction.LONG else bar.bid_open
execution = apply_adverse_slippage(
    reference,
    side=entry_side,
    pips=slippage_pips,
    symbol=intent.symbol,
)
```

`Position.position_id` is deterministically derived from `decision_id` (e.g. exactly `decision_id`) because Phase 3 permits at most one filled position per decision.

- [ ] **Step 5: Implement exit semantics**

Use BID OHLC for LONG exit reachability and ASK OHLC for SHORT. Evaluate in this order:

```text
1. adverse stop gap at executable side open
2. stop reachable? target reachable?
3. if both: stop, ambiguous=True
4. stop only: stop
5. target only: declared target
6. neither: remain open
```

Apply adverse exit slippage to the selected reference price. `exit_slippage_cost_usd` is the incremental PnL degradation caused by exit slippage, not a second deduction from already-slipped PnL.

- [ ] **Step 6: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_execution -v
```

- [ ] **Step 7: Commit**

```bash
git add src/fmp/backtest/execution.py tests/test_phase3_execution.py
git commit -m "[phase1-no-source] Add conservative Phase 3 execution semantics"
```

---

## Task 5: Implement deterministic reporting before orchestration

**Files:**
- Create: `src/fmp/reporting/__init__.py`
- Create: `src/fmp/reporting/backtest.py`
- Test: `tests/test_phase3_reporting.py`

**Interfaces:**
- Produces `compute_backtest_metrics(*, starting_equity_usd: float, trades: Sequence[TradeRecord], equity_checkpoints: Sequence[EquityCheckpoint]) -> dict[str, object]`.
- Produces `write_backtest_artifacts(run: BacktestRun, out_dir: Path) -> dict[str, object]`.
- Manifest protocol: `fmp-phase3-backtest-artifacts-v1`.

- [ ] **Step 1: Write failing metric tests**

Use four hand-built trades with net PnLs `[100.0, -50.0, 25.0, -25.0]` from `$10,000` starting equity and assert:

```text
net_pnl_usd = 50.0
net_return = 0.005
trade_count = 4
win_rate = 0.5
average_win_usd = 62.5
average_loss_usd = -37.5
expectancy_usd = 12.5
gross_profit_usd = 125.0
gross_loss_usd = 75.0
profit_factor = 125 / 75
longest_winning_streak = 1
longest_losing_streak = 1
```

Provide realized-equity checkpoints and assert maximum drawdown in USD/fraction from the previous realized-equity peak. `recovery_factor = net_pnl_usd / max_drawdown_usd` only when drawdown >0; otherwise `None`.

Also sum stored slippage, commission, and financing components independently.

- [ ] **Step 2: Write failing zero-trade behavior tests**

Freeze:

```text
net_pnl_usd = 0.0
net_return = 0.0
trade_count = 0
expectancy_usd = None
win_rate = None
average_win_usd = None
average_loss_usd = None
profit_factor = None
recovery_factor = None
```

- [ ] **Step 3: Write failing deterministic artifact tests**

Write one `BacktestRun` to two temp directories. Assert identical relative filenames and bytes for:

```text
summary.json
trades.jsonl
rejections.jsonl
metrics.json
manifest.json
```

Manifest records byte size and SHA-256 for the first four artifacts and does not recursively hash itself.

- [ ] **Step 4: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_reporting -v
```

- [ ] **Step 5: Implement metrics**

Compute only from deterministic stored trade/equity state. Do not infer mark-to-market equity from market bars in this first Phase 3 kernel; acceptance drawdown is realized-equity drawdown exactly as frozen in the design.

- [ ] **Step 6: Implement stable serialization**

Mirror Phase 2 atomic-write discipline without importing Phase 2 private helpers:

```text
UTF-8
sorted JSON keys
indent=2 for JSON files
allow_nan=False
terminal newline
ISO UTC timestamps with Z
JSONL records sorted by stable timestamp/id
no wall-clock generated_at field in hashed payloads
atomic temp-file + os.replace
```

- [ ] **Step 7: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_reporting -v
```

- [ ] **Step 8: Commit**

```bash
git add src/fmp/reporting tests/test_phase3_reporting.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 reporting"
```

---

## Task 6: Implement the chronological backtest state machine

**Files:**
- Create: `src/fmp/backtest/engine.py`
- Test: `tests/test_phase3_engine.py`

**Interfaces:**
- Produces frozen `BacktestConfig`:

```text
starting_equity_usd
slippage_pips
risk_config
commission_model
financing_model
processed_data_manifest_id
schema_version
timeframe
requested_start_utc
requested_end_utc
code_commit
decision_config: Mapping[str, object]
```

- Produces `run_backtest(*, bars: Sequence[QuoteBar], decisions: Sequence[Decision], config: BacktestConfig) -> BacktestRun`.
- Consumes Tasks 1-5.

- [ ] **Step 1: Write failing timing-contract tests**

Bars for a symbol occur at `00:00`, `00:01`, `00:02`. A directional decision stamped `00:00` must declare earliest execution `00:01`; the engine verifies that `00:01` is the first supplied bar strictly after the decision timestamp. If the decision declares `00:02`, record `TIMING_CONTRACT`; do not silently delay it. A decision can never fill on `00:00`.

- [ ] **Step 2: Write failing event-order tests**

At one timestamp, create an existing position whose target exits and a new decision whose risk is affordable only after reserved risk is released. Assert exit happens first and the new decision is approved.

Create simultaneous decisions `decision_id="A"` and `"B"` whose combined risk exceeds the cap. Assert stable `decision_id` ordering makes A fill and B reject every run.

- [ ] **Step 3: Write failing NO_TRADE/rejection tests**

Assert `NO_TRADE` produces a preserved `RejectionRecord` with code `NO_TRADE`, never a position. Exercise invalid stop/target geometry, daily halt, simultaneous-risk cap, and invalid size with their stable codes.

- [ ] **Step 4: Write failing realized-equity/daily-halt tests**

Construct hand-calculable trades that cross the 1.50% UTC-day realized loss threshold. Assert:

- subsequent same-day entries reject `DAILY_HALT`;
- any already-open positions are left intact solely by the halt;
- next UTC date resets halt;
- new day-start basis equals current realized risk equity before new-day PnL.

- [ ] **Step 5: Write failing same-bar post-entry tests**

A position filled at the bar open is immediately eligible for stop/target checks using that same bar's subsequent high/low range. If both are reachable, stop wins and `intrabar_ambiguous=True`. This does not permit execution before bar open.

- [ ] **Step 6: Write failing end-of-data test**

Leave a position open at the final bar and assert `END_OF_DATA` closes LONG at slipped `bid_close` and SHORT at slipped `ask_close`, with reference/actual/cost fields consistent.

- [ ] **Step 7: Run focused tests RED**

```bash
python -m unittest tests.test_phase3_engine -v
```

- [ ] **Step 8: Implement engine validation/indexing**

Validate bar/decision sequences first. For each directional decision, find the first supplied bar for that symbol strictly after `decision_timestamp_utc`; require its timestamp to equal `earliest_executable_timestamp_utc`, otherwise preserve a `TIMING_CONTRACT` rejection.

Index valid decisions by `(earliest_executable_timestamp_utc, symbol)` and sort each bucket by `decision_id`.

- [ ] **Step 9: Implement chronological event loop**

```text
for each global bar timestamp in ascending order:
  roll UTC risk day
  for positions whose symbol has a bar at this timestamp, in position_id order:
    evaluate exit first
    when closed:
      gross = pnl_usd(reference entry, reference exit)
      slipped_execution_pnl = pnl_usd(slipped entry, slipped exit)
      slippage_cost = max(0, gross - slipped_execution_pnl)
      commission = entry_commission + exit_commission
      financing = exit_fill.financing
      net = gross - slippage_cost - commission - financing
      release exact reserved risk
      record realized net PnL immediately
      append TradeRecord + EquityCheckpoint
  for valid decisions scheduled now, in decision_id order:
    preserve NO_TRADE without risk assessment
    compute executable reference entry
    assess risk
    on reject: append RejectionRecord
    on approve: create OrderIntent, fill entry, reserve approved USD risk
    then evaluate same-bar post-entry stop/target immediately
```

After the final timestamp, close all remaining positions in stable `position_id` order using final bars and `END_OF_DATA` semantics; release/realize each result.

- [ ] **Step 10: Build deterministic run identity and metrics**

Run identity includes exactly:

```text
backtest_engine_version
code_commit
processed_data_manifest_id
schema_version
timeframe
requested_start_utc
requested_end_utc
starting_equity_usd
slippage_pips
risk_config values
commission_model.to_config()
financing_model.to_config()
decision_config
```

No current clock time, host name, random UUID, or process-specific metadata is included. Call Task 5 `compute_backtest_metrics` before returning `BacktestRun`.

- [ ] **Step 11: Run focused tests GREEN**

```bash
python -m unittest tests.test_phase3_engine -v
```

- [ ] **Step 12: Commit**

```bash
git add src/fmp/backtest/engine.py tests/test_phase3_engine.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 backtest engine"
```

---

## Task 7: Prove end-to-end golden scenarios and repeated-run equality

**Files:**
- Create: `tests/test_phase3_acceptance.py`
- Modify only when a golden failure proves a production defect: Phase 3 production files from Tasks 1-6.

**Interfaces:**
- Uses public `run_backtest` and `write_backtest_artifacts`.
- No strategy module is introduced; decisions are scripted fixtures.

- [ ] **Step 1: Add LONG executable-side golden scenario**

Use zero slippage/commission. A LONG decision becomes executable on the next bar at ASK. Close at BID via target or EOD and assert exact entry/exit references, units, gross/net PnL, timestamps, and risk equity.

- [ ] **Step 2: Add SHORT executable-side golden scenario**

Use SHORT BID entry and ASK exit with exact hand-calculated USD PnL.

- [ ] **Step 3: Add stop/target ambiguity and gap golden scenarios**

Prove:

```text
both reachable in one bar -> STOP + ambiguous=true
gap through stop -> worse executable open reference
favorable gap through target -> declared target reference, no price improvement
```

- [ ] **Step 4: Add JPY/non-JPY sizing golden scenarios**

Assert Task 3 sizing through the complete engine, including USDJPY PnL conversion at executable exit price.

- [ ] **Step 5: Add cost golden scenario**

Use 1 pip slippage and fixed commission. Hand-calculate:

```text
gross reference-price PnL
slippage degradation
entry + exit commission
financing = 0
net = gross - slippage - commission
```

Assert the engine does not subtract slippage twice.

- [ ] **Step 6: Add risk-control golden scenarios**

Prove per-trade cap rejection, simultaneous-risk rejection, exit-before-entry risk release, daily halt, and next-day reset through the public engine.

- [ ] **Step 7: Add deterministic repeated-run/artifact equality**

Run the identical fixture/config twice. Assert equality of `BacktestRun` semantic content and byte-identical `summary.json`, `trades.jsonl`, `rejections.jsonl`, `metrics.json`, `manifest.json`.

- [ ] **Step 8: Run acceptance tests; fix production defects only**

```bash
python -m unittest tests.test_phase3_acceptance -v
```

Do not weaken a hand-calculated golden expectation merely to match implementation output. If a test exposes an implementation defect, patch the smallest responsible production unit and rerun its focused test plus acceptance test.

- [ ] **Step 9: Commit**

```bash
git add tests/test_phase3_acceptance.py src/fmp/contracts.py src/fmp/risk src/fmp/backtest src/fmp/reporting
git commit -m "[phase1-no-source] Prove Phase 3 golden scenarios"
```

---

## Task 8: Record active Phase 3 semantics in source-of-truth docs

**Files:**
- Modify: `docs/project-state.md`
- Modify: `docs/decision-log.md`

**Interfaces:**
- Adds `DEC-016 — Phase 3 backtester semantics`.
- Records Phase 3 as ACTIVE, not PASS.

- [ ] **Step 1: Add DEC-016**

Record without changing approved hard limits:

```text
- daily realized-loss basis = UTC day-start realized risk equity
- reaching -1.50% blocks new entries for the remainder of that UTC date
- existing positions are not force-closed solely by the daily halt
- exits process before entries at equal timestamps
- stable decision_id orders simultaneous new decisions
- LONG ASK entry/BID exit; SHORT BID entry/ASK exit
- stop wins unresolved stop/target ambiguity
- target gaps receive no favorable price improvement
- EOD uses final executable close side
- no real-money permission changes
```

- [ ] **Step 2: Update project state**

Set exactly:

```text
Current phase: Phase 3 — Backtesting Engine
Phase status: ACTIVE
Next milestone: verify the deterministic Phase 3 golden acceptance suite and inspect acceptance artifacts
```

Preserve all Phase 2 PASS/checkpoint evidence and state explicitly that Phase 4 has not started.

- [ ] **Step 3: Commit**

```bash
git add docs/project-state.md docs/decision-log.md
git commit -m "[phase1-no-source] Record Phase 3 backtester semantics"
```

---

## Task 9: Full regression verification and safe merge

**Files:**
- No intended new files unless verification proves a defect.

**Interfaces:**
- Proves the implementation is mergeable; does **not** by itself make Phase 3 PASS.

- [ ] **Step 1: Run all focused Phase 3 tests**

```bash
python -m unittest \
  tests.test_phase3_contracts \
  tests.test_phase3_costs \
  tests.test_phase3_risk \
  tests.test_phase3_execution \
  tests.test_phase3_reporting \
  tests.test_phase3_engine \
  tests.test_phase3_acceptance -v
```

Expected: zero failures/errors.

- [ ] **Step 2: Run full regression suite**

```bash
python -m unittest discover -s tests -v
```

Expected: zero failures/errors.

- [ ] **Step 3: Compile source/tests**

```bash
python -m compileall -q src tests
```

Expected exit code 0.

- [ ] **Step 4: Inspect exact branch diff**

Verify all are true:

```text
only Phase 3 source/tests/docs/spec/plan files changed
docs/phase1-exact-gap-queue.json absent
no source-capable Phase 1 workflow modified
no Supabase/raw/cloud mutation path added
no strategy/Phase 4 implementation added
no dependency added
```

- [ ] **Step 5: Open PR with marker present from creation**

Title exactly:

```text
[phase1-no-source] Phase 3 deterministic backtesting engine
```

Body states Phase 3 remains ACTIVE pending post-merge acceptance artifact inspection/checkpoint review.

- [ ] **Step 6: Require fresh green PR CI on exact immutable head**

Confirm `tests` succeeds and Phase 1 source-capable PR workflows skip. Merge only the exact verified head with squash title/message containing `[phase1-no-source]`.

- [ ] **Step 7: Verify post-merge main safety**

Confirm:

```text
main points to squash merge
tests push workflow succeeds
no Phase 1 acquisition-capable workflow triggers on the merge push
```

---

## Task 10: Produce, inspect, and close Phase 3 only after real acceptance evidence

**Files:**
- Create after evidence exists: `docs/phase3-acceptance-evidence.md`
- Modify after evidence exists: `docs/project-state.md`
- Modify after evidence exists: `docs/decision-log.md`

**Interfaces:**
- Closure checkpoint: `fmp-v1-phase3-backtester`.
- This task starts only from the merged engine on verified `main`.

- [ ] **Step 1: Run a deterministic merged-main acceptance fixture**

Run a small hand-calculable scripted fixture that exercises at minimum LONG, SHORT, nonzero slippage/commission, one stop/target ambiguity, one simultaneous-risk rejection, one daily halt, and one next-day reset. Persist with `write_backtest_artifacts`.

- [ ] **Step 2: Independently inspect persisted artifacts**

Verify:

```text
summary identity fields
trade records and exact PnL math
rejection codes/explanations
realized-equity checkpoints
metrics math
manifest SHA-256/size against actual files
repeated-run byte/digest equality
```

- [ ] **Step 3: Review every Phase 3 acceptance-gate line**

Compare evidence against `docs/build-order.md` and `docs/superpowers/specs/2026-09-14-phase3-backtester-design.md`. Any unmet criterion keeps Phase 3 ACTIVE.

- [ ] **Step 4: Record acceptance evidence only if all gates pass**

Create `docs/phase3-acceptance-evidence.md` with immutable code/data/config identities, exact test/run identities, artifact hashes, hand-calculated checks, and zero unresolved acceptance failures.

- [ ] **Step 5: Create checkpoint and formal PASS in a separate closure change**

Only after evidence review passes:

```text
create checkpoint fmp-v1-phase3-backtester
update project-state to Phase 3 PASS
record acceptance decision in decision-log
keep Phase 4 explicitly unstarted
```
