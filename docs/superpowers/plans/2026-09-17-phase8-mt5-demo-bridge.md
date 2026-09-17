# Phase 8 MT5 Demo Quote Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unavailable OANDA Practice quote-source path with the approved read-only FP Markets MT5 demo file bridge while preserving all frozen Phase 8 strategy, simulator, campaign, replay, review, and no-order constraints.

**Architecture:** Add a source-auditable MQL5 Expert Advisor that emits only `BRIDGE_START`, `TICK`, and `BRIDGE_HEARTBEAT` JSONL records to the fixed MT5 `FILE_COMMON` path. Add a Python bridge reader/normalizer that discovers only the fixed transport file under bounded MetaQuotes/Wine Common Files roots, validates session/server/account bindings, feeds accepted ticks into the existing provider-neutral shadow pipeline, and keeps local heartbeats out of market-time/bar advancement. Retire OANDA from all operator/runtime entry points without introducing the `MetaTrader5` Python package or any trading surface.

**Tech Stack:** MQL5 EA source, Python 3.11+, standard-library `pathlib/json/hashlib/time/datetime`, existing FMP Phase 8 contracts/bars/strategy/simulation/evidence/replay/review code, `unittest`/pytest-compatible repository tests, GitHub Actions source-free verification.

**Spec:** `docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md`

## Global Constraints

- Preserve DEC-008: no demo order placement, live order placement, order modification/cancellation, broker mutation, or real-money path.
- Phase 8 remains `ACTIVE`; Phase 9 remains locked.
- New experiment identity is exactly `EXP-20260917-010`; decision identity is exactly `DEC-037`.
- Sole strategy remains `session_breakout`, `USDJPY`, `15m`, 5-pip buffer, 1.5x target, exact London-session/DST semantics, exact 16:00 `Europe/London` flat time, no ML overlay.
- Virtual scenarios remain exactly 0.2/0.5/1.0 adverse pips per fill with independent $100,000 starting equity, zero commission, and zero financing.
- Evidence protocol is exactly `fmp-phase8-shadow-evidence-v2`; connector protocol is exactly `fmp-mt5-demo-file-bridge-v1`.
- Provider identity is exactly `FP_MARKETS_MT5_DEMO`; transport identity is exactly `MT5_FILE_COMMON_JSONL`; logical bridge file is exactly `FMP/phase8-usdjpy-feed.jsonl`.
- Approved MT5 servers are exactly `FPMarketsSC-Demo` and `FPMarketsSC-Demo2`; live server names are forbidden.
- The EA must fail closed unless account mode is demo and chart symbol is exactly `USDJPY`.
- The EA source must contain no `OrderSend`, `OrderSendAsync`, `MqlTradeRequest`, `MqlTradeResult`, `CTrade`, position/order mutation helper, or `<Trade/Trade.mqh>` import.
- Python runtime must import no `MetaTrader5`/`mt5` package and expose no broker mutation API.
- AutoTrading remains off in operator instructions; this is a secondary safety control, not the primary structural guarantee.
- `BRIDGE_HEARTBEAT` is local liveness only. It must never become a provider-market `HeartbeatEvent`, close/advance bars, advance strategy time, trigger entry/exit, or satisfy quote deadlines.
- Market ordering is authoritative only from `MqlTick.time_msc` on accepted `TICK` records.
- Stale timeout remains 15 seconds for both bridge liveness and market-feed liveness during live shadow capture.
- Qualification remains bounded to at most 600 seconds and requires at least 100 post-reader-start valid ticks and 6 valid bridge heartbeats.
- No backfill/reconstruction from pre-reader-start transport content, MT5 candles, broker history, or missed periods.
- FMP accepts no arbitrary bridge filename/path from CLI. Python may only auto-discover the fixed file under a bounded set of known MetaQuotes/Wine Common Files roots; tests may inject temporary roots only through private/internal helpers.
- The plain account login/password must never be persisted. Only a lowercase SHA-256 account fingerprint may cross the bridge/evidence boundary.
- No live MT5 qualification, live shadow campaign, or broker interaction runs in CI.
- Follow TDD for runtime behavior: failing test first, verify failure, minimal implementation, verify pass, then regression.
- Every branch commit remains source-free and uses `[phase1-no-source]` so Phase 1 acquisition workflows stay suppressed.

