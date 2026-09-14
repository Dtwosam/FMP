# EXP-20260914-006 — Session High/Low Sweep-Rejection Evidence

**Experiment result:** FAIL  
**Conclusion:** REJECT  
**Protocol decision:** DEC-026 — APPROVED  
**Outcome decision:** DEC-027 — APPROVED
**Final-test touched?: NO**

## Authoritative execution

- implementation / benchmark commit: `120348d4a5df806f674551590610b216a9bc33ac`
- merged-main tests run: `34895426082` — SUCCESS; unit tests, workflow YAML validation, and compile PASS
- unchanged Phase 3 acceptance run: `34895426066` — SUCCESS
- authoritative Phase 4 benchmark workflow: `phase4-session-sweep-rejection`
- benchmark run: `34895426037` — SUCCESS
- benchmark protocol: `fmp-phase4-session-sweep-rejection-grid-v1`
- matrix: 3 pairs × 3 timeframes × development/validation = 18/18 cells successful
- benchmark rows: 162/162 independently inspected
- independent audit errors: zero
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive

The benchmark used only the accepted Phase 2 processed artifacts. It did not acquire source data, mutate raw data, access the final-test split, or introduce broker/live or real-money execution.

## Accepted processed-data identities

- EURUSD: `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`
- GBPUSD: `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`
- USDJPY: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

## Authoritative artifact registry

Each artifact is a ZIP containing `benchmark.json` and `manifest.json`. GitHub's recorded SHA-256 matched the independently recomputed ZIP SHA-256 in every cell.

| Pair | TF | Split | Artifact ID | ZIP SHA-256 |
| --- | --- | --- | ---: | --- |
| EURUSD | 5m | development | `10369332015` | `d9e16f5c01c5b4f2d21ebaca6a756c2be8ebeb10c848558437853c5590e29b2e` |
| EURUSD | 5m | validation | `10369155684` | `905eb5f4bc75e07283c7eefbe026a594b487524f061ade93e45d30b46a249ce7` |
| EURUSD | 15m | development | `10368307661` | `16054915c34bb6c300faa24960bee6b0cc9073524568b87126f03492b01ac588` |
| EURUSD | 15m | validation | `10369130320` | `eb3cb2fdc1724f0c5a7f4af368f847e637475f1f4ef20b15cf1a507d58a1d567` |
| EURUSD | 1h | development | `10368821109` | `3e4eb64e8df49de719655e785b0820dffb5078d649071d6e28e397ad277bb428` |
| EURUSD | 1h | validation | `10369030816` | `754ffc97d9e288548557c42c4706257acb9bc3dc7c217c89bc51747726bdd593` |
| GBPUSD | 5m | development | `10368274088` | `1cfbd9792433db23461a0f21fef63f166daf118b1ec9632ccbb3e9e235a13c2a` |
| GBPUSD | 5m | validation | `10368991246` | `9ecb0d852a8068f8af9edf71f2b9bd867c8c7c85a10eddd2754b3d8d6e9a72ef` |
| GBPUSD | 15m | development | `10368895678` | `243faf8115a15993ae970b2c498f5e5ce3072e2d878a7ba8faf4374bada372bd` |
| GBPUSD | 15m | validation | `10369036032` | `05d91f92a989783589b8ebcf8a6ab0c5cee9cee27070ffda6befdfa9c6edfde9` |
| GBPUSD | 1h | development | `10368179967` | `37f902eb7e3ed7e8908f535e5d382efc75034ee4cc5bda1e189338fc3d88c45d` |
| GBPUSD | 1h | validation | `10368695498` | `e87e0a39bf4cf7178ac84313ac61bf38b82145116d2a0232abcdc1146823ee2c` |
| USDJPY | 5m | development | `10368447425` | `75a545f5f139fc5fe999bd5de1a2eef81d6d24142f398b72bfd0e4cbd4ed23df` |
| USDJPY | 5m | validation | `10369270479` | `67b849c38308c1c447e735f256d93ce500f88bd229729b3bfbabdce32c36832e` |
| USDJPY | 15m | development | `10368376191` | `d759020dd345ad025c32ce75bcaa040e03ec7d7f42f8c925e7403bf8441bfa9f` |
| USDJPY | 15m | validation | `10368880876` | `fe2177853d8576b7a825e723c6ead26b60d1d16f8564730fe9bb52974d8886bb` |
| USDJPY | 1h | development | `10368515859` | `61b3bce0f0e66e0f282489ec5e149a1927454a65b386285914b80000da4996a4` |
| USDJPY | 1h | validation | `10368224520` | `1e08fa77389328d2913f266c1254f0cdd8013e377bc3cbcd6d685f48d5f21e64` |

