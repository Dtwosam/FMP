# EXP-006 Session Sweep-Rejection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and benchmark the predeclared `EXP-20260914-006` Asian-session high/low sweep-rejection baseline exactly as frozen by DEC-026, without changing Phase 3 semantics or touching the final-test split.

**Architecture:** Follow the existing Phase 4 family boundary: deterministic signal generation in `fmp.strategies`, source-free grid execution in `fmp.research`, a thin CLI in `scripts/`, and a narrowly scoped GitHub Actions benchmark workflow. Reuse accepted Phase 2 processed artifacts and the existing Phase 3 adapter/backtester/reporting stack. Candidate generation occurs once per buffer and is reused byte-identically across all three cost scenarios.

**Tech Stack:** Python 3.12, stdlib `unittest`, existing `fmp` strategy/research/backtest contracts, GitHub Actions YAML, accepted Phase 2 artifact ZIPs.

**Spec:** `docs/superpowers/specs/2026-09-14-phase4-session-sweep-rejection-design.md` and DEC-026 in `docs/decision-log.md`.

## Global Constraints

- Implement only the frozen EXP-006 protocol: EURUSD/GBPUSD/USDJPY × 5m/15m/1h; London reference `[00:00, 08:00)`; signal labels 08:00–14:00 inclusive; buffers 0/2/5 pips; exact 16:00 London flat.
- LONG/SHORT predicates, strict close-back-inside semantics, dual-side ambiguity, first-signal-only behavior, signal-bar-extreme stop, and frozen session-midpoint target must match DEC-026 literally.
- Development and validation only. Any `final` split request must fail before market-data loading.
- Keep accepted Phase 3 execution/risk semantics unchanged: 0.25% requested risk, 0.50% hard maximum, 1.00% simultaneous open risk, 1.50% UTC day-start realized-loss halt; historical BID/ASK execution; conservative ambiguity semantics.
- Cost scenarios are exactly 0.2/0.5/1.0 adverse slippage pips per fill, zero commission, zero financing.
- No Dukascopy/upstream source access, raw mutation, Supabase write, acquisition credential, final-test access, broker/live path, or real-money permission.
- Result-producing workflow must bind `code_commit` to the exact merged-main SHA.
- No post-result parameter expansion or rescue logic under EXP-006.

---

## Task 1: Add strategy-level RED tests

**Files:**
- Create: `tests/test_phase4_session_sweep_rejection.py`
- Reference only: `src/fmp/strategies/previous_day_rejection.py`, `src/fmp/strategies/session_breakout.py`

- [ ] Add helper builders for deterministic `QuoteBar` sequences at 5m/15m/1h with explicit UTC timestamps and BID/ASK values.
- [ ] Add a config test proving only buffers `{0,2,5}` and timeframes `{5m,15m,1h}` are accepted.
- [ ] Add winter and summer DST tests proving `[00:00,08:00)` and exact 16:00 London map through `ZoneInfo("Europe/London")`, never hard-coded UTC offsets.
- [ ] Add reference tests proving exactly the full 00:00–08:00 midpoint OHLC window is used and the 08:00 signal bar is excluded from the frozen high/low/midpoint.
- [ ] Add fail-closed tests for missing reference cadence, missing signal-session cadence, missing exact 16:00 exit, duplicate identity, and multi-symbol input.
- [ ] Add SHORT test: previous close `<= high`, current high `>= high + buffer`, current close strictly `< high`; assert stop=current midpoint high and target=frozen session midpoint.
- [ ] Add symmetric LONG test at the reference low.
- [ ] Add zero-buffer test proving an intrabar boundary touch can satisfy penetration but a close exactly on the boundary does not qualify.
- [ ] Add JPY pip-size test proving 2/5-pip buffers use the accepted USDJPY pip convention.
- [ ] Add dual-side bar test expecting deterministic `AMBIGUOUS_DUAL_SESSION_SWEEP` NO_TRADE evidence.
- [ ] Add complete-no-setup test expecting `NO_SESSION_SWEEP_REJECTION`.
- [ ] Add first-qualifying-signal-only test and ensure later same-day opposite-direction setups are ignored.
- [ ] Add invalid signal-time geometry test: first qualifying sweep is consumed and emitted as reasoned NO_TRADE rather than repaired or followed by a later retry.
- [ ] Add byte-determinism test over repeated candidate generation.

