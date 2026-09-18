# Phase 8 Live Shadow Implementation Plan

> **SUPERSEDED FOR OPERATOR USE (2026-09-17):** The connector/operator steps in this historical plan are superseded by **DEC-037** for the active Phase 8 experiment. Use `docs/phase8-mt5-operator-handoff.md` for the current FP Markets MT5 demo workflow. This file is retained as historical design/implementation context and its old operator commands must not be used for `EXP-20260917-010`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task with review checkpoints.

**Goal:** Implement the approved Phase 8 OANDA Practice live-shadow protocol for the sole USDJPY 15m `session_breakout` survivor while making broker order submission structurally impossible, preserving Phase 3/4/7 semantics, and producing deterministic replayable evidence for the frozen Phase 8 acceptance gate.

**Architecture:** Add a narrow `fmp.shadow` package around existing strategy, decision, cost, risk, and reporting primitives. The package owns only the Phase 8-specific live quote boundary, normalization/liveness, live-bar construction, shadow-only simulation, append-only evidence, deterministic replay, historical spread reference, campaign registration, and acceptance review. The network transport is a hard-coded OANDA Practice pricing-stream GET client for `USD_JPY`; it has no generic HTTP method/base URL/path API and no order/trade/position mutation surface. Long-running live qualification/campaign execution is explicit and operator-started; CI remains source-free and may test deterministic replay only.

**Tech Stack:** Python 3.11+, standard library networking/time/JSON/hashlib/pathlib, existing FMP `polars` stack only where historical Phase 2/7 loading already needs it, pytest, existing Phase 3 risk/backtest primitives, existing Phase 4 session-breakout generator, existing Phase 7 canonical data/evidence identities. Do not add a paid service, broker SDK, MT5 package, dashboard, database, or generic HTTP client abstraction.

**Spec:** `docs/superpowers/specs/2026-09-15-phase8-shadow-design.md`

## Global constraints

- **Runtime code is blocked until all four design completion prerequisites are true:** written design approved; `fmp-v1-phase7-walk-forward` exists at exact SHA `b6fb0176555b071fef6d1070edf3407b03cd60c9`; this implementation plan exists; Phase 8 source-of-truth activation is committed.
- At plan-writing time the Phase 7 tag is intentionally absent. Tasks 2+ below MUST NOT begin until Task 1's exact-tag preflight passes and activation is merged/committed.
- Preserve `DEC-008`: no demo order placement, live order placement, broker mutation, or real-money path.
- Only `USDJPY` / provider instrument `USD_JPY`, 15m `session_breakout`, 5-pip buffer, 1.5x target-range multiple, exact existing London session semantics, exact 16:00 `Europe/London` flat time, no ML overlay.
- OANDA Practice pricing-stream boundary is exactly: `GET https://stream-fxpractice.oanda.com/v3/accounts/{account_id}/pricing/stream?instruments=USD_JPY&snapshot=true&includeHomeConversions=false`.
- No caller-supplied host, base URL, HTTP method, arbitrary path, instrument, production host, generic request helper, broker execution adapter, order endpoint, trade endpoint, or position endpoint.
- Credentials come only from environment/local secret storage. Never log/persist token or plain account ID. Durable evidence may contain only a SHA-256 account fingerprint.
- No REST candle backfill, historical repair, hidden continuation after gaps, provider failover, parameter search, alternate pair/timeframe, or post-registration threshold changes.
- Stale timeout = 15 seconds. Entry quote deadline = 5 seconds after signal-known time. Scheduled-exit quote deadline = 5 seconds after exact London 16:00.
- Cost scenarios are exactly 0.2/0.5/1.0 pips adverse per fill. 0.2 and 0.5 gate; 1.0 is diagnostic only. Each virtual account starts at exactly $100,000 and carries independently through the accepted campaign.
- Reuse `generate_session_breakout_candidates`, `candidate_to_decision`, `RiskConfig`, `RiskState`, `assess_decision`, `reserve_risk`, `release_risk`, `record_realized_pnl`, `pnl_usd`, `apply_adverse_slippage`, `ZeroCommission`, and `ZeroFinancing` rather than reimplementing their semantics.
- Follow repository TDD: RED test -> smallest implementation -> focused tests -> phase regression. Keep commits scoped and source-free unless the task is an explicitly operator-started live qualification/campaign step.

---

### Task 1: Verify the Phase 7 checkpoint and activate Phase 8 source of truth

**Files:**
- Modify: `docs/superpowers/specs/2026-09-15-phase8-shadow-design.md`
- Modify: `docs/decision-log.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Modify: `docs/source-register.md`
- Create: `tests/test_phase8_protocol_state.py`

**Step 1: Run the hard checkpoint preflight before editing activation records**

Run:

```bash
actual="$(git rev-list -n 1 fmp-v1-phase7-walk-forward 2>/dev/null || true)"
test "$actual" = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
```

Expected now: FAIL because the tag is intentionally absent. Stop here until the tag is created at the exact closure SHA. Do not create runtime files while this fails.

After the tag exists, rerun and require PASS.

**Step 2: Write the failing protocol-state test**

Test exact frozen records, including:

```python
EXPECTED_PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
EXPECTED_EXPERIMENT = "EXP-20260915-009"
EXPECTED_DECISION = "DEC-036"


