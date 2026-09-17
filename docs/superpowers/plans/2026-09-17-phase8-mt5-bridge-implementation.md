# Phase 8 MT5 Demo Quote Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unavailable OANDA Practice live quote edge with a structurally read-only FP Markets MT5 demo file bridge while preserving the frozen Phase 8 strategy, simulator, replay, campaign gates, and no-order boundary.

**Architecture:** A purpose-built MQL5 Expert Advisor attached to the demo `USDJPY` chart emits `BRIDGE_START`, `TICK`, and local `BRIDGE_HEARTBEAT` JSONL records into the fixed MT5 `FILE_COMMON` transport. Python auto-discovers exactly one fixed transport file on macOS, binds the bridge session, tails only records appended after reader start, normalizes ticks into the existing `NormalizedQuote` pipeline, and keeps local bridge heartbeats out of market-time/bar semantics. Evidence moves to v2 with explicit MT5 connector/session/server/source binding; campaign/replay/review reuse the existing strategy and simulation core.

**Tech Stack:** Python 3.11+, stdlib (`json`, `pathlib`, `hashlib`, `time`, `dataclasses`, `datetime`), MQL5 Expert Advisor source, `unittest`/`pytest`, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md`

## Global Constraints

- Phase 8 remains shadow-only; no practice/demo orders, live orders, broker mutation, or real-money trading.
- Phase 9 remains locked.
- Strategy remains exactly `session_breakout`, `USDJPY`, `15m`, 5-pip buffer, 1.5x target, exact `16:00 Europe/London` flat rule, no ML overlay.
- Slippage scenarios remain exactly `0.2`, `0.5`, and `1.0` pips with independent `$100,000` virtual accounts and the existing zero-commission/zero-financing simulator semantics.
- Existing campaign gates and review outcomes remain unchanged.
- Active connector identity is exactly `fmp-mt5-demo-file-bridge-v1` / `FP_MARKETS_MT5_DEMO` / `USDJPY` / `MT5_FILE_COMMON_JSONL`.
- Fixed bridge file identity is exactly `FMP/phase8-usdjpy-feed.jsonl`.
- Allowed MT5 servers are exactly `FPMarketsSC-Demo` and `FPMarketsSC-Demo2`.
- Python runtime under `src/fmp/shadow` must import no `MetaTrader5`/`mt5` package and expose no broker mutation surface.
- MQL5 bridge source must contain no order/trade/position mutation APIs or Trade library import.
- MT5 AutoTrading stays disabled during operator use.
- `BRIDGE_HEARTBEAT` is local liveness only; it never advances market time, bars, strategy, entries, exits, or quote deadlines.
- Reader start is no-backfill: only the existing `BRIDGE_START` may be read for binding; market records before reader-start EOF are never admitted to qualification/campaign processing.
- No Phase 1 acquisition command/workflow is required by this implementation.
- Live MT5 qualification is never run in CI and is not run until the source-free implementation is merged.
- Every feature-branch commit for this work uses the `[phase1-no-source]` prefix.

---

## File Structure

- `mt5/FMPPhase8QuoteBridge.mq5` — read-only EA; validates demo/server/symbol, fingerprints account login locally, emits fixed JSONL protocol.
- `src/fmp/shadow/mt5_bridge.py` — MT5 bridge constants, start/session types, fixed macOS transport discovery, strict line parsing, no-backfill file reader.
- `src/fmp/shadow/normalization.py` — stateful MT5 session/tick normalization and duplicate/source-time integrity.
- `src/fmp/shadow/qualification.py` — bounded 10-minute bridge qualification with separate bridge/market liveness.
- `src/fmp/shadow/runner.py` — bridge binding, polling event loop, two liveness dimensions, existing downstream bars/strategy/simulator reuse.
- `src/fmp/shadow/evidence.py` — evidence v2 connector/session/server/source identity.
- `src/fmp/shadow/campaign.py` — amended registration identity and mixed-connector rejection.
- `src/fmp/shadow/replay.py` — replay bridge start + raw MT5 records through the same runtime pipeline.
- `src/fmp/shadow/review_compiler.py` — v2 manifest/campaign identity validation.
- `src/fmp/shadow/cli.py` — credential-free local `qualify`/`run`; no arbitrary bridge path option.
- `tests/phase8_helpers.py` — shared canonical MT5 bridge test records/bindings.
- `tests/test_phase8_mt5_bridge.py` — parser/discovery/tailer/no-backfill tests.
- Existing Phase 8 tests — amended in place for v2/provider semantics.
- `docs/phase8-mt5-operator-runbook.md` — one-time macOS/MetaEditor installation and explicit qualification/capture handoff.

---

### Task 1: Activate the approved connector amendment in source of truth

**Files:**
- Modify: `docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md`
- Modify: `docs/decision-log.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Modify: `docs/source-register.md`
- Modify: `tests/test_phase8_protocol_state.py`

**Interfaces:**
- Consumes: approved amendment spec and existing DEC-036 / EXP-20260915-009 state.
- Produces: active DEC-037 / EXP-20260917-010 source-of-truth identity for all later runtime tasks.

- [ ] **Step 1: Rewrite the protocol-state test first**

Replace OANDA-specific expectations with exact amended identities:

```python
EXPECTED_PHASE7_TAG = "fmp-v1-phase7-walk-forward"
EXPECTED_PHASE7_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
STOPPED_EXPERIMENT = "EXP-20260915-009"
ACTIVE_EXPERIMENT = "EXP-20260917-010"
ACTIVE_DECISION = "DEC-037"
CONNECTOR_PROTOCOL = "fmp-mt5-demo-file-bridge-v1"
PROVIDER = "FP_MARKETS_MT5_DEMO"
ALLOWED_SERVERS = ("FPMarketsSC-Demo", "FPMarketsSC-Demo2")


def test_phase8_source_of_truth_uses_mt5_demo_and_execution_remains_locked():
    decision_log = Path("docs/decision-log.md").read_text(encoding="utf-8")
    experiment_log = Path("docs/experiment-log.md").read_text(encoding="utf-8")
    state = Path("docs/project-state.md").read_text(encoding="utf-8")
    sources = Path("docs/source-register.md").read_text(encoding="utf-8")
    amendment = Path(
        "docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md"
    ).read_text(encoding="utf-8")

    assert ACTIVE_DECISION in decision_log
    assert STOPPED_EXPERIMENT in experiment_log
    assert "Status: STOPPED" in experiment_log
    assert ACTIVE_EXPERIMENT in experiment_log
    assert "Status: RUNNING" in experiment_log
    assert CONNECTOR_PROTOCOL in state
    assert PROVIDER in state
    for server in ALLOWED_SERVERS:
        assert server in state
    assert EXPECTED_PHASE7_TAG in state
    assert EXPECTED_PHASE7_SHA in state
    assert "mql5.com/en/docs/event_handlers/ontick" in sources
    assert "mql5.com/en/docs/files/fileopen" in sources
    assert "mql5.com/en/docs/common/cryptencode" in sources
    assert "APPROVED / ACTIVATED" in amendment
    assert "Phase 9/demo order placement: LOCKED" in state
    assert "production/live order placement and broker mutation: LOCKED" in state
    assert "Real-money trading: locked" in state
```

