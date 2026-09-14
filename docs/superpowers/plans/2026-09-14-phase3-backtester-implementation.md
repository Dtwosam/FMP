# Phase 3 Backtesting Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic event-driven Phase 3 backtesting engine with realistic bid/ask execution, explicit costs, conservative stop/target handling, independent risk controls, auditable rejection records, and deterministic reporting artifacts.

**Architecture:** Polars remains the market-data/storage layer, while trading state is processed chronologically through explicit broker-independent records. Contracts, costs, risk, execution, reporting, and orchestration stay separate so later shadow/demo modes can reuse decision/risk/order semantics without importing historical-data internals.

**Tech Stack:** Python >=3.11, standard library dataclasses/enums/hashlib/json/math/pathlib/tempfile/os, Polars 1.44.2, unittest.

**Spec:** `docs/superpowers/specs/2026-09-14-phase3-backtester-design.md`

## Global Constraints

- V1 instruments are exactly `EURUSD`, `GBPUSD`, `USDJPY`.
- Phase 2 checkpoint remains `fmp-v1-phase2-normalized-data`; raw data is immutable.
- Every Phase 3 commit and PR title includes `[phase1-no-source]`.
- Do not invoke source acquisition, mutate `fmp-raw`, modify `docs/phase1-exact-gap-queue.json`, or start Phase 4.
- Python remains >=3.11; add no dependency.
- Account currency is USD.
- Default risk/trade 0.25%; hard max requested risk/trade 0.50%; simultaneous open risk 1.00%; daily realized-loss halt 1.50% of UTC day-start realized risk equity.
- Earliest executable timestamp must equal the first supplied bar for that symbol strictly after the decision timestamp.
- LONG: ASK entry, BID exit. SHORT: BID entry, ASK exit.
- Stop wins unresolved same-bar stop/target ambiguity.
- Spread is represented by executable bid/ask references and is never charged again synthetically.
- Slippage only degrades execution prices. Total slippage USD cost is computed once at trade close as `reference-price PnL - slipped-price PnL`, floored at zero.
- Same-timestamp order: existing-position exits first; then new decisions by stable `decision_id`.
- End-of-data uses final executable CLOSE side: BID close for LONG, ASK close for SHORT.
- Equivalent runs must produce byte-identical deterministic artifacts and SHA-256 digests.

---

## File Map

**Create production files**

- `src/fmp/contracts.py` — enums/dataclasses and invariant validation.
- `src/fmp/risk/__init__.py` — public risk exports.
- `src/fmp/risk/sizing.py` — USD PnL, stop-loss-per-unit, integer sizing.
- `src/fmp/risk/policy.py` — risk config/state, UTC daily halt, reserve/release, assessment.
- `src/fmp/backtest/__init__.py` — public exports and version.
- `src/fmp/backtest/costs.py` — pip/slippage, commission, financing.
- `src/fmp/backtest/execution.py` — entry/exit/gap/ambiguity/EOD semantics.
- `src/fmp/reporting/__init__.py` — public reporting exports.
- `src/fmp/reporting/backtest.py` — metrics and stable artifacts.
- `src/fmp/backtest/engine.py` — chronological event loop.

**Create tests**

- `tests/test_phase3_contracts.py`
- `tests/test_phase3_costs.py`
- `tests/test_phase3_risk.py`
- `tests/test_phase3_execution.py`
- `tests/test_phase3_reporting.py`
- `tests/test_phase3_engine.py`
- `tests/test_phase3_acceptance.py`

**Modify after behavior is proven**

- `docs/project-state.md`
- `docs/decision-log.md`
- `docs/phase3-acceptance-evidence.md` only after merged-main artifacts are independently inspected.

---

## Task 1: Freeze contracts and invariants

**Files:**
- Create: `src/fmp/contracts.py`
- Test: `tests/test_phase3_contracts.py`

**Interfaces:**
- Enums: `Direction`, `OrderSide`, `ExitReason`, `RejectionCode`.
- Dataclasses: `QuoteBar`, `Decision`, `RiskAssessment`, `OrderIntent`, `Position`, `TradeRecord`, `RejectionRecord`, `EquityCheckpoint`, `BacktestRun`.
- Functions: `validate_quote_bars(bars)`, `validate_decisions(decisions)`.