Run RED:

```bash
python -m unittest tests.test_phase4_session_sweep_rejection -v
```

Expected: failure because `fmp.strategies.session_sweep_rejection` does not yet exist.

Commit only tests at RED:

```bash
git add tests/test_phase4_session_sweep_rejection.py
git commit -m "[phase1-no-source] Add RED EXP-006 strategy tests"
```

## Task 2: Implement deterministic strategy generator to GREEN

**Files:**
- Create: `src/fmp/strategies/session_sweep_rejection.py`
- Test: `tests/test_phase4_session_sweep_rejection.py`

Required public interface:

```python
@dataclass(frozen=True, slots=True)
class SessionSweepRejectionConfig:
    buffer_pips: int
    timeframe: str


def generate_session_sweep_rejection_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: SessionSweepRejectionConfig,
) -> tuple[SignalCandidate, ...]:
    ...
```

Implementation notes:

- [ ] Define `LONDON = ZoneInfo("Europe/London")`, timeframe minutes map, and allowed buffers exactly `{0,2,5}`.
- [ ] Compute midpoint high/low/close only for analysis; never synthesize execution prices.
- [ ] Build London-local reference labels from 00:00 inclusive to 08:00 exclusive at exact tested cadence.
- [ ] Build eligible signal labels 08:00 through 14:00 inclusive and required signal-session labels from one bar before 08:00 through exact 16:00.
- [ ] Require exact identities/cadence and finite midpoint values. Do not shorten windows or interpolate.
- [ ] Freeze `reference_high`, `reference_low`, `reference_midpoint` once per London date; require `high > low`.
- [ ] Evaluate the exact DEC-026 predicates using `buffer_pips * pip_size(symbol)`.
- [ ] On dual qualification emit NO_TRADE with `AMBIGUOUS_DUAL_SESSION_SWEEP` and stop scanning the date/config.
- [ ] For first directional qualification, freeze signal-bar extreme stop and session-midpoint target. If signal-time geometry is invalid, emit deterministic NO_TRADE such as `INVALID_SESSION_SWEEP_GEOMETRY`, consume the date/config, and do not retry.
- [ ] Otherwise emit a directional `SignalCandidate` with `signal_known_timestamp_utc = observation + timeframe width`, exact 16:00 exit, deterministic ID, and sufficient metadata for subperiod/level audit.
- [ ] Complete dates with no setup emit `NO_SESSION_SWEEP_REJECTION`.

Run GREEN:

```bash
python -m unittest tests.test_phase4_session_sweep_rejection -v
```

Then regression subset:

```bash
python -m unittest tests.test_phase4_previous_day_rejection tests.test_phase4_session_breakout -v
```

Commit:

```bash
git add src/fmp/strategies/session_sweep_rejection.py tests/test_phase4_session_sweep_rejection.py
git commit -m "[phase1-no-source] Implement EXP-006 session sweep signals"
```

## Task 3: Add research-runner RED tests

**Files:**
- Create: `tests/test_phase4_session_sweep_rejection_research.py`
- Reference: `src/fmp/research/previous_day_rejection.py`, `src/fmp/research/volatility_breakout.py`

- [ ] Test frozen grid constants: buffers `(0,2,5)`, slippage `(0.2,0.5,1.0)`, $100k starting equity, 0.25% requested risk.
- [ ] Test `final` is rejected before the injected/monkeypatched loader can be called.
- [ ] Test one pair/timeframe/split produces exactly 9 rows = 3 buffers × 3 costs.
- [ ] Test candidate generation is invoked once per buffer, not once per cost scenario.
- [ ] For each fixed buffer, assert candidate SHA/count/reason counts are identical across all three cost rows.
- [ ] Assert each backtest run identity includes family/version, split, buffer, candidate SHA, processed-manifest SHA, canonical schema, timeframe, exact requested split bounds, cost/risk identity, and supplied code commit.
- [ ] Assert USDJPY research path uses the strategy’s accepted pip convention rather than introducing a family-local pip calculation.