## File Structure

New focused files:

- `mt5/Experts/FMPPhase8QuoteBridge.mq5` — demo-only USDJPY quote/heartbeat producer; no execution surface.
- `src/fmp/shadow/mt5_bridge.py` — protocol constants, typed parsed records, strict JSONL parser, fixed-file discovery, no-backfill tail reader, session binding, duplicate/source-time checks.
- `tests/test_phase8_mt5_bridge.py` — parser/discovery/tail/session/duplicate tests.
- `tests/test_phase8_mt5_ea_safety.py` — source-level MQL5 structural guard.

Existing files updated by responsibility:

- `src/fmp/shadow/contracts.py` — amended experiment/provider constants only; provider-neutral quote/simulation contracts stay intact.
- `src/fmp/shadow/qualification.py` — MT5-file qualification and separate bridge/market liveness.
- `src/fmp/shadow/runner.py` — bridge-record ingestion and separate liveness; strategy/simulator logic remains reused.
- `src/fmp/shadow/cli.py` — no credentials; explicit local `qualify`/`run` against fixed discovered bridge file.
- `src/fmp/shadow/evidence.py` — v2 manifest connector identity/session/server/source binding.
- `src/fmp/shadow/campaign.py` — v2 registration identity; unchanged frozen thresholds.
- `src/fmp/shadow/replay.py` — deterministic replay of captured MT5 bridge records.
- `src/fmp/shadow/review_compiler.py` — validate v2 segment/registration identity and reject mixed protocols.
- `tests/test_phase8_structural_safety.py` — retain Python no-order checks and add no-MT5-package/no-live-server rules.
- `tests/test_phase8_cli.py`, `tests/test_phase8_qualification.py`, `tests/test_phase8_runner.py`, `tests/test_phase8_evidence.py`, `tests/test_phase8_campaign*.py`, `tests/test_phase8_replay.py`, `tests/test_phase8_review_*.py`, `tests/test_phase8_operator_handoff.py` — amended expectations.
- `docs/decision-log.md`, `docs/experiment-log.md`, `docs/project-state.md`, `docs/source-register.md`, and the amendment spec — source-of-truth transition.

---

### Task 1: Activate DEC-037 / EXP-20260917-010 source of truth

**Files:**
- Modify: `docs/superpowers/specs/2026-09-17-phase8-mt5-bridge-amendment.md`
- Modify: `docs/decision-log.md`
- Modify: `docs/experiment-log.md`
- Modify: `docs/project-state.md`
- Modify: `docs/source-register.md`
- Modify: `tests/test_phase8_protocol_state.py`

**Interfaces:**
- Consumes: approved amendment spec and existing DEC-036/EXP-20260915-009 state.
- Produces: authoritative activated MT5 connector identity consumed by all later tasks.

- [ ] **Step 1: Write the failing protocol-state test**

Change `tests/test_phase8_protocol_state.py` to require `DEC-037`, `EXP-20260917-010`, `FP_MARKETS_MT5_DEMO`, the two demo servers, amendment status `APPROVED / ACTIVATED`, Phase 8 `ACTIVE`, and all demo/live/real-money locks. Require the old experiment to be recorded as stopped before qualification, not financially/market/safety rejected.

- [ ] **Step 2: Run the focused test and require RED**

Run: `python -m unittest tests.test_phase8_protocol_state -v`
Expected: FAIL because source-of-truth files still describe DEC-036/OANDA as the active connector.

- [ ] **Step 3: Make the source-of-truth edits**

Add DEC-037 to the decision index and body; record DEC-036 as superseded only for the Phase 8 quote-source connector while preserving its unchanged strategy/campaign gates. Mark `EXP-20260915-009` stopped before qualification because the required account was unavailable to the operator; add `EXP-20260917-010` as RUNNING. Update project state next milestone to MT5 bridge implementation/qualification. Update source register to select the MQL5 file bridge and keep direct Python `MetaTrader5` integration explicitly rejected for Phase 8. Change amendment status to `APPROVED / ACTIVATED`.