- [ ] **Step 1: Write failing contract tests**

Freeze stable values:

```python
self.assertEqual(Direction.LONG.value, "LONG")
self.assertEqual(Direction.SHORT.value, "SHORT")
self.assertEqual(Direction.NO_TRADE.value, "NO_TRADE")
self.assertEqual(RejectionCode.TIMING_CONTRACT.value, "TIMING_CONTRACT")
```

Test UTC timestamps, supported symbols, finite positive prices, `low <= open/close <= high`, ask not below bid for each OHLC field, no duplicate `(symbol, timestamp)` identities, bars globally sorted `(timestamp_utc, symbol)`, unique non-empty `decision_id`, and directional `earliest_executable_timestamp_utc > decision_timestamp_utc`.

Representative invalid timestamp test:

```python
with self.assertRaisesRegex(ValueError, "UTC"):
    QuoteBar(
        timestamp_utc=datetime(2026, 9, 14, 0, 0),
        symbol="EURUSD",
        bid_open=1.1000, bid_high=1.1010, bid_low=1.0990, bid_close=1.1005,
        ask_open=1.1002, ask_high=1.1012, ask_low=1.0992, ask_close=1.1007,
    )
```

- [ ] **Step 2: Run RED**

```bash
python -m unittest tests.test_phase3_contracts -v
```

Expected: missing `fmp.contracts`.

- [ ] **Step 3: Implement contracts**

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

Freeze fields:

```text
QuoteBar: timestamp_utc, symbol, bid_open/high/low/close, ask_open/high/low/close
Decision: decision_id, symbol, decision_timestamp_utc, direction,
          earliest_executable_timestamp_utc | None,
          requested_risk_fraction | None, stop_price | None, target_price | None,
          reason_code | None, reason_text | None
RiskAssessment: approved, approved_risk_usd, approved_units,
                rejection_code | None, explanation
OrderIntent: decision_id, symbol, direction, units, reserved_risk_usd,
             stop_price, target_price, decision_timestamp_utc,
             earliest_executable_timestamp_utc
Position: position_id, decision_id, symbol, direction, units,
          entry_timestamp_utc, entry_reference_price, entry_price,
          entry_commission_usd, stop_price, target_price, reserved_risk_usd
TradeRecord: trade_id, decision_id, symbol, direction, units,
             entry_timestamp_utc, exit_timestamp_utc,
             entry_reference_price, exit_reference_price,
             entry_price, exit_price, stop_price, target_price,
             exit_reason, intrabar_ambiguous,
             gross_pnl_usd, slippage_cost_usd,
             commission_cost_usd, financing_cost_usd, net_pnl_usd,
             risk_equity_before_usd, risk_equity_after_usd
RejectionRecord: decision_id, symbol, decision_timestamp_utc,
                 evaluated_timestamp_utc, code, explanation
EquityCheckpoint: timestamp_utc, realized_risk_equity_usd
BacktestRun: run_identity, trades, rejections, equity_checkpoints, metrics
```

`gross_pnl_usd` is PnL from executable BID/ASK **reference prices before configured slippage**. `slippage_cost_usd` is the non-negative degradation to slipped-price PnL. Therefore:

```text
net_pnl_usd = gross_pnl_usd - slippage_cost_usd
              - commission_cost_usd - financing_cost_usd
```

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest tests.test_phase3_contracts -v
```

- [ ] **Step 5: Commit**

```bash
git add src/fmp/contracts.py tests/test_phase3_contracts.py
git commit -m "[phase1-no-source] Freeze Phase 3 trading contracts"
```

---

## Task 2: Implement pip and cost primitives

**Files:**
- Create: `src/fmp/backtest/__init__.py`
- Create: `src/fmp/backtest/costs.py`
- Test: `tests/test_phase3_costs.py`

**Interfaces:**
- `BACKTEST_ENGINE_VERSION = "fmp-backtest-v1"`.
- `pip_size(symbol) -> float`.
- `apply_adverse_slippage(price, *, side, pips, symbol) -> float`.
- `CommissionModel.cost_usd(*, units)`, `CommissionModel.to_config()`.
- `FinancingModel.cost_usd(...)`, `FinancingModel.to_config()`.
- `ZeroCommission`, `FixedCommissionPerMillion`, `ZeroFinancing`.

- [ ] **Step 1: Write failing tests**

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
model = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
self.assertAlmostEqual(model.cost_usd(units=100_000), 3.0)
```

