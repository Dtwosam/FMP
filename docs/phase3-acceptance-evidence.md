# Phase 3 Backtester Acceptance Evidence

**Review date:** 2026-09-14  
**Phase:** Phase 3 — Backtesting Engine  
**Acceptance result:** PASS  
**Formal checkpoint:** `fmp-v1-phase3-backtester` (created only after this closure change merges and merged-main CI is green)

## Scope

This record closes the Phase 3 acceptance gate for the deterministic broker-independent backtesting engine. It does not start Phase 4, does not grant broker/live access, and does not change DEC-008 real-money lock.

The accepted implementation was introduced by PR #78 and the source-free merged-main acceptance runner by PR #79.

- implementation merge: `96ca80b3baae4de511b5b14eb6c2f9d4d723645b`
- acceptance-runner merge / evidence code commit: `f7d98676d40f9af67f2d6f6cde36b3a465f68741`
- formal merged-main test run: `34838682046`
- formal merged-main acceptance run: `34838682032`
- acceptance workflow: `phase3-acceptance`
- acceptance event: `push`
- acceptance branch: `main`
- acceptance conclusion: SUCCESS

The merge SHA `f7d98676d40f9af67f2d6f6cde36b3a465f68741` produced exactly two GitHub Actions workflow runs: `tests` and `phase3-acceptance`. No Phase 1 acquisition-capable workflow triggered for that SHA.

## Merged-main regression evidence

Run `34838682046` checked out exact main SHA `f7d98676d40f9af67f2d6f6cde36b3a465f68741`.

- workflow YAML validation: PASS
- `python -m unittest discover -s tests -v`: **300 tests, all PASS**
- `python -m compileall -q src tests`: PASS

The green suite includes the Phase 3 contracts, cost models, risk sizing/policy, execution semantics, chronological engine, deterministic reporting, hand-calculated acceptance tests, USDJPY sizing/PnL conversion, and acceptance-runner determinism tests, while retaining the Phase 1 and Phase 2 regression suite.

## Formal acceptance artifact

Run `34838682032` generated and uploaded:

- artifact ID: `10344943075`
- artifact name: `phase3-backtester-acceptance-f7d98676d40f9af67f2d6f6cde36b3a465f68741`
- compressed size: 23,487 bytes
- GitHub digest: `sha256:357152cef5118163f06f9d6166e7e02cdd7ed556a3de1c5723a6a6079bd6c4f0`
- independently recomputed ZIP SHA-256: `357152cef5118163f06f9d6166e7e02cdd7ed556a3de1c5723a6a6079bd6c4f0`
- artifact entries: 51 files total: one acceptance index plus 5 scenarios × 2 copies × 5 persisted backtest files

Independent inspection produced **zero validation errors**.

### Acceptance index identity

`acceptance-index.json` contains:

- protocol: `fmp-phase3-acceptance-fixture-v1`
- fixture ID: `phase3-merged-main-acceptance-v1`
- code commit: `f7d98676d40f9af67f2d6f6cde36b3a465f68741`
- scenario count: 5
- every scenario reports `bytes_equal: true`

Scenario manifest SHA-256 values, independently recomputed from persisted `primary/*/manifest.json` and matched to the repeat copy:

| Scenario | Manifest SHA-256 |
| --- | --- |
| `ambiguity` | `05489124b2967452a848ea256788118722e84d9ac1f1ab95ca3bda097b2890d3` |
| `daily-halt-reset` | `55f137cc57afc62ad7199631a8ec5aafd6e19a4b0cee9a67a44b37d9cdbe0006` |
| `long-cost` | `5196e7d9bd891081aabce284d588064a1d07113ac294ebc7c6b8329f6ed963ad` |
| `short-target` | `1d326bce2fd042a1ea909f1a2e2186da33e67f84f87291db56c77fc01a16bbf8` |
| `simultaneous-risk` | `9f162a9e46451084e460075f0abe36e6b3c9dc6fdf2e441939227f70f23803e4` |