## Independent integrity verification

The independent verifier checked all 18 ZIPs and all 162 configuration rows and found zero discrepancies across:

- outer ZIP SHA-256 versus the GitHub artifact digest;
- inner benchmark SHA-256 and byte size from `manifest.json`;
- exact code commit, benchmark protocol, strategy family/version, canonical schema, symbol, timeframe, chronological split, and accepted processed-manifest identity;
- exact frozen grid order of buffers `0`, `2`, `5` pips × adverse slippage `0.2`, `0.5`, `1.0` pips;
- requested risk fraction `0.0025`, starting equity `$100,000`, zero commission, zero financing, and exact Phase 3 risk/cost identity;
- candidate SHA/count/reason-count reuse across all three cost scenarios for a fixed cell/buffer;
- candidate/rejection/trade accounting, expectancy, profit factor, net PnL, net return, and explicit costs;
- absence of any final-test split in the evidence.

## Frozen 0.2-pip promotion screen

Exactly **zero of 27 pair/timeframe/buffer points** satisfy the predeclared gate on both development and validation. Therefore EXP-006 has no baseline survivor and no configuration proceeds to robustness-based promotion.

There is one development-only qualifier and two validation-only qualifiers; each fails the required chronological two-split gate:

| Point | Development | Validation | Outcome |
| --- | --- | --- | --- |
| USDJPY 5m / 2-pip buffer | +1.9167% return; +$5.6874 expectancy; PF 1.0282; 337 trades; 7.6380% max DD | -15.4056% return; -$64.1899 expectancy; PF 0.6706; 240 trades; 16.7821% max DD | fails validation decisively |
| USDJPY 1h / 2-pip buffer | -4.0619% return; -$7.6066 expectancy; PF 0.9438; 534 trades; 6.5384% max DD | +0.5797% return; +$2.0779 expectancy; PF 1.0155; 279 trades; 8.8471% max DD | fails development |
| USDJPY 1h / 5-pip buffer | -0.3861% return; -$1.3405 expectancy; PF 0.9890; 288 trades; 3.8172% max DD | +0.2743% return; +$1.5853 expectancy; PF 1.0132; 173 trades; 4.7239% max DD | fails development |

Every other 0.2-pip point also fails at least one split. The clearest apparent development edge, USDJPY 5m / 2 pips, reverses sharply in validation rather than generalizing.

## Cost and robustness handling

DEC-026 authorizes downstream 0.5-pip, neighboring-buffer, subperiod, sample-size, drawdown, and top-winner robustness review only for baseline survivors. Because there are zero survivors at 0.2 pip, no 0.5-pip or 1.0-pip result may rescue a failed point and no post-result parameter expansion is permitted. The complete 0.5/1.0 cost rows remain preserved as benchmark evidence rather than a retuning surface.

## Conclusion

`EXP-20260914-006` is **FAIL / REJECT**. No session high/low sweep-rejection configuration is promoted.

The failure is not an implementation or evidence-quality failure: the authoritative merged-main workflow completed all 18 cells successfully and the independent 162-row audit found zero integrity or accounting errors. The family fails because no exact predeclared buffer clears the development-and-validation profitability gate at baseline costs.

The two existing serious Phase 4 candidates remain frozen unchanged: **EXP-001 USDJPY 15m / 5-pip / 1.5x session breakout** and **EXP-005 USDJPY 1h / 2.0x / fixed 1.0R volatility breakout**. No EXP-006 parameter widening, alternate reference session, extra buffer, target/stop retuning, or rescue rule is authorized.

This completes benchmarking of all six planned baseline families. Phase 4 still requires its explicit acceptance/checkpoint review; the final untouched test remains locked and is not authorized by this rejection. Phase 5, broker/live integration, and real-money trading remain locked pending their governing gates.