- [ ] **Step 4: Verify GREEN**

Run: `python -m unittest tests.test_phase8_protocol_state tests.test_phase7_acceptance_state tests.test_phase7_protocol_state -v`
Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "[phase1-no-source] Activate Phase 8 MT5 bridge amendment"`

---

### Task 2: Freeze amended Phase 8 constants and connector identity

**Files:**
- Modify: `src/fmp/shadow/contracts.py`
- Modify: `tests/test_phase8_contracts.py`

**Interfaces:**
- Produces exact constants: `PHASE8_EXPERIMENT_ID`, `MT5_BRIDGE_PROTOCOL`, `MT5_PROVIDER`, `MT5_TRANSPORT`, `MT5_BRIDGE_FILE`, `MT5_ALLOWED_SERVERS`.

- [ ] **Step 1: Add failing contract tests** requiring exact values and unchanged strategy/slippage/liveness/deadline constants.
- [ ] **Step 2: Run focused tests and require RED.**
- [ ] **Step 3: Add only the new constants and replace old experiment/provider-export constants where runtime no longer needs OANDA. Keep `NormalizedQuote`, `ShadowIntent`, `ShadowOutcome` semantics unchanged.**
- [ ] **Step 4: Run `python -m unittest tests.test_phase8_contracts -v` and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Freeze Phase 8 MT5 connector contracts`.

---

### Task 3: Add the read-only MQL5 bridge and structural safety guard

**Files:**
- Create: `mt5/Experts/FMPPhase8QuoteBridge.mq5`
- Create: `tests/test_phase8_mt5_ea_safety.py`
- Modify: `tests/test_phase8_structural_safety.py`

**Interfaces:**
- Produces fixed JSONL record shapes for `BRIDGE_START`, `TICK`, `BRIDGE_HEARTBEAT`.
- No callable trading interface is produced.

- [ ] **Step 1: Write failing source-safety tests** that require the exact bridge protocol/file/server literals, explicit demo-mode and exact-symbol checks, SHA-256 hashing use, `OnTick`, a timer heartbeat, `FILE_COMMON`, `FileFlush`, and all three record types; reject every forbidden order/trade/position identifier/import and any `FPMarketsSC-Live` literal.
- [ ] **Step 2: Run tests and require RED because the `.mq5` file does not exist.**
- [ ] **Step 3: Implement the minimal EA**: `OnInit` validates `ACCOUNT_TRADE_MODE_DEMO`, `_Symbol == "USDJPY"`, server allowlist; creates a new session ID; hashes the login locally; truncates/creates the fixed transport only at session start; emits `BRIDGE_START`; starts a five-second timer. `OnTick` reads `MqlTick` and emits only finite positive non-crossed bid/ask ticks. `OnTimer` emits liveness-only heartbeat with last tick time. Every record carries protocol/session/symbol/server/fingerprint; every write is newline-terminated and flushed. No execution library/import/function is present.
- [ ] **Step 4: Run safety tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Add read-only MT5 Phase 8 quote bridge`.

---

### Task 4: Implement strict Python bridge parser, session binding, discovery, and no-backfill tailing

**Files:**
- Create: `src/fmp/shadow/mt5_bridge.py`
- Create: `tests/test_phase8_mt5_bridge.py`
- Modify: `src/fmp/shadow/__init__.py`

**Interfaces:**
- Produces `BridgeStartRecord`, `BridgeTickRecord`, `BridgeHeartbeatRecord`, `BridgeRecord`.
- Produces `parse_bridge_line(line: bytes) -> BridgeRecord`.
- Produces `BridgeSessionValidator.accept(record, received_at_utc, receive_monotonic_ns) -> NormalizedQuote | None` plus liveness metadata.
- Produces `discover_bridge_file() -> Path` using bounded fixed-name discovery only.
- Produces `BridgeFileTail` that validates the first `BRIDGE_START`, snapshots EOF, then yields only complete appended lines after reader start.

- [ ] **Step 1: Write failing tests** for valid start/tick/heartbeat, malformed/unknown records, exact field sets, wrong protocol/symbol/server/session/fingerprint, non-hex fingerprint, bad/crossed/nonfinite/nonpositive prices, source-time regression, exact duplicate dedup, conflicting duplicate rejection, partial final line waiting, reader-start offset, file truncation/session restart detection, and bounded discovery rejecting ambiguity.
- [ ] **Step 2: Run focused tests and require RED.**
- [ ] **Step 3: Implement minimal parser/validator/tailer.** Tick epoch milliseconds convert to aware UTC; heartbeats never produce `HeartbeatEvent`; exact duplicates return `None`; conflicting same-source-time ticks raise a bridge integrity error. Discovery checks only fixed filename candidates below known MetaQuotes/Wine Common Files roots and raises on zero or multiple matches.
- [ ] **Step 4: Run focused tests and existing normalization tests; require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Add MT5 bridge parser and tail reader`.