def test_phase8_source_of_truth_is_active_and_execution_remains_locked():
    decision_log = Path("docs/decision-log.md").read_text()
    experiment_log = Path("docs/experiment-log.md").read_text()
    state = Path("docs/project-state.md").read_text()
    sources = Path("docs/source-register.md").read_text()

    assert "DEC-036" in decision_log
    assert "EXP-20260915-009" in experiment_log
    assert "Phase 8" in state and "ACTIVE" in state
    assert "stream-fxpractice.oanda.com" in sources
    assert "DEC-008" in decision_log
    assert "real-money" in state.lower() and "locked" in state.lower()
```

Run:

```bash
pytest -q tests/test_phase8_protocol_state.py
```

Expected: FAIL before activation edits.

**Step 3: Activate exactly the approved protocol**

- Add `DEC-036` with the approved design identity and exact Phase 7 checkpoint SHA.
- Add planned/running `EXP-20260915-009` with only the sole survivor and frozen thresholds.
- Mark Phase 8 `ACTIVE`, not PASS.
- Reverify/update SRC-003/SRC-004 on 2026-09-15 and record OANDA Practice pricing stream as the selected Phase 8 quote role; MT5 remains deferred.
- Change the design status from pending written-spec review to approved/activated, while preserving the runtime prerequisites and demo/live locks.

**Step 4: Rerun source-of-truth tests**

```bash
pytest -q tests/test_phase8_protocol_state.py tests/test_phase7_acceptance_state.py tests/test_phase7_protocol_state.py
```

Expected: PASS.

**Step 5: Commit activation before runtime work**

```bash
git add docs/superpowers/specs/2026-09-15-phase8-shadow-design.md docs/decision-log.md docs/experiment-log.md docs/project-state.md docs/source-register.md tests/test_phase8_protocol_state.py
git commit -m "[phase1-no-source] Activate Phase 8 shadow protocol"
```

Do not combine this activation commit with runtime code.

---

### Task 2: Freeze Phase 8 constants and shadow-only contracts

**Files:**
- Create: `src/fmp/shadow/__init__.py`
- Create: `src/fmp/shadow/contracts.py`
- Create: `tests/test_phase8_contracts.py`

**Step 1: Write failing contract tests**

Cover exact constants, UTC validation, finite positive quote sides, fixed cost scenarios, immutable strategy identity, and the absence of any submit/send/order method on shadow objects.

Expected public constants/interfaces:

```python
PHASE8_EXPERIMENT_ID = "EXP-20260915-009"
PHASE7_CHECKPOINT_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_CHECKPOINT_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
PRACTICE_STREAM_HOST = "stream-fxpractice.oanda.com"
PRACTICE_STREAM_PATH_TEMPLATE = "/v3/accounts/{account_id}/pricing/stream"
PROVIDER_INSTRUMENT = "USD_JPY"
FMP_SYMBOL = "USDJPY"
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
STARTING_EQUITY_USD = 100_000.0
LIVENESS_TIMEOUT_SECONDS = 15.0
QUOTE_DEADLINE_SECONDS = 5.0
```

Add frozen dataclasses/enums for at least:

```python
@dataclass(frozen=True, slots=True)
class NormalizedQuote:
    source_time_utc: datetime
    received_at_utc: datetime
    receive_monotonic_ns: int
    symbol: str
    bid: float
    ask: float
    tradeable: bool

@dataclass(frozen=True, slots=True)
class HeartbeatEvent:
    source_time_utc: datetime
    received_at_utc: datetime
    receive_monotonic_ns: int

@dataclass(frozen=True, slots=True)
class ShadowIntent:
    decision: Decision
    scheduled_exit: ScheduledExit
    units: int
    reserved_risk_usd: float
    slippage_pips: float

class ShadowOutcome(str, Enum):
    COMPLETED = "COMPLETED"
    OUTCOME_UNKNOWN_AFTER_GAP = "OUTCOME_UNKNOWN_AFTER_GAP"
    ENTRY_DEADLINE_MISSED = "ENTRY_DEADLINE_MISSED"
    EXIT_DEADLINE_MISSED = "EXIT_DEADLINE_MISSED"