- [ ] **Step 2: Run the state test and confirm RED**

Run:

```bash
pytest -q tests/test_phase8_protocol_state.py
```

Expected: FAIL because DEC-037 / EXP-20260917-010 and amended connector state are not yet activated in source-of-truth docs.

- [ ] **Step 3: Update source-of-truth docs**

Record exactly:

```text
DEC-037 — Replace unavailable OANDA Practice connector with read-only FP Markets MT5 demo quote bridge — APPROVED
EXP-20260915-009 — Status: STOPPED; reason: connector unavailable before qualification because required OANDA account is unavailable in operator jurisdiction; no scored campaign evidence exists.
EXP-20260917-010 — Status: RUNNING; Phase 8 MT5 demo live-shadow evaluation.
Phase 8 — ACTIVE
Connector protocol — fmp-mt5-demo-file-bridge-v1
Provider — FP_MARKETS_MT5_DEMO
Allowed servers — FPMarketsSC-Demo, FPMarketsSC-Demo2
Phase 9/demo order placement — LOCKED
production/live order placement and broker mutation — LOCKED
Real-money trading — locked
```

Change the amendment header to:

```markdown
**Status:** APPROVED / ACTIVATED — DEC-037; Phase 8 ACTIVE under amended connector
```

Add the official MQL5 source-register references used by the amendment: `OnTick`, `MqlTick`, `FileOpen`, `FileFlush`, `CryptEncode`, `OnTimer`, and `EventSetTimer`, with reverification date `2026-09-17`.

- [ ] **Step 4: Run the state test and full source-state regression**

Run:

```bash
pytest -q tests/test_phase8_protocol_state.py tests/test_phase7_acceptance_state.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md \
  docs/decision-log.md docs/experiment-log.md docs/project-state.md \
  docs/source-register.md tests/test_phase8_protocol_state.py
git commit -m "[phase1-no-source] Activate Phase 8 MT5 bridge amendment"
```

---

### Task 2: Add the read-only MQL5 bridge and structural guard

**Files:**
- Create: `mt5/FMPPhase8QuoteBridge.mq5`
- Modify: `tests/test_phase8_structural_safety.py`

**Interfaces:**
- Consumes: DEC-037 fixed protocol/file/server/symbol values.
- Produces: static read-only EA source emitting the three-record bridge protocol.

- [ ] **Step 1: Add failing MQL5 structural tests**

Add constants and tests:

```python
EA_PATH = Path(__file__).resolve().parents[1] / "mt5" / "FMPPhase8QuoteBridge.mq5"
MQL5_FORBIDDEN = (
    "OrderSend",
    "OrderSendAsync",
    "MqlTradeRequest",
    "MqlTradeResult",
    "CTrade",
    "PositionOpen",
    "PositionClose",
    "PositionModify",
    "<Trade/Trade.mqh>",
)
MQL5_REQUIRED = (
    "ACCOUNT_TRADE_MODE_DEMO",
    '"USDJPY"',
    '"FPMarketsSC-Demo"',
    '"FPMarketsSC-Demo2"',
    '"FMP\\\\phase8-usdjpy-feed.jsonl"',
    '"fmp-mt5-demo-file-bridge-v1"',
    '"BRIDGE_START"',
    '"TICK"',
    '"BRIDGE_HEARTBEAT"',
    "CRYPT_HASH_SHA256",
    "FILE_COMMON",
    "FileFlush",
    "EventSetTimer(5)",
)


def test_mql5_bridge_has_read_only_surface():
    source = EA_PATH.read_text(encoding="utf-8")
    for forbidden in MQL5_FORBIDDEN:
        assert forbidden not in source
    for required in MQL5_REQUIRED:
        assert required in source
    assert "FPMarketsSC-Live" not in source
    assert "FPMarketsSC-Live2" not in source
```

Also keep the Python runtime AST guard that rejects `MetaTrader5`, `mt5`, and public mutation method names.

- [ ] **Step 2: Run the structural test and confirm RED**

```bash
pytest -q tests/test_phase8_structural_safety.py
```

Expected: FAIL because the EA file does not exist.

- [ ] **Step 3: Implement the minimal EA source**

The implementation must use these fixed constants and event handlers:

```cpp
#property strict

#define BRIDGE_PROTOCOL "fmp-mt5-demo-file-bridge-v1"
#define BRIDGE_FILE "FMP\\phase8-usdjpy-feed.jsonl"
#define BRIDGE_SYMBOL "USDJPY"

int g_file = INVALID_HANDLE;
string g_server = "";
string g_fingerprint = "";
string g_session_id = "";
long g_last_tick_msc = 0;

bool AllowedServer(const string server)
{
   return server == "FPMarketsSC-Demo" || server == "FPMarketsSC-Demo2";
}

string Sha256Hex(const string text)
{
   uchar data[], key[], digest[];
   int count = StringToCharArray(text, data, 0, WHOLE_ARRAY, CP_UTF8);
   if(count <= 1) return "";
   ArrayResize(data, count - 1);
   ArrayResize(key, 0);
   if(CryptEncode(CRYPT_HASH_SHA256, data, key, digest) != 32) return "";
   string result = "";
   for(int i = 0; i < ArraySize(digest); i++)
      result += StringFormat("%02X", digest[i]);
   StringToLower(result);
   return result;
}

long AuditTimeMs()
{
   return ((long)TimeGMT()) * 1000;
}

void WriteRecord(const string line)
{
   if(g_file == INVALID_HANDLE) return;
   FileSeek(g_file, 0, SEEK_END);
   FileWriteString(g_file, line + "\n");
   FileFlush(g_file);
}

int OnInit()
{
   if((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
      return INIT_FAILED;
   if(_Symbol != BRIDGE_SYMBOL)
      return INIT_FAILED;
   g_server = AccountInfoString(ACCOUNT_SERVER);
   if(!AllowedServer(g_server))
      return INIT_FAILED;

   string login = IntegerToString((long)AccountInfoInteger(ACCOUNT_LOGIN));
   g_fingerprint = Sha256Hex(login);
   login = "";
   if(StringLen(g_fingerprint) != 64)
      return INIT_FAILED;

   g_session_id = Sha256Hex(g_fingerprint + "|" + g_server + "|" +
                            IntegerToString(AuditTimeMs()) + "|" +
                            IntegerToString((long)GetTickCount64()));
   if(StringLen(g_session_id) != 64)
      return INIT_FAILED;

   FileDelete(BRIDGE_FILE, FILE_COMMON);
   g_file = FileOpen(BRIDGE_FILE,
      FILE_READ|FILE_WRITE|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_COMMON,
      0,
      CP_UTF8);
   if(g_file == INVALID_HANDLE)
      return INIT_FAILED;

   WriteRecord(StringFormat(
      "{\"protocol\":\"%s\",\"record_type\":\"BRIDGE_START\",\"bridge_session_id\":\"%s\",\"symbol\":\"%s\",\"account_mode\":\"DEMO\",\"server\":\"%s\",\"account_fingerprint_sha256\":\"%s\",\"audit_time_ms\":%I64d}",
      BRIDGE_PROTOCOL, g_session_id, BRIDGE_SYMBOL, g_server, g_fingerprint, AuditTimeMs()));

   if(!EventSetTimer(5))
      return INIT_FAILED;
   return INIT_SUCCEEDED;
}

void OnTick()
{
   MqlTick tick;
   if(!SymbolInfoTick(BRIDGE_SYMBOL, tick)) return;
   if(!MathIsValidNumber(tick.bid) || !MathIsValidNumber(tick.ask)) return;
   if(tick.bid <= 0.0 || tick.ask <= 0.0 || tick.bid > tick.ask) return;
   g_last_tick_msc = tick.time_msc;
   WriteRecord(StringFormat(
      "{\"protocol\":\"%s\",\"record_type\":\"TICK\",\"bridge_session_id\":\"%s\",\"symbol\":\"%s\",\"source_time_msc\":%I64d,\"bid\":%s,\"ask\":%s,\"flags\":%u,\"server\":\"%s\",\"account_fingerprint_sha256\":\"%s\"}",
      BRIDGE_PROTOCOL, g_session_id, BRIDGE_SYMBOL, tick.time_msc,
      DoubleToString(tick.bid, _Digits), DoubleToString(tick.ask, _Digits),
      tick.flags, g_server, g_fingerprint));
}

void OnTimer()
{
   string last_tick = g_last_tick_msc > 0 ? IntegerToString(g_last_tick_msc) : "null";
   WriteRecord(StringFormat(
      "{\"protocol\":\"%s\",\"record_type\":\"BRIDGE_HEARTBEAT\",\"bridge_session_id\":\"%s\",\"symbol\":\"%s\",\"audit_time_ms\":%I64d,\"server\":\"%s\",\"account_fingerprint_sha256\":\"%s\",\"last_tick_source_time_msc\":%s}",
      BRIDGE_PROTOCOL, g_session_id, BRIDGE_SYMBOL, AuditTimeMs(),
      g_server, g_fingerprint, last_tick));
}

void OnDeinit(const int reason)
{
   EventKillTimer();
   if(g_file != INVALID_HANDLE)
   {
      FileFlush(g_file);
      FileClose(g_file);
      g_file = INVALID_HANDLE;
   }
}
```