Also reject unsupported symbols, non-finite prices, negative pips/rates. Assert deterministic JSON-serializable `to_config()` mappings.

- [ ] **Step 2: Run RED**

```bash
python -m unittest tests.test_phase3_costs -v
```

- [ ] **Step 3: Implement**

```python
PIP_SIZES = {"EURUSD": 0.0001, "GBPUSD": 0.0001, "USDJPY": 0.01}

def apply_adverse_slippage(price, *, side, pips, symbol):
    delta = pips * pip_size(symbol)
    return price + delta if side is OrderSide.BUY else price - delta
```

`FixedCommissionPerMillion` charges `abs(units) / 1_000_000 * rate` **per execution side**. `ZeroFinancing` returns exactly `0.0`; venue-specific rollover is out of scope.

- [ ] **Step 4: Run GREEN**

```bash
python -m unittest tests.test_phase3_costs -v
```

- [ ] **Step 5: Commit**

```bash
git add src/fmp/backtest/__init__.py src/fmp/backtest/costs.py tests/test_phase3_costs.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 cost models"
```

---

## Task 3: Implement USD PnL, sizing, and risk state

**Files:**
- Create: `src/fmp/risk/__init__.py`
- Create: `src/fmp/risk/sizing.py`
- Create: `src/fmp/risk/policy.py`
- Test: `tests/test_phase3_risk.py`

**Interfaces:**
- `pnl_usd(*, symbol, direction, units, entry_price, exit_price) -> float`.
- `loss_usd_per_unit(symbol, entry_price, stop_price) -> float`.
- `size_units(*, symbol, entry_price, stop_price, allowed_risk_usd) -> int`.
- `RiskConfig(default_risk_fraction=0.0025, max_risk_fraction=0.005, max_simultaneous_risk_fraction=0.01, daily_loss_halt_fraction=0.015)`.
- `RiskState` with realized risk equity, UTC day state, halt state/time, and exact USD reservations keyed by position ID.
- `assess_decision`, `reserve_risk`, `release_risk`, `record_realized_pnl`, `roll_utc_day`.

- [ ] **Step 1: Write failing PnL/sizing tests**

```python
self.assertAlmostEqual(
    pnl_usd(
        symbol="EURUSD", direction=Direction.LONG,
        units=10_000, entry_price=1.1000, exit_price=1.1010,
    ),
    10.0,
)
expected_jpy = (150.10 - 150.00) * 10_000 / 150.10
self.assertAlmostEqual(
    pnl_usd(
        symbol="USDJPY", direction=Direction.LONG,
        units=10_000, entry_price=150.00, exit_price=150.10,
    ),
    expected_jpy,
)
self.assertEqual(size_units(
    symbol="EURUSD", entry_price=1.1000, stop_price=1.0990,
    allowed_risk_usd=25.0,
), 25_000)
expected_units = math.floor(25.0 / (abs(150.00 - 149.90) / 149.90))
self.assertEqual(size_units(
    symbol="USDJPY", entry_price=150.00, stop_price=149.90,
    allowed_risk_usd=25.0,
), expected_units)
```

Test SHORT PnL and invalid/non-finite/unsupported inputs.

- [ ] **Step 2: Write failing risk boundary tests**

For $10,000 realized risk equity:

```text
default 0.25% -> $25 approved
exactly 0.50% requested -> allowed
>0.50% -> PER_TRADE_RISK
$75 reserved + $25 -> exactly 1.00%, allowed
$75.01 reserved + $25 -> SIMULTANEOUS_RISK
```