---

### Task 5: Replace qualification with the bounded MT5 bridge protocol

**Files:**
- Modify: `src/fmp/shadow/qualification.py`
- Modify: `tests/test_phase8_qualification.py`

**Interfaces:**
- Produces `qualify_bridge(tail, *, utc_now, monotonic_ns) -> QualificationResult`.
- `QualificationResult` adds active session/server/account fingerprint plus separate `max_bridge_liveness_gap_seconds` and `max_market_liveness_gap_seconds`.

- [ ] **Step 1: Rewrite/add failing tests** for PASS at 100 ticks + 6 heartbeats after reader start; INCONCLUSIVE for insufficient market activity; CONNECTOR_UNAVAILABLE for missing/inaccessible/inactive bridge; CONNECTOR_REJECTED for malformed/session/server/fingerprint/source-regression/conflicting duplicate; and the distinct >15s bridge-vs-market gap rules from the spec.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Implement qualification against `BridgeFileTail`/`BridgeSessionValidator`.** No strategy/bar/simulator object may be constructed. Boundary audit reports protocol/provider/transport/fixed file/allowed servers only.
- [ ] **Step 4: Run qualification + bridge tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Qualify the MT5 demo quote bridge`.

---

### Task 6: Route MT5 ticks through the existing shadow runner with two-dimensional liveness

**Files:**
- Modify: `src/fmp/shadow/runner.py`
- Modify: `tests/test_phase8_runner.py`
- Modify: `tests/test_phase8_processing_latency.py`
- Modify: `tests/test_phase8_restart_state.py`

**Interfaces:**
- Adds `ShadowRunner.process_bridge_record(...)` or equivalent narrow method accepting already parsed bridge records.
- Accepted ticks reuse existing `NormalizedQuote -> LiveBarBuilder -> strategy -> ShadowSimulator` path.
- Bridge heartbeats update local liveness evidence only.

- [ ] **Step 1: Write failing tests** proving heartbeat-only input never closes bars/advances simulator time, bridge and market liveness are tracked separately, a >=15s gap invalidates the London date under existing stale rules, restart/session change prevents continuity, and tick processing still writes durable raw/normalized latency evidence.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Refactor the smallest provider-neutral quote-processing helper out of `process_provider_message`; call it from the MT5 path.** Preserve all existing strategy/simulation semantics. Do not duplicate bar/strategy/simulator code.
- [ ] **Step 4: Run runner/bars/strategy/simulation/restart/latency tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Feed MT5 ticks into Phase 8 shadow runtime`.

---

### Task 7: Convert CLI/operator commands to local MT5 bridge with no credentials or path overrides

**Files:**
- Modify: `src/fmp/shadow/cli.py`
- Modify: `tests/test_phase8_cli.py`
- Modify: `scripts/phase8_shadow.py` only if delegation text needs no functional change.