No trade include/import is added. Do not add inputs that allow symbol/server/path overrides.

- [ ] **Step 4: Run structural tests**

```bash
pytest -q tests/test_phase8_structural_safety.py
```

Expected: PASS. CI is a source-level safety proof only; MetaEditor compilation remains an operator precondition later.

- [ ] **Step 5: Commit**

```bash
git add mt5/FMPPhase8QuoteBridge.mq5 tests/test_phase8_structural_safety.py
git commit -m "[phase1-no-source] Add read-only MT5 quote bridge"
```

---

### Task 3: Implement fixed transport discovery, session binding, tailing, and normalization

**Files:**
- Create: `src/fmp/shadow/mt5_bridge.py`
- Create: `tests/phase8_helpers.py`
- Create: `tests/test_phase8_mt5_bridge.py`
- Modify: `src/fmp/shadow/normalization.py`
- Modify: `tests/test_phase8_normalization.py`
- Modify: `src/fmp/shadow/contracts.py`
- Modify: `tests/test_phase8_contracts.py`

**Interfaces:**
- Produces: `BridgeSessionBinding`, `BridgeHeartbeatEvent`, `BridgeFileReader`, `parse_bridge_line`, `normalize_bridge_start`, and a binding-aware `StreamSegmentNormalizer`.
- Later tasks consume these exact names.

- [ ] **Step 1: Add shared canonical bridge fixtures**

Create `tests/phase8_helpers.py` with deterministic records:

```python
from datetime import datetime, timezone

FINGERPRINT = "a" * 64
SESSION = "b" * 64
SERVER = "FPMarketsSC-Demo2"


def bridge_start() -> dict[str, object]:
    return {
        "protocol": "fmp-mt5-demo-file-bridge-v1",
        "record_type": "BRIDGE_START",
        "bridge_session_id": SESSION,
        "symbol": "USDJPY",
        "account_mode": "DEMO",
        "server": SERVER,
        "account_fingerprint_sha256": FINGERPRINT,
        "audit_time_ms": 1789650000000,
    }


def tick(*, source_time_msc: int = 1789650001000, bid: float = 146.100, ask: float = 146.102) -> dict[str, object]:
    return {
        "protocol": "fmp-mt5-demo-file-bridge-v1",
        "record_type": "TICK",
        "bridge_session_id": SESSION,
        "symbol": "USDJPY",
        "source_time_msc": source_time_msc,
        "bid": bid,
        "ask": ask,
        "flags": 6,
        "server": SERVER,
        "account_fingerprint_sha256": FINGERPRINT,
    }


def heartbeat(*, last_tick_source_time_msc: int | None = 1789650001000) -> dict[str, object]:
    return {
        "protocol": "fmp-mt5-demo-file-bridge-v1",
        "record_type": "BRIDGE_HEARTBEAT",
        "bridge_session_id": SESSION,
        "symbol": "USDJPY",
        "audit_time_ms": 1789650005000,
        "server": SERVER,
        "account_fingerprint_sha256": FINGERPRINT,
        "last_tick_source_time_msc": last_tick_source_time_msc,
    }
```

- [ ] **Step 2: Write failing parser/reader/normalizer tests**

Cover these exact behaviors in `tests/test_phase8_mt5_bridge.py` and `tests/test_phase8_normalization.py`:

```python
def test_reader_starts_at_eof_and_never_backfills_prior_ticks(tmp_path):
    path = make_bridge_file(tmp_path, [bridge_start(), tick(source_time_msc=1789650001000)])
    reader = BridgeFileReader(path=path)
    snapshot = reader.bind()
    assert snapshot.binding.bridge_session_id == SESSION
    assert reader.poll() == ()
    append_record(path, tick(source_time_msc=1789650002000))
    assert len(reader.poll()) == 1


def test_partial_final_line_waits_for_newline(tmp_path):
    path = make_bridge_file(tmp_path, [bridge_start()])
    reader = BridgeFileReader(path=path)
    reader.bind()
    with path.open("ab") as handle:
        handle.write(b'{"protocol":"fmp-mt5-demo-file-bridge-v1"')
    assert reader.poll() == ()


def test_heartbeat_never_normalizes_to_market_heartbeat():
    binding = normalize_bridge_start(bridge_start())
    normalizer = StreamSegmentNormalizer(binding=binding)
    event = normalizer.accept(
        heartbeat(),
        received_at_utc=datetime(2026, 9, 17, 12, 0, tzinfo=timezone.utc),
        receive_monotonic_ns=1,
    )
    assert isinstance(event, BridgeHeartbeatEvent)
    assert not isinstance(event, HeartbeatEvent)
```