For every scenario, independent inspection verified:

- primary and repeat `summary.json`, `trades.jsonl`, `rejections.jsonl`, `metrics.json`, and `manifest.json` are byte-identical
- each manifest protocol is `fmp-phase3-backtest-artifacts-v1`
- every manifest-listed artifact size matches the actual persisted bytes
- every manifest-listed SHA-256 matches a fresh digest of the persisted bytes
- summary trade/rejection/equity-checkpoint counts match the persisted records
- `backtest_engine_version` is `fmp-backtest-v1`
- `code_commit` is exact merged-main SHA `f7d98676d40f9af67f2d6f6cde36b3a465f68741`
- processed-data identity is `phase3-scripted-acceptance-data-v1`
- schema identity is `fmp-canonical-1m-v1`
- timeframe is `1m`
- decision config records fixture `phase3-merged-main-acceptance-v1` and the exact scenario name
- realized-equity checkpoints equal starting equity plus the cumulative persisted net PnL
- independently recomputed metrics match `metrics.json`

## Hand-calculated scenarios

### 1. LONG executable-side pricing and explicit costs

Scenario: `long-cost`.

- starting equity: $10,000
- default risk: 0.25% = $25
- reference entry: ASK `1.1002`
- stop: `1.0992`
- stop distance: `0.0010`
- units: `$25 / 0.0010 = 25,000`
- reference target exit: BID `1.1012`
- reference gross PnL: `(1.1012 - 1.1002) × 25,000 = $25.00`
- one-pip adverse entry slippage: execution `1.1003`
- one-pip adverse exit slippage: execution `1.1011`
- slipped PnL: `(1.1011 - 1.1003) × 25,000 = $20.00`
- slippage cost: `$25.00 - $20.00 = $5.00`
- commission rate: $30 per million units per execution side
- commission per side: `25,000 / 1,000,000 × $30 = $0.75`
- total commission: `$1.50`
- financing: `$0.00`
- net PnL: `$25.00 - $5.00 - $1.50 = $18.50`

Persisted trade and metrics match every value. Final realized risk equity is `$10,018.50`; total explicit cost is `$6.50`.

### 2. SHORT executable-side pricing

Scenario: `short-target`.

- reference entry: BID `1.1000`
- stop: `1.1010`
- units: 25,000
- target cover: ASK `1.0990`
- gross/net PnL: `(1.1000 - 1.0990) × 25,000 = $25.00`

Persisted trade direction is SHORT, exit reason is TARGET, and final realized risk equity is `$10,025.00`.

### 3. Conservative unresolved intrabar ambiguity

Scenario: `ambiguity`.

Both stop `1.0992` and target `1.1020` are reachable within the same post-entry bar. Persisted result is:

- exit reason: STOP
- `intrabar_ambiguous: true`
- executable-side exit reference: `1.0992`
- units: 25,000
- net PnL: `(1.0992 - 1.1002) × 25,000 = -$25.00`
- final realized risk equity: `$9,975.00`

This matches DEC-016's conservative STOP-wins policy.

### 4. Simultaneous-risk cap and stable decision ordering

Scenario: `simultaneous-risk`.

Decisions `A`, `B`, and `C` are eligible at the same timestamp and ordered by stable `decision_id`.

- `A` requests 0.50% of $10,000 = $50 risk and is accepted
- `B` requests another $50 and is accepted
- reserved risk reaches the exact 1.00% = $100 limit
- `C` would exceed the limit and is rejected with `SIMULTANEOUS_RISK`

Persisted trades are only `A` and `B`; persisted rejection is exactly `C / SIMULTANEOUS_RISK`. Both accepted positions close deterministically at end-of-data.

### 5. Daily realized-loss halt and next-UTC-day reset

Scenario: `daily-halt-reset` uses 0.50% requested risk per trade with starting day equity $10,000, so the daily halt threshold is `-1.50% × $10,000 = -$150.00`.

The four same-day stop losses are:

| Trade | Units | Net PnL | Cumulative day PnL | Realized risk equity |
| --- | ---: | ---: | ---: | ---: |
| `LOSS-1` | 25,000 | -$50.000 | -$50.000 | $9,950.000 |
| `LOSS-2` | 24,875 | -$49.750 | -$99.750 | $9,900.250 |
| `LOSS-3` | 24,750 | -$49.500 | -$149.250 | $9,850.750 |
| `LOSS-4` | 24,626 | -$49.252 | -$198.502 | $9,801.498 |

After `LOSS-3`, cumulative realized loss is `-$149.25`, so the halt is not yet active. After `LOSS-4`, cumulative loss is `-$198.502`, which is at or beyond the `-$150.00` threshold. The later same-day decision `HALTED` is therefore rejected with `DAILY_HALT`.

At the next UTC day boundary, the basis resets to current realized risk equity `$9,801.498`. `NEXT-DAY` is accepted, sized to 24,503 units, reaches its target, earns `$19.6024`, and closes at final realized risk equity `$9,821.1004`.

The persisted equity checkpoints exactly reproduce this sequence.

## Metrics recomputation

For all five scenarios, metrics were recomputed independently from persisted trades and realized-equity checkpoints using the frozen Phase 3 definitions. Recomputed values matched every persisted field, including:

- net PnL and net return
- trade count and win rate
- average win/loss and expectancy
- gross profit/loss and profit factor
- maximum realized-equity drawdown and fraction
- recovery factor
- winning/losing streaks
- slippage, commission, financing, and total explicit cost

No discrepancy was found.

## Required golden coverage review

The Phase 3 required golden tests in `docs/build-order.md` are satisfied:

| Required gate | Evidence | Result |
| --- | --- | --- |
| LONG buy at ask, exit at bid | `long-cost` artifact + `test_long_ask_entry_bid_target_exit_matches_hand_calculation` | PASS |
| SHORT sell at bid, cover at ask | `short-target` artifact + `test_short_bid_entry_ask_target_exit_matches_hand_calculation` | PASS |
| Stop hit | `ambiguity`, daily-loss artifacts, execution unit tests | PASS |
| Target hit | `long-cost`, `short-target`, `NEXT-DAY` | PASS |
| Both stop/target in one bar -> conservative documented outcome | `ambiguity` STOP + `intrabar_ambiguous=true` | PASS |
| JPY and non-JPY risk size math | merged-main USDJPY sizing/PnL tests plus EURUSD/GBPUSD artifacts | PASS |
| Daily halt | `daily-halt-reset` + merged-main risk/engine tests | PASS |
| Simultaneous-risk rejection | `simultaneous-risk` | PASS |
| Deterministic repeated-run equality | primary/repeat byte equality for every persisted file in all five scenarios | PASS |

The broader design acceptance requirements are also covered by the 300-test merged-main suite: timing/no-lookahead, exact risk boundaries, stop/target geometry, stop gaps, target gaps, same-bar ambiguity, adverse slippage direction, per-side commission, EOD side selection, exit-before-entry risk release, stable decision ordering, reason-code preservation, metrics math, manifest hashing, and deterministic serialization.

## Acceptance conclusion

The Phase 3 acceptance gate is PASS:

1. hand-calculated golden scenarios agree with the engine;
2. realistic bid/ask, slippage, commission, risk, daily-halt, and ambiguity semantics are regression-tested;
3. merged-main CI is green with 300 tests;
4. deterministic persisted artifacts were produced from merged `main`;
5. artifact ZIP digest, per-file SHA/size, repeated bytes, run identities, equity checkpoints, PnL, rejection codes, and metrics were independently verified with zero errors;
6. no Phase 1 acquisition-capable workflow triggered for the formal evidence merge SHA;
7. no source acquisition, raw mutation, Supabase write, broker/live path, Phase 4 strategy code, or real-money permission was introduced.

Checkpoint `fmp-v1-phase3-backtester` must point at the verified Phase 3 closure commit. Phase 4 remains unstarted and DEC-008 remains in force.