**Interfaces:**
- `qualify --out ...` discovers the fixed bridge file automatically.
- `run --campaign-dir ...` discovers the fixed bridge file automatically.
- No account/token/server/path/filename/instrument option or environment secret is required.

- [ ] **Step 1: Write failing CLI tests** requiring absence of OANDA credential env requirements, absence of arbitrary path/server/instrument overrides, fixed-file discovery injection through internal dependency hooks for tests, qualification result persistence, and no secret/account-login persistence.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Remove OANDA stream construction and credential hashing from CLI; wire `discover_bridge_file`, tail creation, `qualify_bridge`, and MT5 capture runner.**
- [ ] **Step 4: Run CLI/operator-handoff tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Switch Phase 8 CLI to MT5 bridge`.

---

### Task 8: Upgrade evidence and campaign registration to connector protocol v2

**Files:**
- Modify: `src/fmp/shadow/evidence.py`
- Modify: `src/fmp/shadow/campaign.py`
- Modify: `tests/test_phase8_evidence.py`
- Modify: `tests/test_phase8_campaign.py`
- Modify: `tests/test_phase8_campaign_registration_guard.py`
- Modify: `tests/test_phase8_campaign_risk_identity.py`

**Interfaces:**
- `EvidenceWriter` is bound at construction to `bridge_session_id`, `server`, `account_fingerprint_sha256`, and bridge-source/repository commit identity.
- Manifest protocol becomes v2 and removes OANDA HTTP fields.
- Campaign registration becomes v2 and freezes MT5 connector/provider/transport/fixed-file/allowed-server identity while leaving acceptance thresholds unchanged.

- [ ] **Step 1: Write failing tests** for exact v2 fields, absence of OANDA host/method/path/snapshot fields, no plain account login/password, canonical bytes, write-once registration, unchanged strategy/risk/slippage/threshold identities, and mixed connector registration rejection.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Implement minimal v2 manifest/registration changes.** Do not alter reference-generation economics or gate thresholds.
- [ ] **Step 4: Run evidence/campaign/reference tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Version Phase 8 evidence for MT5 bridge`.

---

### Task 9: Make live capture and deterministic replay MT5-native

**Files:**
- Modify: `src/fmp/shadow/runner.py`
- Modify: `src/fmp/shadow/replay.py`
- Modify: `tests/test_phase8_replay.py`
- Modify: `tests/test_phase8_runner.py`

**Interfaces:**
- `run_live_shadow_capture` consumes the fixed MT5 bridge tail and active `BRIDGE_START` binding rather than OANDA account/token/stream factory.
- `raw.jsonl` stores accepted bridge records plus FMP receive metadata; replay re-feeds those records through the same MT5 parser/session validator/runner path.

- [ ] **Step 1: Write failing replay/capture tests** proving semantic byte-for-byte replay, session/server/fingerprint mismatch rejection, restart behavior, and no pre-reader-start backfill.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Implement MT5 capture/replay path; remove OANDA parsing from replay/capture entry points.**
- [ ] **Step 4: Run replay + runner tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Replay MT5 bridge shadow evidence deterministically`.

---

### Task 10: Amend review compiler and campaign aggregation for v2-only campaigns

**Files:**
- Modify: `src/fmp/shadow/review_compiler.py`
- Modify: `tests/test_phase8_review_compiler.py`
- Modify: `tests/test_phase8_review_aggregation.py`
- Modify: `tests/test_phase8_review_compiler_wiring.py`
- Modify: `tests/test_phase8_review_spread_precision.py` only if fixture identity changes.

**Interfaces:**
- Compiler accepts only campaign-registered v2 MT5 segments for `EXP-20260917-010`.
- Existing operational/market/financial/safety gate order and exact outcome vocabulary remain unchanged.

- [ ] **Step 1: Add failing tests** for v2 identity validation, mixed OANDA-v1/MT5-v2 rejection, manifest/session/server mismatch rejection, unchanged spread/timing/financial calculations, and empty campaign -> NEED_MORE_DATA behavior.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Update compiler validation only; do not change gate thresholds or outcome precedence.**
- [ ] **Step 4: Run review/gates/campaign tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Validate MT5 v2 campaign evidence`.