Also test unknown record type, wrong protocol/symbol/server/session/fingerprint, live server, malformed JSON, non-finite/non-positive/crossed prices, source-time regression, exact duplicate returns `None`, conflicting duplicate raises `ProviderMessageError`, and reader session-file replacement/truncation fails closed.

For macOS discovery, inject a fake home and require exactly one non-symlink match under:

```text
~/Library/Application Support/*/drive_c/users/*/AppData/Roaming/MetaQuotes/Terminal/Common/Files/FMP/phase8-usdjpy-feed.jsonl
```

Zero or multiple matches must raise `Mt5BridgeUnavailableError`. Runtime discovery accepts no CLI path.

- [ ] **Step 3: Run focused tests and confirm RED**

```bash
pytest -q tests/test_phase8_mt5_bridge.py tests/test_phase8_normalization.py tests/test_phase8_contracts.py
```

Expected: FAIL because MT5 bridge types/reader do not exist yet.

- [ ] **Step 4: Implement exact public interfaces**

`src/fmp/shadow/mt5_bridge.py` exports:

```python
BRIDGE_PROTOCOL = "fmp-mt5-demo-file-bridge-v1"
BRIDGE_FILE = "FMP/phase8-usdjpy-feed.jsonl"
BRIDGE_SYMBOL = "USDJPY"
BRIDGE_PROVIDER = "FP_MARKETS_MT5_DEMO"
BRIDGE_TRANSPORT = "MT5_FILE_COMMON_JSONL"
ALLOWED_SERVERS = ("FPMarketsSC-Demo", "FPMarketsSC-Demo2")

class Mt5BridgeError(RuntimeError):
    pass

class Mt5BridgeUnavailableError(Mt5BridgeError):
    pass

@dataclass(frozen=True, slots=True)
class BridgeSessionBinding:
    protocol: str
    bridge_session_id: str
    symbol: str
    server: str
    account_fingerprint_sha256: str
    start_audit_time_utc: datetime

@dataclass(frozen=True, slots=True)
class BridgeHeartbeatEvent:
    emitted_at_utc: datetime
    received_at_utc: datetime
    receive_monotonic_ns: int
    last_tick_source_time_utc: datetime | None

@dataclass(frozen=True, slots=True)
class BridgeStartSnapshot:
    binding: BridgeSessionBinding
    provider_object: Mapping[str, object]
```

`parse_bridge_line(line: bytes) -> dict[str, object]` must decode strict UTF-8 JSON and require an object.

`normalize_bridge_start(raw: Mapping[str, object]) -> BridgeSessionBinding` requires exact protocol, `BRIDGE_START`, `USDJPY`, `DEMO`, allowed server, lowercase 64-hex session/fingerprint, and integer positive `audit_time_ms` converted from epoch milliseconds to UTC.

`resolve_bridge_file(*, home: Path | None = None, platform_name: str | None = None) -> Path` uses `Path.home()` / `sys.platform` by default, supports only `darwin`, searches the fixed suffix under `~/Library/Application Support`, rejects symlinks, and requires exactly one file.

`BridgeFileReader(path: Path | None = None)` may accept a path only as an internal/test constructor seam. Production CLI never exposes it. `bind()` reads/validates the first complete line as `BRIDGE_START`, stores its bytes and the current EOF offset, and returns `BridgeStartSnapshot`. `poll()` verifies the file still begins with the same start line, reads only complete lines after the stored offset, leaves a partial final line unconsumed, and raises on truncation/session replacement.

Rewrite `StreamSegmentNormalizer` construction to require `binding: BridgeSessionBinding`. Its `accept()` supports only `TICK` and `BRIDGE_HEARTBEAT`; it rejects a new `BRIDGE_START` mid-segment. `TICK` returns existing `NormalizedQuote(symbol="USDJPY", tradeable=True, ...)`. `BRIDGE_HEARTBEAT` returns `BridgeHeartbeatEvent` and never `HeartbeatEvent`.

Update `PHASE8_EXPERIMENT_ID` in `contracts.py` to `EXP-20260917-010`; remove active OANDA provider constants from new call sites but defer deleting `oanda.py` until Task 8.

- [ ] **Step 5: Run focused tests**

```bash
pytest -q tests/test_phase8_mt5_bridge.py tests/test_phase8_normalization.py tests/test_phase8_contracts.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/fmp/shadow/mt5_bridge.py src/fmp/shadow/normalization.py \
  src/fmp/shadow/contracts.py tests/phase8_helpers.py \
  tests/test_phase8_mt5_bridge.py tests/test_phase8_normalization.py \
  tests/test_phase8_contracts.py
git commit -m "[phase1-no-source] Parse and tail MT5 bridge records"
```

---

### Task 4: Replace OANDA qualification with bounded MT5 bridge qualification

**Files:**
- Modify: `src/fmp/shadow/qualification.py`
- Modify: `src/fmp/shadow/cli.py`
- Modify: `tests/test_phase8_qualification.py`
- Modify: `tests/test_phase8_cli.py`

**Interfaces:**
- Consumes: `BridgeFileReader`, `BridgeStartSnapshot`, `StreamSegmentNormalizer`.
- Produces: `qualify_bridge(reader, utc_now, monotonic_ns, sleep) -> QualificationResult` and credential-free CLI qualification.

- [ ] **Step 1: Rewrite qualification tests first**

Use a fake reader with `bind()` and `poll()` and injected clocks. Require:

```python
def test_qualification_pass_requires_100_ticks_and_6_bridge_heartbeats():
    result = qualify_bridge(
        reader=FakeReader(start=bridge_start(), batches=qualification_batches()),
        utc_now=clock.utc_now,
        monotonic_ns=clock.monotonic_ns,
        sleep=clock.sleep,
    )
    assert result.outcome is QualificationOutcome.PASS
    assert result.price_count == 100
    assert result.heartbeat_count == 6
    assert result.boundary_audit["connector_protocol"] == "fmp-mt5-demo-file-bridge-v1"
    assert result.boundary_audit["provider"] == "FP_MARKETS_MT5_DEMO"
    assert result.boundary_audit["transport"] == "MT5_FILE_COMMON_JSONL"
```

Add cases:
- bridge liveness >15s -> `CONNECTOR_REJECTED` / `BRIDGE_LIVENESS_GAP`;
- heartbeats continue but no tick for >15s -> `INCONCLUSIVE` / `MARKET_FEED_GAP`;
- missing/inaccessible file -> `CONNECTOR_UNAVAILABLE`;
- malformed/identity/source-time conflict -> `CONNECTOR_REJECTED`;
- timeout at 600s without minima -> `INCONCLUSIVE`;
- records before bind EOF do not count.

CLI tests must prove `qualify` and `run` require no OANDA environment variables and expose no `--bridge-path`, `--server`, `--symbol`, or generic provider override.

- [ ] **Step 2: Run tests and confirm RED**

```bash
pytest -q tests/test_phase8_qualification.py tests/test_phase8_cli.py
```

- [ ] **Step 3: Implement qualification polling**

Keep:

```python
MAX_QUALIFICATION_SECONDS = 600.0
MIN_PRICE_COUNT = 100
MIN_HEARTBEAT_COUNT = 6
```