```

`ShadowIntent` is data only. It must expose no `send`, `submit`, `place`, `execute_broker`, or broker adapter reference.

**Step 2: Run RED**

```bash
pytest -q tests/test_phase8_contracts.py
```

Expected: FAIL because `fmp.shadow` does not exist.

**Step 3: Implement the smallest immutable contracts**

Use the same stable JSON rules already used by strategy/Phase 7 evidence: UTC only, sorted keys, no NaN/Infinity, explicit enum values.

**Step 4: Run focused tests**

```bash
pytest -q tests/test_phase8_contracts.py
```

Expected: PASS.

**Step 5: Commit**

```bash
git add src/fmp/shadow tests/test_phase8_contracts.py
git commit -m "Implement Phase 8 shadow contracts"
```

---

### Task 3: Implement the structurally GET-only OANDA Practice pricing stream

**Files:**
- Create: `src/fmp/shadow/oanda.py`
- Create: `tests/test_phase8_oanda.py`

**Step 1: Write failing tests for the exact wire boundary**

Tests must monkeypatch the module's stdlib HTTPS connection, not inject a configurable host/method/path into runtime constructors.

Require:

- host exactly `stream-fxpractice.oanda.com`;
- HTTP verb exactly `GET`;
- path exactly `/v3/accounts/{account_id}/pricing/stream`;
- query exactly `instruments=USD_JPY`, `snapshot=true`, `includeHomeConversions=false`;
- Authorization header uses the token in-memory only;
- constructor accepts account ID/token, but no host/base_url/method/path/instrument argument;
- no production host strings in `src/fmp/shadow/*.py`;
- no order/trade/position endpoint construction.

Target interface:

```python
class OandaPracticePricingStream:
    def __init__(self, *, account_id: str, token: str) -> None: ...

    def iter_lines(self) -> Iterator[bytes]: ...
```

Do not add `request(method, url, ...)` or any public generic HTTP helper.

**Step 2: Run RED**

```bash
pytest -q tests/test_phase8_oanda.py
```

**Step 3: Implement with standard-library HTTPS only**

Keep method/host/path/query literals internal and fixed. Validate account/token non-empty; redact them from exceptions. Refuse redirects or response behavior that escapes the exact Practice host.

**Step 4: Run focused tests**

```bash
pytest -q tests/test_phase8_oanda.py
```

Expected: PASS.

**Step 5: Commit**

```bash
git add src/fmp/shadow/oanda.py tests/test_phase8_oanda.py
git commit -m "Implement GET-only OANDA Practice quote transport"
```

---

### Task 4: Parse and normalize PRICE/HEARTBEAT messages fail-closed

**Files:**
- Modify: `src/fmp/shadow/oanda.py`
- Create: `src/fmp/shadow/normalization.py`
- Create: `tests/test_phase8_normalization.py`

**Step 1: Write failing parser/normalization tests**

Cover:

- newline-delimited JSON;
- only `PRICE` and `HEARTBEAT` types accepted;
- provider instrument must be `USD_JPY`;
- best bid = maximum finite positive bid ladder price;
- best ask = minimum finite positive ask ladder price;
- ladder ordering irrelevant;
- `tradeable=false` retained only as non-executable observation;
- absent/non-finite/non-positive/crossed sides rejected;
- UTC provider timestamps;
- source-time regression fails the stream segment;
- exact duplicate may dedupe only when source time/instrument/bid/ask/tradeable all match;
- conflicting duplicate is integrity failure;
- token/account ID never appears in exceptions or serialized normalized evidence.

Target pure function:

```python
def normalize_provider_message(
    raw: Mapping[str, object],
    *,
    received_at_utc: datetime,
    receive_monotonic_ns: int,
) -> NormalizedQuote | HeartbeatEvent: ...
```

**Step 2: Run RED**

```bash
pytest -q tests/test_phase8_normalization.py
```

**Step 3: Implement pure parsing/normalization**

Do not let provider liquidity, units-available, account state, or home conversion fields enter strategy data.

**Step 4: Run focused tests**

```bash
pytest -q tests/test_phase8_oanda.py tests/test_phase8_normalization.py
```

**Step 5: Commit**

```bash
git add src/fmp/shadow/oanda.py src/fmp/shadow/normalization.py tests/test_phase8_normalization.py
git commit -m "Normalize Phase 8 OANDA quote events"
```

---

### Task 5: Add the bounded connector qualification command

**Files:**
- Create: `src/fmp/shadow/qualification.py`
- Create: `src/fmp/shadow/cli.py`
- Create: `scripts/phase8_shadow.py`
- Create: `tests/test_phase8_qualification.py`
- Create: `tests/test_phase8_cli.py`

**Step 1: Write failing qualification tests with a fake stream and fake clocks**

Freeze outcomes such as:

```python
class QualificationOutcome(str, Enum):
    PASS = "PASS"
    INCONCLUSIVE = "INCONCLUSIVE"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    CONNECTOR_REJECTED = "CONNECTOR_REJECTED"
```

Require PASS only after successful auth/connection, >=100 valid PRICE, >=6 HEARTBEAT, USD_JPY only, quote integrity, non-regressing UTC source time, no liveness gap >15 seconds, no malformed/unknown silent acceptance, and exact GET/Practice boundary audit.

The run lasts at most ten minutes and may stop early only after both count minima are met.

**Step 2: Prove qualification imports no strategy/risk modules**

Add a test that inspects the qualification module imports/source and rejects `fmp.strategies`, `fmp.research.adapter`, and `fmp.risk`.

**Step 3: Run RED**

```bash
pytest -q tests/test_phase8_qualification.py tests/test_phase8_cli.py
```

**Step 4: Implement only `qualify` CLI first**

Example operator surface:

```bash
OANDA_PRACTICE_ACCOUNT_ID=... OANDA_PRACTICE_TOKEN=... \
python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification
```

Credentials are environment-only. No command-line token/account parameters.

**Step 5: Run focused tests and commit**

```bash
pytest -q tests/test_phase8_qualification.py tests/test_phase8_cli.py
git add src/fmp/shadow/qualification.py src/fmp/shadow/cli.py scripts/phase8_shadow.py tests/test_phase8_qualification.py tests/test_phase8_cli.py
git commit -m "Implement bounded Phase 8 connector qualification"
```

Do not run live qualification as part of this code task.

---

### Task 6: Build complete-only 1m and 15m live bid/ask bars

**Files:**
- Create: `src/fmp/shadow/bars.py`
- Create: `tests/test_phase8_bars.py`

**Step 1: Write failing bar tests**

Cover exact semantics:

- UTC 1m bars left-labelled at minute start;
- only valid `tradeable=true` PRICE events form OHLC;
- bid and ask OHLC remain separate;
- no forward fill;
- heartbeat can advance/close a bucket but never creates a price observation;
- 1m complete only with >=1 valid tradeable price and no stale interval intersecting it;
- 15m left-labelled, exactly 15 consecutive 1m bars, complete only if all 15 complete;
- 15m becomes knowable only at interval end;
- stale/gap intersection invalidates every crossed interval;
- no historical candle backfill hook exists.

Target surface:

```python
class LiveBarBuilder:
    def on_quote(self, quote: NormalizedQuote) -> tuple[QuoteBar, ...]: ...
    def on_time_advance(self, now_utc: datetime) -> tuple[QuoteBar, ...]: ...
    def mark_stale_interval(self, start_utc: datetime, end_utc: datetime) -> None: ...
```

Only completed 15m bars are exposed to the strategy adapter.

**Step 2: Run RED, implement, rerun**

```bash
pytest -q tests/test_phase8_bars.py
```

**Step 3: Commit**

```bash
git add src/fmp/shadow/bars.py tests/test_phase8_bars.py
git commit -m "Build Phase 8 complete-only live bars"
```

---

### Task 7: Reuse the frozen session-breakout and decision bridge unchanged

**Files:**
- Create: `src/fmp/shadow/strategy.py`
- Create: `tests/test_phase8_strategy.py`
- Regression-only: `src/fmp/strategies/session_breakout.py`
- Regression-only: `src/fmp/research/adapter.py`

**Step 1: Write failing parity tests**

The adapter must construct only:

```python
SessionBreakoutConfig(
    buffer_pips=5,
    target_range_multiple=1.5,
    timeframe="15m",
)
```

Then call `generate_session_breakout_candidates(...)` and `candidate_to_decision(...)` without reimplementing London windows, range logic, signal timing, stop/target geometry, or scheduled exit.

Tests must cover:

- USDJPY only;
- London DST behavior through existing strategy tests;
- no candidate from missing/incomplete 15m context;
- signal-known time remains `T + 15m`;
- scheduled exit remains exact 16:00 `Europe/London`;
- requested risk fraction exactly 0.0025;
- no ML/model import.

**Step 2: Run RED then implement a narrow adapter**

```bash
pytest -q tests/test_phase8_strategy.py tests/test_phase4_session_breakout.py tests/test_phase4_session_breakout_research.py
```

**Step 3: Commit**

```bash
git add src/fmp/shadow/strategy.py tests/test_phase8_strategy.py
git commit -m "Bridge frozen session breakout into Phase 8"
```

---

### Task 8: Implement shadow-only entry, risk sizing, stop/target, and time-exit simulation

**Files:**
- Create: `src/fmp/shadow/simulation.py`
- Create: `tests/test_phase8_simulation.py`
- Regression-only: `src/fmp/backtest/costs.py`
- Regression-only: `src/fmp/risk/policy.py`
- Regression-only: `src/fmp/risk/sizing.py`

**Step 1: Write failing simulation tests for executable-side semantics**

Require:

- first valid tradeable quote at/after signal-known and <=5 seconds is entry reference;
- LONG entry reference = ask; SHORT entry reference = bid;
- LONG exits observe bid; SHORT exits observe ask;
- adverse slippage uses `apply_adverse_slippage`;
- adverse stop gap uses worse observed executable quote;
- favorable target jump receives no improvement beyond declared target;
- exact London 16:00 time exit uses first valid quote <=5 seconds after flat time;
- missed entry deadline opens nothing;
- missed time-exit deadline invalidates outcome, no silent extension;
- stale gap while open -> `OUTCOME_UNKNOWN_AFTER_GAP`, excluded from financial metrics;
- risk uses `RiskConfig()` + `RiskState` + `assess_decision` and existing JPY sizing;
- 0.2/0.5/1.0 accounts are independent and begin at $100,000;
- commission/financing remain zero.

Target orchestration may use one state per scenario:

```python
@dataclass(slots=True)
class ScenarioState:
    slippage_pips: float
    risk_state: RiskState
    open_positions: dict[str, ShadowPosition]
    completed_trades: list[ShadowTrade]
```

Do not use `OrderIntent` as a broker-facing API. If a Phase 3-compatible in-memory value is useful internally for calculations, keep it private; the public Phase 8 contract remains `ShadowIntent` with no submission behavior.

**Step 2: Run RED**

```bash
pytest -q tests/test_phase8_simulation.py
```

**Step 3: Implement the event-driven simulator using existing primitives**

For PnL/risk accounting, call the existing primitives; do not duplicate JPY conversion or daily-halt math.

**Step 4: Run focused regressions**

```bash
pytest -q tests/test_phase8_simulation.py tests/test_phase3_costs.py tests/test_phase3_risk.py tests/test_phase3_execution.py
```

**Step 5: Commit**

```bash
git add src/fmp/shadow/simulation.py tests/test_phase8_simulation.py
git commit -m "Implement Phase 8 shadow-only simulation"
```

---

### Task 9: Implement append-only evidence with redaction and manifest binding

**Files:**
- Create: `src/fmp/shadow/evidence.py`
- Create: `tests/test_phase8_evidence.py`

**Step 1: Write failing evidence tests**

Each segment must append deterministic JSONL/JSON artifacts for:

1. accepted raw PRICE/HEARTBEAT provider objects plus receive metadata;
2. normalized events;
3. 1m/15m bars;
4. candidate/decision/no-trade/invalidation events;
5. per-scenario position/trade events;
6. operational connect/disconnect/stale/restart/rejection events;
7. SHA-256 manifest.

Manifest must bind at least:

```python
{
    "code_commit": ...,
    "phase7_checkpoint_tag": "fmp-v1-phase7-walk-forward",
    "phase7_checkpoint_sha": "b6fb0176555b071fef6d1070edf3407b03cd60c9",
    "phase7_experiment": "EXP-20260915-008",
    "phase7_outcome": "PASS / PROMOTE",
    "strategy": {"id": "session_breakout", "symbol": "USDJPY", "timeframe": "15m", "buffer_pips": 5, "target_range_multiple": 1.5},
    "connector_protocol": ...,
    "practice_host": "stream-fxpractice.oanda.com",
    "provider_instrument": "USD_JPY",
    "account_fingerprint_sha256": ...,
    "slippage_scenarios": [0.2, 0.5, 1.0],
    "risk_policy": RiskConfig().to_config(),
    "file_sha256": {...},
    "replay_result_digest": ...,
}
```

Tests must assert raw request headers/token/plain account ID never appear in any persisted bytes, including exception/operational records.

**Step 2: Run RED, implement stable append/write helpers, rerun**

```bash
pytest -q tests/test_phase8_evidence.py
```

Use canonical sorted JSON and explicit newline conventions so replay can compare bytes exactly.

**Step 3: Commit**

```bash
git add src/fmp/shadow/evidence.py tests/test_phase8_evidence.py
git commit -m "Implement append-only Phase 8 evidence"
```

---

### Task 10: Implement liveness, restart invalidation, and the explicit event loop

**Files:**
- Create: `src/fmp/shadow/runner.py`
- Modify: `src/fmp/shadow/cli.py`
- Create: `tests/test_phase8_runner.py`

**Step 1: Write failing runner tests with injected clocks and fake normalized event sources**

Cover:

- 15 seconds since last valid PRICE or HEARTBEAT => stale;
- stale blocks new entries;
- stale invalidates intersected bars;
- stale while open invalidates all scenario outcomes for that candidate;
- every connect/disconnect/stale/restart/rejection event is durably appended;
- restart never assumes unseen path;
- if required London context was missed, current London date is ineligible for new entries;
- restart with open shadow position -> `OUTCOME_UNKNOWN_AFTER_GAP`;
- capture can resume but strategy waits for later fully observed date;
- no backfill, broker-position query, or order reconciliation call exists.

Target runner dependency direction:

```text
OandaPracticePricingStream
  -> normalize_provider_message
  -> EvidenceWriter(raw + normalized)
  -> LiveBarBuilder
  -> frozen strategy adapter
  -> shadow simulator (3 virtual accounts)
  -> EvidenceWriter(derived + operational)
```

**Step 2: Run RED**

```bash
pytest -q tests/test_phase8_runner.py
```

**Step 3: Implement a `run` CLI that requires explicit operator action**

Example:

```bash
OANDA_PRACTICE_ACCOUNT_ID=... OANDA_PRACTICE_TOKEN=... \
python scripts/phase8_shadow.py run --campaign-dir evidence/phase8/campaign
```

No daemon install, cron job, automatic CI start, or background hosting.

**Step 4: Run focused tests and commit**

```bash
pytest -q tests/test_phase8_runner.py tests/test_phase8_bars.py tests/test_phase8_simulation.py
git add src/fmp/shadow/runner.py src/fmp/shadow/cli.py tests/test_phase8_runner.py
git commit -m "Orchestrate explicit Phase 8 shadow runs"
```

---

### Task 11: Add deterministic offline replay

**Files:**
- Create: `src/fmp/shadow/replay.py`
- Modify: `src/fmp/shadow/cli.py`
- Create: `tests/test_phase8_replay.py`

**Step 1: Write failing replay tests from captured fixture messages**

Given the same raw provider messages and frozen config, two offline replays must produce byte-identical:

- normalized quotes;
- bars;
- candidates/decisions;
- shadow trade/outcome ledger;
- financial metrics.

Runtime `received_at_utc` and monotonic timing remain operational evidence but must not perturb deterministic decision/financial serialization where they do not affect semantics.

**Step 2: Run RED**

```bash
pytest -q tests/test_phase8_replay.py
```

**Step 3: Implement replay through the same normalization/bar/strategy/simulation pipeline**

Do not create a separate replay-only strategy or simulator.

CLI:

```bash
python scripts/phase8_shadow.py replay --segment-dir evidence/phase8/campaign/<segment>
```

Replay writes a digest and refuses acceptance when derived bytes differ.

**Step 4: Rerun and commit**

```bash
pytest -q tests/test_phase8_replay.py tests/test_phase8_evidence.py
git add src/fmp/shadow/replay.py src/fmp/shadow/cli.py tests/test_phase8_replay.py
git commit -m "Add deterministic Phase 8 offline replay"
```

---

### Task 12: Build and freeze the historical spread reference

**Files:**
- Create: `src/fmp/shadow/reference.py`
- Modify: `src/fmp/shadow/cli.py`
- Create: `tests/test_phase8_reference.py`

**Step 1: Write failing identity/parity tests**

The builder must bind to:

- Phase 7 checkpoint SHA `b6fb0176555b071fef6d1070edf3407b03cd60c9`;
- Phase 7 experiment `EXP-20260915-008` PASS/PROMOTE;
- authoritative Stage 2 run `35015277625`;
- accepted Phase 2 USDJPY artifact `10327600628` and ZIP SHA-256 `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`;
- processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`;
- exact frozen `session_breakout` config.

For every completed Phase 7 survivor trade admitted to the reference:

```python
entry_spread_pips = (entry_bar.ask_open - entry_bar.bid_open) / pip_size("USDJPY")
exit_spread_pips = (exit_bar.ask_open - exit_bar.bid_open) / pip_size("USDJPY")
```

The output stores count, median and p95 entry spreads, median and p95 exit spreads, exact identities, method version, and artifact SHA-256.

**Step 2: Reuse existing Phase 7 loading/strategy/backtest primitives, not aggregate-only evidence**

Where trade timestamps are needed, deterministically reproduce the frozen survivor trade path from accepted Phase 2 data using the exact Phase 7 windows/config and existing `run_backtest`. Do not infer entry/exit spreads from aggregate Stage 2 metrics.

**Step 3: Run RED, implement, rerun**

```bash
pytest -q tests/test_phase8_reference.py tests/test_phase7_data.py tests/test_phase7_evaluation.py
```

**Step 4: Commit**

```bash
git add src/fmp/shadow/reference.py src/fmp/shadow/cli.py tests/test_phase8_reference.py
git commit -m "Build frozen Phase 8 spread reference"
```

The actual reference artifact is generated only after implementation verification and before first scored live campaign observation.

---

### Task 13: Freeze campaign registration and denominator accounting

**Files:**
- Create: `src/fmp/shadow/campaign.py`
- Modify: `src/fmp/shadow/cli.py`
- Create: `tests/test_phase8_campaign.py`

**Step 1: Write failing campaign tests**

Registration is immutable after the first scored observation and contains:

- campaign start UTC;
- first London date;
- code/reference identities;
- all acceptance thresholds;
- spread-reference digest;
- exact slippage/risk/provider/strategy identities.

Denominator logic:

- every Monday-Friday London date from registered start through review cutoff counts;
- only provider-documented full-market closure recorded before the date begins may be excluded;
- outage/failed dates cannot be removed after observation.

Review eligibility requires all:

```python
completed_scorable_trades_0p2 >= 40
elapsed_calendar_weeks >= 8
fully_observed_london_dates >= 30
all_scored_trades_have_complete_path is True
all_three_scenarios_share_candidate_sequence is True
```

**Step 2: Run RED, implement immutable registration/accounting, rerun**

```bash
pytest -q tests/test_phase8_campaign.py
```

**Step 3: Commit**

```bash
git add src/fmp/shadow/campaign.py src/fmp/shadow/cli.py tests/test_phase8_campaign.py
git commit -m "Freeze Phase 8 campaign registration"
```

---

### Task 14: Implement acceptance metrics and exact Phase 8 review outcomes

**Files:**
- Create: `src/fmp/shadow/gates.py`
- Modify: `src/fmp/shadow/cli.py`
- Create: `tests/test_phase8_gates.py`

**Step 1: Write boundary-first failing tests**

Test values exactly on and one epsilon either side of every threshold.

Structural safety:
- exact GET-only Practice boundary;
- no production/order mutation surface;
- no token/plain account ID in durable artifacts.

Operational integrity:
- qualification PASS;
- >=30 fully observed London dates;
- valid date coverage >=90%;
- zero malformed silently accepted;
- zero stale-gap outcomes in financial metrics;
- all disconnect/reconnect/stale events logged.

Timing:
- p99 processing latency <=250 ms;
- scored entry quote delay <=5 s;
- scored time-exit quote delay <=5 s.

Spread:
- live median/p95 entry and exit each <= corresponding historical value +0.5 pip.

Financial at both 0.2 and 0.5:
- net return >0;
- expectancy/trade >0;
- PF >1.0;
- max drawdown <=0.05;
- 0.2 trade count >=40.

Replay:
- deterministic bytes/metrics identical.

Exact outcomes:

```python
class Phase8ReviewOutcome(str, Enum):
    PASS = "PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN"
    NEED_MORE_DATA = "PHASE8_NEED_MORE_DATA"
    REJECT_OPERATIONAL = "PHASE8_REJECT_OPERATIONAL_MISMATCH"
    REJECT_MARKET = "PHASE8_REJECT_MARKET_MISMATCH"
    REJECT_FINANCIAL = "PHASE8_REJECT_FINANCIAL_MISMATCH"
    REJECT_SAFETY = "PHASE8_REJECT_SAFETY_FAILURE"
```

Safety failure has its dedicated reject outcome. If implementation is sound but minimum evidence is short, return NEED_MORE_DATA and keep Phase 8 active.

**Step 2: Run RED, implement pure gates, rerun**

```bash
pytest -q tests/test_phase8_gates.py
```

**Step 3: Add `review` CLI over evidence only**

```bash
python scripts/phase8_shadow.py review --campaign-dir evidence/phase8/campaign
```

This command performs no network access.

**Step 4: Commit**

```bash
git add src/fmp/shadow/gates.py src/fmp/shadow/cli.py tests/test_phase8_gates.py
git commit -m "Implement frozen Phase 8 acceptance gates"
```

---

### Task 15: Add repository-level structural safety guards

**Files:**
- Create: `tests/test_phase8_structural_safety.py`
- Modify only if required by a real finding: `src/fmp/shadow/*.py`

**Step 1: Write source/AST guards that fail on forbidden runtime surface**

The guard should inspect runtime `src/fmp/shadow` only and reject:

- production OANDA hosts;
- `/orders`, `/trades`, `/positions`, transaction/account mutation endpoints;
- `order_send`;
- function parameters named like `base_url`, `host`, `method`, `path`, or generic `url` on the pricing transport;
- HTTP verbs other than the fixed GET request in the OANDA transport;
- imports of MT5 or any execution/broker adapter;
- public shadow methods containing `submit`, `send_order`, `place_order`, or equivalent broker mutation behavior.

Tests/docs may contain forbidden strings to prove rejection; scope the guard to runtime code.

**Step 2: Run the guard**

```bash
pytest -q tests/test_phase8_structural_safety.py
```

Expected after implementation: PASS.

**Step 3: Commit**

```bash
git add tests/test_phase8_structural_safety.py
git commit -m "Guard Phase 8 against broker mutation surfaces"
```

---

### Task 16: Full source-free implementation verification

**Files:**
- No production changes expected; fix only verified defects.

**Step 1: Run all Phase 8 tests**

```bash
pytest -q tests/test_phase8_*.py
```

Expected: PASS.

**Step 2: Run full Python regression**

```bash
pytest -q
```

Expected: all tests PASS.

**Step 3: Validate workflow YAML and compile**

```bash
ruby scripts/validate_workflow_yaml.rb
python -m compileall -q src scripts
```

Expected: PASS.

**Step 4: Regenerate Phase 3 acceptance evidence locally and test deterministic parity**

```bash
rm -rf /tmp/fmp-phase3-acceptance
python scripts/phase3_acceptance_fixture.py \
  --out /tmp/fmp-phase3-acceptance \
  --code-commit "$(git rev-parse HEAD)"
pytest -q tests/test_phase3_acceptance.py tests/test_phase3_acceptance_runner.py
```

Expected: success; Phase 3 semantics unchanged.

**Step 5: Explicitly verify no Phase 1 acquisition path ran**

No Phase 1 acquisition workflow or command is needed by Phase 8 implementation verification. Treat any accidental Phase 1 acquisition trigger as a process defect and stop.

**Step 6: Commit only if verification required fixes**

Use a focused commit naming the verified defect. Do not create a bookkeeping commit solely to claim tests ran.

---

### Task 17: Perform the explicit live connector qualification

**Files/artifacts:**
- Runtime evidence outside Git: operator-selected `evidence/phase8/qualification/...`
- Later documentation: `docs/phase8-shadow-evidence.md` only after evidence exists

**Preconditions:** Tasks 1–16 PASS; credentials available out of band; market open/active enough for the bounded sample.

**Step 1: Run qualification explicitly**

```bash
OANDA_PRACTICE_ACCOUNT_ID=... OANDA_PRACTICE_TOKEN=... \
python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification
```

Never paste credentials into shell history in a way that persists them; use the operator's approved local secret mechanism where practical.

**Step 2: Inspect the qualification manifest**

Require exact Practice GET audit, >=100 valid PRICE, >=6 HEARTBEAT, no >15s liveness gap while active, quote integrity, and zero silent malformed/unknown messages.

Outcomes:
- PASS -> continue;
- INCONCLUSIVE -> retain evidence and retry later without changing protocol;
- CONNECTOR_UNAVAILABLE/REJECTED -> retain evidence and stop Phase 8 campaign start.

**Step 3: Do not alter code/thresholds based on observed quote behavior**

A provider/protocol change requires a design amendment and source-of-truth update, not an ad hoc fallback.

---

### Task 18: Generate the frozen historical spread reference and register the campaign

**Artifacts:**
- Runtime evidence outside Git: historical reference artifact + registration record

**Step 1: Build the reference before first scored live observation**

Use the exact accepted Phase 2/7 identities and frozen Phase 7 survivor.

```bash
python scripts/phase8_shadow.py build-reference \
  --dataset-root <accepted-phase2-dataset-root> \
  --processed-manifest <accepted-usdjpy-processed-manifest> \
  --out evidence/phase8/reference
```

Use the accepted/local materialization of the exact Phase 2 USDJPY dataset and processed manifest bound by Task 12. If those artifacts must first be retrieved through the existing authenticated canonical-data path, do that separately; do not call the Phase 1 source or any OANDA candle-history endpoint.

**Step 2: Verify and freeze the reference digest**

Check trade count, entry/exit distribution rows, median/p95 values, upstream/code identity, and SHA-256.

**Step 3: Register the campaign exactly once**

```bash
python scripts/phase8_shadow.py register \
  --reference evidence/phase8/reference \
  --campaign-dir evidence/phase8/campaign
```

After the first scored observation, the registration start boundary, reference digest, and acceptance thresholds are immutable.

---

### Task 19: Run the live shadow campaign and accumulate only fully observed evidence

**Artifacts:**
- Append-only campaign evidence outside Git

**Step 1: Start explicit shadow capture when the operator chooses**

```bash
OANDA_PRACTICE_ACCOUNT_ID=... OANDA_PRACTICE_TOKEN=... \
python scripts/phase8_shadow.py run --campaign-dir evidence/phase8/campaign
```

**Step 2: Treat every restart/disconnect honestly**

Never reconstruct unseen path. Invalidate current-day context and any open outcome as specified. Resume capture only as evidence, not as fabricated continuity.

**Step 3: Replay every accepted segment offline**

```bash
python scripts/phase8_shadow.py replay --segment-dir evidence/phase8/campaign/<segment>
```

Repeat replay for every finalized accepted segment. Any mismatch blocks acceptance and requires defect correction plus fresh valid evidence; retain failed evidence.

**Step 4: Do not request acceptance review until the minimum sample is real**

Need all of:
- >=40 completed scorable 0.2-pip trades;
- >=8 elapsed calendar weeks;
- >=30 complete London dates;
- fully observed path for every scored trade;
- identical candidate sequence across 0.2/0.5/1.0 scenarios.

If minima are short, record/return `PHASE8_NEED_MORE_DATA`; do not widen thresholds or backdate the campaign.

---

### Task 20: Review Phase 8 evidence, record the outcome, and checkpoint only a verified PASS

**Files:**
- Create after real evidence: `docs/phase8-shadow-evidence.md`
- Modify: `docs/decision-log.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Create/modify acceptance-state tests as appropriate

**Step 1: Run source-free review from the frozen campaign evidence**

```bash
python scripts/phase8_shadow.py review --campaign-dir evidence/phase8/campaign
```

**Step 2: Independently inspect/recompute every gate**

Review structural safety, operational coverage, p99 timing, entry/exit deadlines, spread parity, 0.2/0.5 financial behavior, diagnostic 1.0 result, replay digest, denominator dates, stale exclusions, and sample minima.

**Step 3: Record exactly one approved review outcome**

- `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN`
- `PHASE8_NEED_MORE_DATA`
- `PHASE8_REJECT_OPERATIONAL_MISMATCH`
- `PHASE8_REJECT_MARKET_MISMATCH`
- `PHASE8_REJECT_FINANCIAL_MISMATCH`
- `PHASE8_REJECT_SAFETY_FAILURE`

`PHASE8_NEED_MORE_DATA` is non-terminal and keeps Phase 8 ACTIVE. Any reject is terminal for this frozen experiment. PASS only permits separate Phase 9 design work; it never enables demo execution.

**Step 4: Run fresh full verification after outcome docs merge**

```bash
pytest -q
ruby scripts/validate_workflow_yaml.rb
python -m compileall -q src scripts
rm -rf /tmp/fmp-phase3-acceptance
python scripts/phase3_acceptance_fixture.py \
  --out /tmp/fmp-phase3-acceptance \
  --code-commit "$(git rev-parse HEAD)"
```

**Step 5: Create `fmp-v1-phase8-shadow` only after verified PASS closure**

```bash
closure_sha="$(git rev-parse HEAD)"
git tag fmp-v1-phase8-shadow "$closure_sha"
git show --no-patch --decorate fmp-v1-phase8-shadow
```

Do not create the Phase 8 PASS checkpoint for NEED_MORE_DATA or a rejected campaign. Phase 9/demo/live/real-money execution remains locked until its own later design/approval gates.

---

## Plan self-review checklist

Before executing runtime tasks, verify:

- [ ] Written design approval is recorded.
- [ ] This plan is committed.
- [ ] `fmp-v1-phase7-walk-forward` resolves exactly to `b6fb0176555b071fef6d1070edf3407b03cd60c9`.
- [ ] `DEC-036`, `EXP-20260915-009`, Phase 8 ACTIVE state, and source-register reverification are committed before runtime code.
- [ ] No Phase 8 module can accept a caller-supplied network host/method/path/instrument.
- [ ] No order/trade/position mutation surface exists anywhere under `src/fmp/shadow`.
- [ ] Strategy logic is reused from `fmp.strategies.session_breakout`; risk/cost logic is reused from Phase 3.
- [ ] Live bars never forward-fill and stale/restart gaps never invent path.
- [ ] Evidence is append-only, secret-redacted, SHA-bound, and replayable offline.
- [ ] Historical spread reference is frozen before the campaign starts.
- [ ] Campaign registration is immutable after first scored observation.
- [ ] 0.2/0.5 gate and 1.0 diagnostic semantics remain unchanged.
- [ ] CI/source-free tests cannot accidentally start the long-running live campaign.
- [ ] Existing Phase 1–7 tests, workflow YAML validation, compile, and Phase 3 acceptance remain green.
- [ ] Phase 8 PASS never authorizes demo orders; it only unlocks separate Phase 9 design work.

## Execution handoff

When the Phase 7 checkpoint tag exists at the exact required SHA, start with **Task 1 only** and commit source-of-truth activation before touching runtime code. Then execute Tasks 2–16 with TDD and review checkpoints. Tasks 17–20 are explicit operator/evidence steps and must never be treated as automatic CI/background work.