Test exact release, risk equity changes only by realized net PnL, day-start snapshot before daily PnL, halt at `day_pnl <= -0.015 * day_start`, and next-UTC-day reset.

- [ ] **Step 3: Run RED**

```bash
python -m unittest tests.test_phase3_risk -v
```

- [ ] **Step 4: Implement PnL/sizing**

```python
def pnl_usd(*, symbol, direction, units, entry_price, exit_price):
    quote_pnl = (
        (exit_price - entry_price) * units
        if direction is Direction.LONG
        else (entry_price - exit_price) * units
    )
    if symbol in {"EURUSD", "GBPUSD"}:
        return quote_pnl
    if symbol == "USDJPY":
        return quote_pnl / exit_price
    raise ValueError(...)
```

USDJPY sizing uses the frozen stop-price conversion denominator:

```python
loss_usd_per_unit = abs(entry_price - stop_price) / stop_price
```

- [ ] **Step 5: Implement risk policy**

`assess_decision` receives a **reference executable entry price before slippage**, validates stop geometry, applies requested/default fraction, enforces hard/simultaneous caps, sizes integer units, and returns `INVALID_SIZE` for normal sizing rejection paths.

Reservations store the approved USD amount and release that exact amount on close; never recompute it from later equity.

- [ ] **Step 6: Run GREEN**

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
- Frozen `ExitFill(timestamp_utc, reference_price, execution_price, reason, intrabar_ambiguous, exit_commission_usd, financing_cost_usd)`.
- `entry_reference_price(bar, direction) -> float`.
- `fill_entry(intent, bar, *, slippage_pips, commission_model) -> Position`.
- `evaluate_exit(position, bar, *, slippage_pips, commission_model, financing_model) -> ExitFill | None`.
- `close_end_of_data(position, bar, ...) -> ExitFill`.

- [ ] **Step 1: Write failing entry tests**

Assert LONG reference entry = `ask_open`, SHORT = `bid_open`; BUY slippage raises price, SELL slippage lowers price; returned `Position` stores reference/slipped entry and entry commission.

- [ ] **Step 2: Write failing stop/target/gap tests**

Cover exactly:

```text
LONG stop uses BID low, SELL exit
SHORT stop uses ASK high, BUY exit
LONG target uses BID high
SHORT target uses ASK low
both reachable -> STOP + ambiguous=true
LONG BID open below stop -> reference exit = worse bid_open
SHORT ASK open above stop -> reference exit = worse ask_open
favorable target gap -> reference exit remains declared target
EOD LONG -> final bid_close
EOD SHORT -> final ask_close
```

- [ ] **Step 3: Run RED**

```bash
python -m unittest tests.test_phase3_execution -v
```

- [ ] **Step 4: Implement entry**

```python
side = OrderSide.BUY if intent.direction is Direction.LONG else OrderSide.SELL
reference = bar.ask_open if intent.direction is Direction.LONG else bar.bid_open
execution = apply_adverse_slippage(
    reference, side=side, pips=slippage_pips, symbol=intent.symbol
)
```

Set deterministic `position_id = decision_id` because Phase 3 permits one filled position per decision.

- [ ] **Step 5: Implement exit ordering**

```text
1. adverse stop gap at executable-side open
2. stop reachable? target reachable?
3. both -> stop, ambiguous=true
4. stop only -> stop
5. target only -> declared target
6. neither -> remain open
```

Apply adverse exit slippage exactly once. Do not compute or subtract slippage USD cost here; engine computes total trade slippage once from reference-vs-slipped PnL at close.

- [ ] **Step 6: Run GREEN**

```bash
python -m unittest tests.test_phase3_execution -v
```

- [ ] **Step 7: Commit**

```bash
git add src/fmp/backtest/execution.py tests/test_phase3_execution.py
git commit -m "[phase1-no-source] Add conservative Phase 3 execution semantics"
```

---

## Task 5: Implement deterministic reporting

**Files:**
- Create: `src/fmp/reporting/__init__.py`
- Create: `src/fmp/reporting/backtest.py`
- Test: `tests/test_phase3_reporting.py`