Run RED:

```bash
python -m unittest tests.test_phase4_session_sweep_rejection_research -v
```

Expected: missing `fmp.research.session_sweep_rejection`.

Commit tests-only RED.

## Task 4: Implement source-free research grid to GREEN

**Files:**
- Create: `src/fmp/research/session_sweep_rejection.py`
- Test: `tests/test_phase4_session_sweep_rejection_research.py`

Required interface:

```python
SESSION_SWEEP_REJECTION_GRID = (0, 2, 5)
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
RESULT_PROTOCOL = "fmp-phase4-session-sweep-rejection-grid-v1"


def run_session_sweep_rejection_grid(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    split_name: str,
    code_commit: str,
) -> dict[str, object]:
    ...
```

- [ ] Call `allowed_split(split_name)` before reading manifest/data.
- [ ] Reuse `load_processed_bars`, `candidate_to_decision`, `run_backtest`, `compute_research_metrics`, `RiskConfig`, `ZeroCommission`, and `ZeroFinancing` exactly as existing Phase 4 families do.
- [ ] Hash accepted processed-manifest bytes and candidate bytes deterministically.
- [ ] Generate candidates exactly once per buffer and reuse decisions/scheduled exits across costs.
- [ ] Emit exactly 9 configuration rows per workflow cell with stable sorted reason counts.
- [ ] Bind code commit, processed-manifest SHA, schema version, family/version, split, buffer, candidate SHA, timeframe, costs, and risk configuration into deterministic evidence.

Run:

```bash
python -m unittest tests.test_phase4_session_sweep_rejection_research -v
```

Commit implementation + tests.

## Task 5: Add CLI RED tests and implement thin CLI

**Files:**
- Create: `tests/test_phase4_session_sweep_rejection_cli.py`
- Create: `scripts/phase4_session_sweep_rejection.py`

RED tests:

- [ ] `--help` exposes only symbols EURUSD/GBPUSD/USDJPY, timeframes 5m/15m/1h, and splits development/validation.
- [ ] Passing `--split final` fails in argparse before any loader/research execution.
- [ ] Static source scan confirms no Dukascopy URL/source client, raw mutation, Supabase write, acquisition credential, broker/live, or final-test bypass.
- [ ] Main delegates only to `run_session_sweep_rejection_grid` and `write_benchmark_artifacts`, printing deterministic compact JSON.

Implement by mirroring the thin existing Phase 4 CLIs.

Run:

```bash
python -m unittest tests.test_phase4_session_sweep_rejection_cli -v
```

Commit.

## Task 6: Add workflow RED tests and implement benchmark workflow

**Files:**
- Create: `tests/test_phase4_session_sweep_rejection_workflow.py`
- Create: `.github/workflows/phase4-session-sweep-rejection.yml`

Workflow requirements:

- [ ] Push trigger on `main` is narrowly scoped to only EXP-006 strategy, research, CLI, and workflow paths; `workflow_dispatch` may also be present.
- [ ] Permissions are read-only (`contents: read`, `actions: read`).
- [ ] Matrix is exactly 3 accepted Phase 2 artifacts × 3 timeframes × 2 splits = 18 jobs.
- [ ] Pin accepted Phase 2 artifact IDs and ZIP SHA-256 values already used by other Phase 4 workflows:
  - EURUSD artifact `10325737935`, ZIP `db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3`
  - GBPUSD artifact `10326096831`, ZIP `fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2`
  - USDJPY artifact `10327600628`, ZIP `6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72`