Implement `qualify_bridge` with this state model:

```python
snapshot = reader.bind()
binding = snapshot.binding
normalizer = StreamSegmentNormalizer(binding=binding)
started_at_utc = utc_now()
started_ns = monotonic_ns()
last_bridge_ns = started_ns
last_tick_ns = started_ns
price_count = 0
heartbeat_count = 0

while True:
    now_ns = monotonic_ns()
    elapsed = (now_ns - started_ns) / 1_000_000_000
    if elapsed >= MAX_QUALIFICATION_SECONDS:
        return finish(QualificationOutcome.INCONCLUSIVE)

    lines = reader.poll()
    if not lines:
        bridge_gap = (now_ns - last_bridge_ns) / 1_000_000_000
        market_gap = (now_ns - last_tick_ns) / 1_000_000_000
        if bridge_gap > LIVENESS_TIMEOUT_SECONDS:
            return finish(QualificationOutcome.CONNECTOR_REJECTED, codes=("BRIDGE_LIVENESS_GAP",))
        if market_gap > LIVENESS_TIMEOUT_SECONDS:
            return finish(QualificationOutcome.INCONCLUSIVE, codes=("MARKET_FEED_GAP",))
        sleep(0.1)
        continue
```

For each complete line: strict parse, normalize with receive UTC/monotonic metadata, update `last_bridge_ns` for every valid tick/heartbeat, update `last_tick_ns` only for `NormalizedQuote`, count `BridgeHeartbeatEvent` separately, and PASS only at 100/6 with both gaps <=15s.

`boundary_audit` must include connector protocol/provider/transport/bridge file/allowed servers/actual server/session id and must contain no plain account login.

- [ ] **Step 4: Make CLI credential-free and path-fixed**

Delete `_ACCOUNT_ENV`, `_TOKEN_ENV`, OANDA credential checks, and `stream_factory`. Add injectable `reader_factory: Callable[[], BridgeFileReader] = BridgeFileReader`. `qualify` becomes:

```python
reader = reader_factory()
result = qualify_bridge(
    reader=reader,
    utc_now=now,
    monotonic_ns=mono,
    sleep=sleep_fn,
)
_write_json(Path(args.out) / "qualification.json", result.to_record())
```

No user-supplied bridge path/server/symbol/provider arguments are added.

- [ ] **Step 5: Run focused tests**

```bash
pytest -q tests/test_phase8_qualification.py tests/test_phase8_cli.py tests/test_phase8_mt5_bridge.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/fmp/shadow/qualification.py src/fmp/shadow/cli.py \
  tests/test_phase8_qualification.py tests/test_phase8_cli.py
git commit -m "[phase1-no-source] Qualify the MT5 demo quote bridge"
```

---

### Task 5: Feed MT5 records through the existing shadow runner with two liveness dimensions

**Files:**
- Modify: `src/fmp/shadow/runner.py`
- Modify: `tests/test_phase8_runner.py`
- Modify: `tests/test_phase8_processing_latency.py`
- Modify: `tests/test_phase8_restart_state.py`

**Interfaces:**
- Consumes: binding-aware normalizer/reader and existing `LiveBarBuilder`, strategy adapter, simulator.
- Produces: `ShadowRunner.bind_bridge_start`, `ShadowRunner.process_bridge_record`, MT5-based `run_live_shadow_capture`.

- [ ] **Step 1: Write runner tests for binding and heartbeat isolation**

Add tests equivalent to:

```python
def test_bridge_heartbeat_does_not_advance_bars_or_market_time():
    runner, evidence = make_runner()
    runner.start(now_utc=T0, restarted=False)
    runner.bind_bridge_start(bridge_start(), received_at_utc=T0, receive_monotonic_ns=0)
    runner.process_bridge_record(heartbeat(), received_at_utc=T0_PLUS_5, receive_monotonic_ns=5_000_000_000)
    assert evidence.bars == []
    assert runner.last_tick_source_time is None


def test_market_stale_occurs_even_while_bridge_heartbeats_continue():
    runner, evidence = make_runner()
    runner.start(now_utc=T0, restarted=False)
    runner.bind_bridge_start(bridge_start(), received_at_utc=T0, receive_monotonic_ns=0)
    runner.process_bridge_record(tick(), received_at_utc=T1, receive_monotonic_ns=1_000_000_000)
    runner.process_bridge_record(heartbeat(), received_at_utc=T10, receive_monotonic_ns=10_000_000_000)
    assert runner.check_liveness(now_utc=T17, now_monotonic_ns=17_000_000_000)
    assert evidence.operational[-1]["reason"] == "market_feed_liveness"
```

Also require:
- bridge gap stale reason `bridge_liveness`;
- a heartbeat cannot recover a stale market feed;
- first valid tick after stale may record recovery but date stays ineligible;
- start/restart identity mismatch fails;
- processing latency is recorded only for normalized ticks;
- operator stop (`KeyboardInterrupt`) finalizes disconnect cleanly as `operator_stop`;
- reader/parse/integrity failure returns code 4 and records rejection;
- no backfill/reconciliation call exists.

- [ ] **Step 2: Run runner tests and confirm RED**

```bash
pytest -q tests/test_phase8_runner.py tests/test_phase8_processing_latency.py tests/test_phase8_restart_state.py
```

- [ ] **Step 3: Refactor `ShadowRunner` around bridge binding**

Constructor requires `bridge_binding: BridgeSessionBinding` and initializes:

```python
self.normalizer = StreamSegmentNormalizer(binding=bridge_binding)
self.bridge_binding = bridge_binding
self._bridge_bound = False
self._last_bridge_monotonic_ns: int | None = None
self._last_tick_monotonic_ns: int | None = None
self._last_tick_source_time: datetime | None = None
```

Add:

```python
def bind_bridge_start(self, raw, *, received_at_utc, receive_monotonic_ns):
    binding = normalize_bridge_start(raw)
    if binding != self.bridge_binding:
        raise ProviderMessageError("bridge start identity mismatch")
    if self._bridge_bound:
        raise ProviderMessageError("bridge start already bound")
    self._bridge_bound = True
    self._last_bridge_monotonic_ns = receive_monotonic_ns
    self.evidence.append_raw(raw, received_at_utc=received_at_utc, receive_monotonic_ns=receive_monotonic_ns)
    self.evidence.append_operational({
        "event": "bridge_session_bound",
        "timestamp_utc": received_at_utc,
        "bridge_session_id": binding.bridge_session_id,
        "server": binding.server,
    })
```

Rename live input handling to `process_bridge_record`. It must append every accepted tick/heartbeat raw record; append normalized evidence/bar/simulator work only for `NormalizedQuote`; append heartbeat operational evidence only for `BridgeHeartbeatEvent`.

`check_liveness` computes bridge and tick gaps independently. Either reaching 15 seconds during capture calls `_mark_stale` with explicit reason. Recovery requires a valid tick, never a heartbeat.

- [ ] **Step 4: Rewrite `run_live_shadow_capture` as a polling loop**

New signature:

```python
def run_live_shadow_capture(
    *,
    campaign_dir: Path,
    code_commit: str,
    utc_now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    sleep: Callable[[float], None] = time.sleep,
    reader_factory: Callable[[], BridgeFileReader] = BridgeFileReader,
) -> int:
```

Sequence:
1. validate campaign registration;
2. `reader = reader_factory(); snapshot = reader.bind()`;
3. construct evidence using snapshot binding;
4. restore simulator if restart;
5. start runner and bind the `BRIDGE_START` snapshot;
6. poll every 0.1 seconds, parse complete lines, process each record, and call `check_liveness` even on empty polls;
7. `KeyboardInterrupt` -> clean `operator_stop` disconnect/return 0;
8. bridge/parser/integrity error -> rejection/disconnect/return 4.

Do not spawn threads, daemonize, or auto-start MT5.

- [ ] **Step 5: Run runner regression**

```bash
pytest -q tests/test_phase8_runner.py tests/test_phase8_processing_latency.py \
  tests/test_phase8_restart_state.py tests/test_phase8_bars.py tests/test_phase8_simulation.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/fmp/shadow/runner.py tests/test_phase8_runner.py \
  tests/test_phase8_processing_latency.py tests/test_phase8_restart_state.py
git commit -m "[phase1-no-source] Run shadow capture from MT5 bridge ticks"
```

---

### Task 6: Bump evidence/campaign identity to MT5 v2 without changing acceptance thresholds

**Files:**
- Modify: `src/fmp/shadow/evidence.py`
- Modify: `src/fmp/shadow/campaign.py`
- Modify: `tests/test_phase8_evidence.py`
- Modify: `tests/test_phase8_campaign.py`
- Modify: `tests/test_phase8_campaign_registration_guard.py`
- Modify: `tests/test_phase8_campaign_risk_identity.py`

**Interfaces:**
- Consumes: `BridgeSessionBinding`, fixed connector constants, EA source digest.
- Produces: v2 segment manifests and v2 immutable campaign registration.

- [ ] **Step 1: Write failing v2 identity tests**

Require segment manifest values:

```python
assert manifest["protocol"] == "fmp-phase8-shadow-evidence-v2"
assert manifest["connector_protocol"] == "fmp-mt5-demo-file-bridge-v1"
assert manifest["connector_boundary"] == {
    "provider": "FP_MARKETS_MT5_DEMO",
    "provider_instrument": "USDJPY",
    "transport": "MT5_FILE_COMMON_JSONL",
    "bridge_file": "FMP/phase8-usdjpy-feed.jsonl",
    "allowed_servers": ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
}
assert manifest["bridge_session_id"] == SESSION
assert manifest["provider_server"] == SERVER
assert manifest["account_fingerprint_sha256"] == FINGERPRINT
assert len(manifest["bridge_source_sha256"]) == 64
for key in ("practice_host", "host", "path_template", "snapshot", "include_home_conversions"):
    assert key not in manifest
```

Campaign registration must contain connector protocol/provider/transport/file/allowed servers and bridge source SHA-256, but no OANDA host/path fields. Existing threshold/risk/slippage assertions remain byte-for-byte unchanged in meaning.

Add a guard that an existing registration with another connector protocol cannot be reused.

- [ ] **Step 2: Run tests and confirm RED**

```bash
pytest -q tests/test_phase8_evidence.py tests/test_phase8_campaign.py \
  tests/test_phase8_campaign_registration_guard.py tests/test_phase8_campaign_risk_identity.py
```

- [ ] **Step 3: Implement evidence v2 and source digest**

Set:

```python
EVIDENCE_PROTOCOL = "fmp-phase8-shadow-evidence-v2"
CONNECTOR_PROTOCOL = "fmp-mt5-demo-file-bridge-v1"
```

Add `bridge_source_sha256()` in `mt5_bridge.py` that hashes repository file `mt5/FMPPhase8QuoteBridge.mq5` resolved from the package's repository root and fails if missing.

Change `EvidenceWriter` constructor to require:

```python
connector_binding: BridgeSessionBinding
bridge_source_sha256: str
```

Preserve compatibility attributes used by runner/replay:

```python
self.account_fingerprint_sha256 = connector_binding.account_fingerprint_sha256
self.bridge_session_id = connector_binding.bridge_session_id
self.provider_server = connector_binding.server
```

Build the v2 manifest exactly from fixed connector constants plus actual session/server/fingerprint/source digest. Keep all Phase 7 identity, strategy, risk, slippage, file-hash, replay digest, and run-time fields.

- [ ] **Step 4: Amend campaign registration identity**

`register_campaign` stores:

```python
"phase8_experiment": "EXP-20260917-010",
"provider": "FP_MARKETS_MT5_DEMO",
"connector_protocol": "fmp-mt5-demo-file-bridge-v1",
"provider_instrument": "USDJPY",
"transport": "MT5_FILE_COMMON_JSONL",
"bridge_file": "FMP/phase8-usdjpy-feed.jsonl",
"allowed_servers": ["FPMarketsSC-Demo", "FPMarketsSC-Demo2"],
"bridge_source_sha256": bridge_source_sha256(),
```

Remove active registration requirements for OANDA host/path. `load_campaign_registration` validates all fixed connector fields and unchanged thresholds/risk identity. Do not allow a v1/OANDA registration to be used by MT5 capture.

- [ ] **Step 5: Run evidence/campaign tests**

```bash
pytest -q tests/test_phase8_evidence.py tests/test_phase8_campaign.py \
  tests/test_phase8_campaign_registration_guard.py tests/test_phase8_campaign_risk_identity.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/fmp/shadow/evidence.py src/fmp/shadow/campaign.py src/fmp/shadow/mt5_bridge.py \
  tests/test_phase8_evidence.py tests/test_phase8_campaign.py \
  tests/test_phase8_campaign_registration_guard.py tests/test_phase8_campaign_risk_identity.py
git commit -m "[phase1-no-source] Bind Phase 8 evidence to MT5 bridge v2"
```

---

### Task 7: Replay and review MT5 bridge evidence deterministically

**Files:**
- Modify: `src/fmp/shadow/replay.py`
- Modify: `src/fmp/shadow/review_compiler.py`
- Modify: `tests/test_phase8_replay.py`
- Modify: `tests/test_phase8_review_compiler.py`
- Modify: `tests/test_phase8_review_aggregation.py`
- Modify: `tests/test_phase8_review_compiler_wiring.py`

**Interfaces:**
- Consumes: raw v2 bridge records, binding-aware runner, v2 manifest/registration.
- Produces: deterministic v2 replay and compiler rejection of mixed/forged connector identities.

- [ ] **Step 1: Rewrite replay tests around `BRIDGE_START` + MT5 records**

Require `raw.jsonl` first accepted bridge object to be `BRIDGE_START`, followed by MT5 ticks/heartbeats. Add:

```python
def test_replay_rebuilds_same_semantic_files_from_mt5_raw_records(tmp_path):
    segment = build_mt5_segment(tmp_path)
    result = replay_segment(segment)
    assert result["match"] is True
    assert result["protocol"] == "fmp-phase8-shadow-replay-v2"
```