**Interfaces:**
- `compute_backtest_metrics(*, starting_equity_usd, trades, equity_checkpoints) -> dict[str, object]`.
- `write_backtest_artifacts(run, out_dir) -> dict[str, object]`.
- Manifest protocol `fmp-phase3-backtest-artifacts-v1`.

- [ ] **Step 1: Write failing metric tests**

For net trade PnLs `[100, -50, 25, -25]` and starting equity `$10,000`, assert:

```text
net_pnl_usd=50
net_return=0.005
trade_count=4
win_rate=0.5
average_win_usd=62.5
average_loss_usd=-37.5
expectancy_usd=12.5
gross_profit_usd=125
gross_loss_usd=75
profit_factor=125/75
longest_winning_streak=1
longest_losing_streak=1
```

Provide realized-equity checkpoints and hand-check max drawdown USD/fraction. `recovery_factor = net_pnl / max_drawdown_usd` only if drawdown >0, else `None`. Sum slippage, commission, financing separately.

- [ ] **Step 2: Freeze zero-trade metrics**

```text
net_pnl_usd=0.0
net_return=0.0
trade_count=0
expectancy_usd=None
win_rate=None
average_win_usd=None
average_loss_usd=None
profit_factor=None
recovery_factor=None
```

- [ ] **Step 3: Write failing artifact determinism test**

Same run written to two temp dirs must yield identical bytes for:

```text
summary.json
trades.jsonl
rejections.jsonl
metrics.json
manifest.json
```

Manifest hashes/sizes the first four artifacts, not itself.

- [ ] **Step 4: Run RED**

```bash
python -m unittest tests.test_phase3_reporting -v
```

- [ ] **Step 5: Implement metrics and stable writer**

Realized-equity drawdown only; no hidden mark-to-market rule. Serialization rules:

```text
UTF-8
sorted keys
allow_nan=False
terminal newline
UTC timestamps as ISO Z
JSONL ordered by stable timestamp/id
no wall-clock generated_at in hashed payloads
atomic temp file + os.replace
```

- [ ] **Step 6: Run GREEN**

```bash
python -m unittest tests.test_phase3_reporting -v
```

- [ ] **Step 7: Commit**

```bash
git add src/fmp/reporting tests/test_phase3_reporting.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 reporting"
```

---

## Task 6: Implement chronological engine

**Files:**
- Create: `src/fmp/backtest/engine.py`
- Test: `tests/test_phase3_engine.py`

**Interfaces:**
- Frozen `BacktestConfig(starting_equity_usd, slippage_pips, risk_config, commission_model, financing_model, processed_data_manifest_id, schema_version, timeframe, requested_start_utc, requested_end_utc, code_commit, decision_config)`.
- `run_backtest(*, bars, decisions, config) -> BacktestRun`.

- [ ] **Step 1: Write failing timing tests**

Bars at `00:00`, `00:01`, `00:02`. Decision timestamp `00:00` must declare earliest `00:01`. Declaring `00:02` records `TIMING_CONTRACT`; never silently delay. No decision fills on `00:00`.

- [ ] **Step 2: Write failing event-order tests**

At one timestamp, close an existing position first and release its risk; then a same-timestamp new decision must be allowed if that release makes it fit. Two simultaneous decisions A/B that exceed combined cap must deterministically fill A then reject B.

- [ ] **Step 3: Write failing NO_TRADE/rejection tests**

Preserve `NO_TRADE` with `RejectionCode.NO_TRADE`. Exercise invalid stop/target, daily halt, simultaneous cap, invalid size.

- [ ] **Step 4: Write failing daily halt/reset tests**

Cross the 1.50% day realized-loss threshold; reject later same-day entries; do not force-close existing positions solely because of halt; next UTC date resets using current realized risk equity as new basis.

- [ ] **Step 5: Write failing same-bar post-entry/EOD tests**

A fill at bar open may stop/target on that bar's later high/low; both reachable -> stop. Remaining positions close at final executable close with `END_OF_DATA`.

- [ ] **Step 6: Run RED**

```bash
python -m unittest tests.test_phase3_engine -v
```

- [ ] **Step 7: Implement timing validation/indexing**