- [ ] Download accepted artifacts only through GitHub Actions API; verify ZIP SHA before unzip.
- [ ] Run CLI with `--code-commit "${GITHUB_SHA}"`.
- [ ] Verify benchmark protocol, symbol/timeframe/split/code commit, exactly 9 rows, and one candidate digest per fixed buffer across costs.
- [ ] Upload one deterministic evidence artifact per cell.
- [ ] Workflow text must contain no Phase 1 source command, Dukascopy host, source credential, raw write, final split, broker/live, or real-money path.

Run RED before workflow exists, then GREEN:

```bash
python -m unittest tests.test_phase4_session_sweep_rejection_workflow -v
ruby scripts/validate_workflow_yaml.rb .github/workflows
```

Commit.

## Task 7: Full verification before implementation merge

- [ ] Run the EXP-006 focused suite:

```bash
python -m unittest \
  tests.test_phase4_session_sweep_rejection \
  tests.test_phase4_session_sweep_rejection_research \
  tests.test_phase4_session_sweep_rejection_cli \
  tests.test_phase4_session_sweep_rejection_workflow \
  tests.test_phase4_session_sweep_state -v
```

- [ ] Run full unit suite:

```bash
python -m unittest discover -s tests -v
```

- [ ] Validate all workflow YAML and compile package/scripts:

```bash
ruby scripts/validate_workflow_yaml.rb .github/workflows
python -m compileall -q src scripts
```

- [ ] Confirm Phase 3 acceptance remains green.
- [ ] Confirm both Phase 1 source-capable PR checks are SKIPPED.
- [ ] Review compare against merged main: only plan + EXP-006 strategy/research/CLI/workflow/tests; no data/source/final/live changes.
- [ ] Merge with `[phase1-no-source]` and expected-head SHA pinned.

## Task 8: Authoritative merged-main benchmark and independent audit

After implementation is merged, only the push-triggered `phase4-session-sweep-rejection` run on the exact merge SHA is authoritative.

- [ ] Require tests and Phase 3 acceptance green on the exact merged-main SHA.
- [ ] Require all 18 EXP-006 matrix jobs SUCCESS.
- [ ] Download all 18 artifact ZIPs and independently verify GitHub-reported ZIP SHA-256 against local bytes.
- [ ] Require each ZIP to contain exactly `benchmark.json` and `manifest.json`; verify inner manifest SHA/size.
- [ ] Require protocol `fmp-phase4-session-sweep-rejection-grid-v1`, exact code commit, symbol/timeframe/split identity, accepted Phase 2 processed-manifest SHA, schema version, frozen grid, cost/risk identities, and exact split bounds.
- [ ] Require exactly 162 total configuration rows and zero final-test rows.
- [ ] For every fixed pair/timeframe/split/buffer, require candidate SHA/count/reason counts identical across 0.2/0.5/1.0 costs.
- [ ] Reconcile candidate accounting/backtest trade/rejection counts using the established Phase 4 audit pattern.

## Task 9: Frozen promotion screen and experiment closure

- [ ] At 0.2 pip, evaluate each of the 27 pair/timeframe/buffer points. A survivor must have net return >0, expectancy/trade >0, and PF>1 on both development and validation for the same buffer.
- [ ] For baseline survivors only, evaluate predeclared 0.5-pip robustness, neighboring-buffer stability, calendar/subperiod concentration, sample size, max drawdown, and top-winner dependence. Treat 1.0 pip as diagnostic.
- [ ] Do not expand parameters or invent rescue rules after results.
- [ ] Write `docs/phase4-session-sweep-rejection-evidence.md`, append the next outcome decision to `docs/decision-log.md`, and update `docs/project-state.md` with PASS/PROMOTE or FAIL/REJECT while preserving all prior candidate identities and locks.
- [ ] Add/update state tests; merge closure source-free only after unit/Phase3 green and Phase1 source-capable checks skip.
- [ ] Because EXP-006 is the sixth/final planned baseline family, stop before any final-test access, Phase 4 checkpoint creation, or Phase 5 transition. Those require a separate explicit promotion/final-test authorization decision.