---

### Task 11: Retire OANDA from active runtime surfaces and strengthen structural guards

**Files:**
- Modify: `src/fmp/shadow/__init__.py`
- Modify: `tests/test_phase8_structural_safety.py`
- Modify/delete active imports in `src/fmp/shadow/cli.py`, `qualification.py`, `runner.py`, `replay.py`.
- Keep `src/fmp/shadow/oanda.py` only if historical unit fixtures still require it; it must be unreachable from active Phase 8 operator/runtime commands. Delete it only if all tests and history remain clearer without it.

**Interfaces:**
- Active runtime graph contains no OANDA stream construction and no generic broker fallback.
- Python source still contains no MT5 Python SDK imports or public mutation names.

- [ ] **Step 1: Add failing structural tests** that inspect active modules/import graph and require MT5 bridge runtime entry points, no OANDA active imports, no `MetaTrader5`/`mt5`, no production/live FP Markets server literals, and no execution method names.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Remove obsolete active imports/exports and keep any historical module isolated.**
- [ ] **Step 4: Run all structural safety tests and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Lock Phase 8 to read-only MT5 bridge`.

---

### Task 12: Update operator handoff for macOS MT5

**Files:**
- Modify: `tests/test_phase8_operator_handoff.py`
- Modify: `docs/superpowers/plans/2026-09-15-phase8-live-shadow.md` only by adding a supersession note; do not rewrite historical plan.
- Create: `docs/phase8-mt5-operator-handoff.md`

**Interfaces:**
- Produces exact operator sequence: compile EA -> attach to USDJPY demo chart -> AutoTrading OFF -> qualify -> build reference -> register -> run -> replay -> review.

- [ ] **Step 1: Write failing handoff test** pinning exact commands and explicit warnings that no password is shared and no demo/live orders are authorized.
- [ ] **Step 2: Run and require RED.**
- [ ] **Step 3: Write concise Mac handoff with MetaEditor placement instructions, fixed bridge filename identity, discovery troubleshooting, expected qualification result codes, and exact existing offline reference/register/replay/review commands.**
- [ ] **Step 4: Run handoff test and require PASS.**
- [ ] **Step 5: Commit** with `[phase1-no-source] Document MT5 Phase 8 operator handoff`.

---

### Task 13: Full source-free verification and merge readiness

**Files:**
- No new feature behavior unless verification exposes a defect.

**Interfaces:**
- Produces a branch that is safe to review/merge but still does not run live qualification.

- [ ] **Step 1: Run full Python suite**: `python -m unittest discover -s tests -v`.
- [ ] **Step 2: Validate workflow YAML** with the repository validator/test.
- [ ] **Step 3: Compile Python**: `python -m compileall -q src tests`.
- [ ] **Step 4: Run Phase 3 deterministic acceptance source-free regression and confirm no Phase 1 acquisition workflow triggers.**
- [ ] **Step 5: Inspect branch diff for secrets/account IDs, forbidden trading identifiers, live server literals, accidental threshold/strategy changes, and placeholder text.**
- [ ] **Step 6: Confirm CI does not compile or run MT5 and does not claim a live qualification PASS.**
- [ ] **Step 7: Create/update the pull request with exact source-free verification evidence. Do not tag Phase 8 and do not start Phase 9.**

## Execution Boundary After Merge

After this plan is implemented, reviewed, source-free verified, and merged to `main`, the next action is **operator-controlled live connector qualification**, not additional code and not a demo order. The operator keeps MT5 logged into the FP Markets demo account, keeps AutoTrading OFF, compiles/attaches `FMPPhase8QuoteBridge` to the `USDJPY` chart, and runs:

```bash
python scripts/phase8_shadow.py qualify --out evidence/phase8/qualification
```

Only a real `PASS` qualification under the amended connector permits the existing offline reference build and new campaign registration. Phase 8 remains `ACTIVE` until the full multi-week campaign independently satisfies all frozen gates and offline review returns exactly `PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN`.