For each directional decision, find first supplied bar for that symbol strictly after the decision timestamp. Require exact equality to declared earliest executable timestamp. Invalid declaration becomes preserved `TIMING_CONTRACT` rejection.

Index valid decisions by `(earliest_executable_timestamp_utc, symbol)`; sort bucket by `decision_id`.

- [ ] **Step 8: Implement event loop**

```text
for each global timestamp ascending:
  roll UTC risk day
  process existing-position exits first, position_id order
    gross = pnl_usd(reference entry, reference exit)
    slipped = pnl_usd(slipped entry, slipped exit)
    slippage_cost = max(0, gross - slipped)
    commission = entry_commission + exit_commission
    financing = exit financing
    net = gross - slippage_cost - commission - financing
    release exact reserved risk
    record realized net PnL immediately
    append TradeRecord and EquityCheckpoint
  process decisions scheduled now, decision_id order
    preserve NO_TRADE
    compute executable reference entry
    risk-assess
    reject -> RejectionRecord
    approve -> OrderIntent, fill entry, reserve approved USD risk
    evaluate same-bar post-entry stop/target immediately
```

After final timestamp, close all remaining positions in `position_id` order via `END_OF_DATA`; release/realize each.

- [ ] **Step 9: Build deterministic identity and metrics**

Run identity contains exactly:

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

No current clock, hostname, UUID, or process metadata. Call `compute_backtest_metrics` before returning `BacktestRun`.

- [ ] **Step 10: Run GREEN**

```bash
python -m unittest tests.test_phase3_engine -v
```

- [ ] **Step 11: Commit**

```bash
git add src/fmp/backtest/engine.py tests/test_phase3_engine.py
git commit -m "[phase1-no-source] Add deterministic Phase 3 backtest engine"
```

---

## Task 7: Prove end-to-end golden scenarios

**Files:**
- Create: `tests/test_phase3_acceptance.py`
- Modify Phase 3 production files only when a golden failure proves a defect.

**Interfaces:** Uses public `run_backtest` and `write_backtest_artifacts`; scripted decisions only, no strategy module.

- [ ] **Step 1: Add LONG golden scenario**

Zero slippage/commission. LONG fills next bar on ASK, exits on BID. Assert exact reference/execution prices, units, timestamps, gross/net PnL, and risk equity.

- [ ] **Step 2: Add SHORT golden scenario**

SHORT fills on BID, exits on ASK; hand-check PnL.

- [ ] **Step 3: Add ambiguity/gap scenarios**

```text
both stop+target reachable -> STOP + ambiguous=true
gap through stop -> worse executable open reference
favorable target gap -> declared target reference
```

- [ ] **Step 4: Add JPY/non-JPY sizing scenarios**

Prove Task 3 math through the full engine, including USDJPY PnL conversion at executable exit price.

- [ ] **Step 5: Add nonzero-cost scenario**

Use 1 pip slippage + fixed commission. Assert:

```text
gross reference PnL
slippage degradation = reference PnL - slipped PnL
commission = entry + exit commissions
financing = 0
net = gross - slippage - commission
```

Explicitly prove slippage is not subtracted twice.

- [ ] **Step 6: Add risk-control scenarios**

Prove per-trade cap, simultaneous cap, exit-before-entry release, daily halt, next-day reset.

- [ ] **Step 7: Add repeated-run equality**

Run identical fixture/config twice; compare semantic `BacktestRun` content and byte-identical artifact files/digests.

- [ ] **Step 8: Run acceptance tests and fix production defects only**

```bash
python -m unittest tests.test_phase3_acceptance -v
```

Do not weaken hand-calculated expectations to match code. Patch the smallest responsible production unit, rerun its focused tests and acceptance.

- [ ] **Step 9: Commit**

```bash
git add tests/test_phase3_acceptance.py src/fmp/contracts.py src/fmp/risk src/fmp/backtest src/fmp/reporting
git commit -m "[phase1-no-source] Prove Phase 3 golden scenarios"
```

---

## Task 8: Record Phase 3 ACTIVE semantics