A forged session/server/fingerprint, mixed OANDA v1 manifest, or missing start binding must fail.

- [ ] **Step 2: Run replay/review tests and confirm RED**

```bash
pytest -q tests/test_phase8_replay.py tests/test_phase8_review_compiler.py \
  tests/test_phase8_review_aggregation.py tests/test_phase8_review_compiler_wiring.py
```

- [ ] **Step 3: Implement v2 replay binding**

Set:

```python
REPLAY_PROTOCOL = "fmp-phase8-shadow-replay-v2"
```

Replay must:
1. read raw + operational records;
2. extract the first raw provider object and require `BRIDGE_START`;
3. `binding = normalize_bridge_start(start_object)`;
4. construct `EvidenceWriter` with that binding and the bridge source digest recorded by the live manifest/registration;
5. `runner.start(...)` then `runner.bind_bridge_start(...)`;
6. feed only remaining raw provider records via `process_bridge_record` using persisted receive UTC/monotonic metadata;
7. compare the same derived semantic files and finalize v2 manifest.

Do not synthesize broker history or missing ticks.

- [ ] **Step 4: Make review compiler enforce v2 campaign identity**

Manifest validation must require:

```python
manifest["protocol"] == "fmp-phase8-shadow-evidence-v2"
manifest["connector_protocol"] == registration["connector_protocol"]
manifest["connector_boundary"]["provider"] == "FP_MARKETS_MT5_DEMO"
manifest["connector_boundary"]["transport"] == "MT5_FILE_COMMON_JSONL"
manifest["provider_server"] in registration["allowed_servers"]
manifest["bridge_source_sha256"] == registration["bridge_source_sha256"]
```

Reject mixed connector/evidence protocols as safety/integrity failure. Preserve financial, spread, date-coverage, latency, quote-deadline, provider-closure, and sample-minimum calculations unchanged.

- [ ] **Step 5: Run replay/review regression**

```bash
pytest -q tests/test_phase8_replay.py tests/test_phase8_review_compiler.py \
  tests/test_phase8_review_aggregation.py tests/test_phase8_review_compiler_wiring.py \
  tests/test_phase8_review_spread_precision.py tests/test_phase8_gates.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/fmp/shadow/replay.py src/fmp/shadow/review_compiler.py \
  tests/test_phase8_replay.py tests/test_phase8_review_compiler.py \
  tests/test_phase8_review_aggregation.py tests/test_phase8_review_compiler_wiring.py
git commit -m "[phase1-no-source] Replay and review MT5 bridge evidence"
```

---

### Task 8: Retire the OANDA live runtime and harden the final no-order surface

**Files:**
- Delete: `src/fmp/shadow/oanda.py`
- Delete: `tests/test_phase8_oanda.py`
- Modify: `src/fmp/shadow/contracts.py`
- Modify: `src/fmp/shadow/__init__.py`
- Modify: `tests/test_phase8_structural_safety.py`
- Modify: all Phase 8 imports/tests still referencing OANDA runtime constants

**Interfaces:**
- Consumes: fully migrated MT5 runtime from Tasks 3–7.
- Produces: exactly one active live connector runtime, with no OANDA HTTP transport and no MT5 execution library.

- [ ] **Step 1: Extend the structural guard before deleting legacy code**

Require:

```python
RUNTIME_FORBIDDEN_IMPORT_PARTS = ("metatrader5", "mt5", "broker")
RUNTIME_FORBIDDEN_PUBLIC_NAMES = (
    "order_send", "send_order", "submit_order", "place_order", "create_order",
    "cancel_order", "replace_order", "close_trade", "close_position",
    "modify_trade", "modify_position",
)


def test_active_phase8_runtime_has_no_oanda_transport_or_execution_adapter():
    assert not (RUNTIME_ROOT / "oanda.py").exists()
    for path, tree in _runtime_trees().items():
        imports = imported_modules(tree)
        for module in imports:
            lowered = module.lower().replace("-", "_")
            assert "metatrader5" not in lowered
            assert ".mt5" not in lowered
        assert _public_mutation_names(tree) == ()
```

Keep the MQL5 source scan from Task 2.

- [ ] **Step 2: Run the structural guard and confirm it fails while OANDA remains**

```bash
pytest -q tests/test_phase8_structural_safety.py
```

- [ ] **Step 3: Delete OANDA runtime and remove legacy active constants/imports**

Delete `src/fmp/shadow/oanda.py` and `tests/test_phase8_oanda.py`. Remove `PRACTICE_STREAM_HOST`, `PRACTICE_STREAM_PATH_TEMPLATE`, OANDA `PROVIDER_INSTRUMENT`, OANDA parser/stream imports, OANDA env names, and any active OANDA connector export from `src/fmp/shadow/__init__.py`.

Historical docs/specs may continue to mention OANDA as the stopped connector attempt; runtime code must not expose it as a fallback.

- [ ] **Step 4: Run every Phase 8 test**

```bash
pytest -q tests/test_phase8_*.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -A src/fmp/shadow tests/test_phase8_*.py
git commit -m "[phase1-no-source] Retire unavailable OANDA shadow runtime"
```

---

### Task 9: Add the macOS operator handoff and pin implemented commands

**Files:**
- Create: `docs/phase8-mt5-operator-runbook.md`
- Modify: `tests/test_phase8_operator_handoff.py`
- Modify: `src/fmp/shadow/cli.py` only if the implemented help text does not match the runbook

**Interfaces:**
- Produces: copy/compile/attach/qualify/run steps with no secrets and no arbitrary connector settings.

- [ ] **Step 1: Rewrite the operator-handoff test**

The test reads the new runbook and requires these exact commands:

```python
text = Path("docs/phase8-mt5-operator-runbook.md").read_text(encoding="utf-8")
assert "python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification" in text
assert "python scripts/phase8_shadow.py run --campaign-dir evidence/phase8/campaign" in text
assert "python scripts/phase8_shadow.py review --campaign-dir evidence/phase8/campaign" in text
assert "OANDA_PRACTICE_ACCOUNT_ID" not in text
assert "OANDA_PRACTICE_TOKEN" not in text
assert "--bridge-path" not in text
assert "AutoTrading: OFF" in text
assert "FPMarketsSC-Demo" in text
assert "FPMarketsSC-Demo2" in text
```

- [ ] **Step 2: Run test and confirm RED**

```bash
pytest -q tests/test_phase8_operator_handoff.py
```

- [ ] **Step 3: Write the runbook**

It must contain these concrete operator steps:

```text
1. MT5 account: FP Markets DEMO only; server FPMarketsSC-Demo or FPMarketsSC-Demo2.
2. Confirm USDJPY quotes are changing.
3. AutoTrading: OFF.
4. In MT5: File -> Open Data Folder -> MQL5 -> Experts.
5. Copy repository file mt5/FMPPhase8QuoteBridge.mq5 into MQL5/Experts.
6. Open MetaEditor, compile FMPPhase8QuoteBridge.mq5, require 0 errors.
7. Return to MT5, Navigator -> Expert Advisors -> Refresh.
8. Open USDJPY chart and attach FMPPhase8QuoteBridge.
9. Confirm Experts/Journal shows initialization success; do not enable AutoTrading.
10. Run: python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification
11. Inspect evidence/phase8/qualification/qualification.json; continue only on PASS.
12. Campaign capture remains explicit: python scripts/phase8_shadow.py run --campaign-dir evidence/phase8/campaign
13. Stop a capture with Ctrl-C; this records operator_stop.
14. Review remains offline: python scripts/phase8_shadow.py review --campaign-dir evidence/phase8/campaign
```