**Files:**
- Modify: `docs/project-state.md`
- Modify: `docs/decision-log.md`

**Interfaces:** Add `DEC-016 — Phase 3 backtester semantics`; status becomes ACTIVE, not PASS.

- [ ] **Step 1: Add DEC-016**

Record:

```text
daily loss basis = UTC day-start realized risk equity
-1.50% blocks new entries for remainder of UTC date
existing positions not force-closed solely by daily halt
exits before entries at equal timestamps
decision_id orders simultaneous decisions
LONG ASK/BID; SHORT BID/ASK
stop wins unresolved stop/target ambiguity
target gaps receive no favorable improvement
EOD uses final executable close side
no real-money permission changes
```

- [ ] **Step 2: Update project state**

Set:

```text
Current phase: Phase 3 — Backtesting Engine
Phase status: ACTIVE
Next milestone: verify deterministic Phase 3 golden acceptance suite and inspect acceptance artifacts
```

Preserve Phase 2 PASS/checkpoint evidence; state Phase 4 has not started.

- [ ] **Step 3: Commit**

```bash
git add docs/project-state.md docs/decision-log.md
git commit -m "[phase1-no-source] Record Phase 3 backtester semantics"
```

---

## Task 9: Full regression verification and safe merge

**Files:** No intended new files unless verification proves a defect.

- [ ] **Step 1: Run all Phase 3 tests**

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

- [ ] **Step 2: Run full suite**

```bash
python -m unittest discover -s tests -v
```

Expected: zero failures/errors.

- [ ] **Step 3: Compile**

```bash
python -m compileall -q src tests
```

Expected exit 0.

- [ ] **Step 4: Inspect diff**

Verify:

```text
only Phase 3 source/tests/docs/spec/plan files changed
docs/phase1-exact-gap-queue.json absent
no Phase 1 source-capable workflow modified
no Supabase/raw/cloud mutation added
no strategy/Phase 4 implementation
no dependency added
```

- [ ] **Step 5: Open safe PR**

Title exactly:

```text
[phase1-no-source] Phase 3 deterministic backtesting engine
```

PR body says Phase 3 remains ACTIVE pending post-merge acceptance artifact inspection/checkpoint review.

- [ ] **Step 6: Require fresh green PR CI on exact head**

`tests` succeeds; Phase 1 source-capable PR workflows skip. Merge only exact verified head with squash title/message containing `[phase1-no-source]`.

- [ ] **Step 7: Verify post-merge main**

Confirm main at squash commit, push tests success, and no Phase 1 acquisition-capable workflow triggered.

---

## Task 10: Produce and inspect real acceptance artifacts before closure

**Files:**
- Create after evidence: `docs/phase3-acceptance-evidence.md`
- Modify after evidence: `docs/project-state.md`, `docs/decision-log.md`

**Interfaces:** Closure checkpoint `fmp-v1-phase3-backtester`.

- [ ] **Step 1: Run merged-main acceptance fixture**

Small hand-calculable scripted fixture must exercise LONG, SHORT, nonzero slippage/commission, one ambiguity, one simultaneous-risk rejection, one daily halt, one next-day reset. Persist with `write_backtest_artifacts`.

- [ ] **Step 2: Independently inspect artifacts**

Verify summary identities, exact trade PnL, rejection codes, equity checkpoints, metrics math, actual file SHA/size against manifest, repeated-run byte/digest equality.

- [ ] **Step 3: Review Phase 3 gate line-by-line**

Compare evidence to `docs/build-order.md` and the Phase 3 design. Any unmet item keeps Phase 3 ACTIVE.

- [ ] **Step 4: Record acceptance only if every gate passes**

Create `docs/phase3-acceptance-evidence.md` with immutable code/data/config identities, exact run/test identities, artifact hashes, hand calculations, and zero unresolved acceptance failures.

- [ ] **Step 5: Create checkpoint and formal PASS in separate closure change**

Only after evidence review passes:

```text
create checkpoint fmp-v1-phase3-backtester
update project-state to Phase 3 PASS
record acceptance decision in decision-log
keep Phase 4 explicitly unstarted
```