State that broker password/login is never entered into FMP or chat. Include the fixed FILE_COMMON logical identity but do not instruct the operator to hand-enter its Wine path.

- [ ] **Step 4: Run handoff/CLI tests**

```bash
pytest -q tests/test_phase8_operator_handoff.py tests/test_phase8_cli.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/phase8-mt5-operator-runbook.md tests/test_phase8_operator_handoff.py src/fmp/shadow/cli.py
git commit -m "[phase1-no-source] Document MT5 shadow operator handoff"
```

---

### Task 10: Full source-free verification and merge readiness

**Files:**
- No production change expected; fix only verified defects.

**Interfaces:**
- Produces: merge-ready source-free implementation. It does not produce live qualification evidence.

- [ ] **Step 1: Run all Phase 8 tests**

```bash
pytest -q tests/test_phase8_*.py
```

Expected: PASS.

- [ ] **Step 2: Run the full Python suite**

```bash
pytest -q
```

Expected: all tests PASS.

- [ ] **Step 3: Validate YAML and Python compilation**

```bash
ruby scripts/validate_workflow_yaml.rb
python -m compileall -q src scripts tests
```

Expected: PASS.

- [ ] **Step 4: Regenerate Phase 3 deterministic acceptance evidence**

```bash
rm -rf /tmp/fmp-phase3-acceptance
python scripts/phase3_acceptance_fixture.py \
  --out /tmp/fmp-phase3-acceptance \
  --code-commit "$(git rev-parse HEAD)"
pytest -q tests/test_phase3_acceptance.py tests/test_phase3_acceptance_runner.py
```

Expected: PASS with unchanged Phase 3 semantics.

- [ ] **Step 5: Verify no Phase 1 acquisition path was invoked**

Do not run Phase 1 acquisition/smoke/full-history source commands as part of this implementation. On GitHub, confirm implementation push/PR checks contain no triggered Phase 1 acquisition run attributable to this branch.

- [ ] **Step 6: Verify connector source surface manually**

Run:

```bash
grep -RniE 'OrderSend|OrderSendAsync|MqlTradeRequest|MqlTradeResult|CTrade|PositionOpen|PositionClose|PositionModify|Trade/Trade\.mqh' mt5 src/fmp/shadow && exit 1 || true
grep -RniE '(^|[^A-Za-z])MetaTrader5([^A-Za-z]|$)|import mt5|from mt5' src/fmp/shadow && exit 1 || true
```

Expected: no matches.

- [ ] **Step 7: Create/update PR and require green checks before merge**

PR title:

```text
[phase1-no-source] Amend Phase 8 for read-only MT5 demo bridge
```

PR body must state:

```text
- Replaces unavailable OANDA Practice connector with FP Markets MT5 demo FILE_COMMON quote bridge.
- No order/trade/position mutation surface exists in MQL5 or Python runtime.
- MT5 AutoTrading remains OFF.
- Strategy, virtual simulator, thresholds, and review outcomes are unchanged.
- Live qualification is not run in CI and remains an explicit post-merge operator step.
- Phase 9 and real-money trading remain locked.
```

Do not tag `fmp-v1-phase8-shadow` at implementation merge.

- [ ] **Step 8: Commit only if verification required a real fix**

Use a focused `[phase1-no-source]` commit describing the verified defect. Do not create a bookkeeping-only commit.

---

### Task 11: Perform the explicit operator MT5 qualification after verified merge

**Files/artifacts:**
- Runtime evidence outside Git: `evidence/phase8/qualification/qualification.json`

**Preconditions:**
- Tasks 1–10 are merged and freshly green on `main`.
- FP Markets MT5 demo is logged in on `FPMarketsSC-Demo` or `FPMarketsSC-Demo2`.
- USDJPY quotes are moving.
- AutoTrading is OFF.
- `FMPPhase8QuoteBridge.mq5` compiled in MetaEditor with 0 errors and is attached to USDJPY.

- [ ] **Step 1: Run qualification explicitly on the operator Mac**

```bash
python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification
```

No broker password, account number, token, or secret is supplied to FMP.

- [ ] **Step 2: Inspect the result**

Require:

```text
outcome == PASS
price_count >= 100
heartbeat_count >= 6
connector_protocol == fmp-mt5-demo-file-bridge-v1
provider == FP_MARKETS_MT5_DEMO
transport == MT5_FILE_COMMON_JSONL
actual server in {FPMarketsSC-Demo, FPMarketsSC-Demo2}
no bridge liveness gap > 15 seconds
no market-feed liveness gap > 15 seconds
no malformed/unknown/session/source-time integrity rejection
```

Outcomes:
- `PASS` -> return to the frozen Phase 8 reference/campaign-registration step; do not start a scored campaign before reference+registration exist.
- `INCONCLUSIVE` -> retain evidence and retry later without changing thresholds/protocol.
- `CONNECTOR_UNAVAILABLE` or `CONNECTOR_REJECTED` -> retain evidence and stop; do not bypass with live server, alternate broker, or parameter changes.

- [ ] **Step 3: Preserve the phase boundary**

Do not place a demo/live order, do not enable an execution connector, do not create `fmp-v1-phase8-shadow`, and do not start Phase 9. Qualification PASS only unlocks the already-frozen Phase 8 reference generation and campaign registration sequence.

---

## Plan self-review checklist

- [x] Every approved amendment requirement maps to a task.
- [x] Source-of-truth activation occurs before runtime changes.
- [x] MQL5 execution APIs are structurally forbidden and statically tested.
- [x] Python imports no MetaTrader5 execution package.
- [x] Demo mode, symbol, exact server allowlist, protocol, and fixed file identity are fail-closed.
- [x] Plain account login/password never enter FMP evidence; only local SHA-256 fingerprint is emitted.
- [x] Reader-start EOF semantics prevent backfill.
- [x] Local bridge heartbeat never advances market time/bars/strategy.
- [x] Bridge and market-feed liveness are independently gated at 15 seconds.
- [x] Evidence protocol is v2 and cannot mix OANDA v1 segments into the new campaign.
- [x] Strategy/simulator/risk/slippage/acceptance thresholds remain unchanged.
- [x] Deterministic replay uses the same runtime pipeline.
- [x] OANDA live runtime is removed only after MT5 replacement paths are working.
- [x] Operator workflow requires AutoTrading OFF and explicit starts only.
- [x] CI never performs live MT5 qualification.
- [x] Phase 1 acquisition is not invoked.
- [x] Phase 9/demo execution/real money remain locked.
- [x] No implementation task creates the Phase 8 PASS tag.
