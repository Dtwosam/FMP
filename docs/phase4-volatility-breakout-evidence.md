# EXP-20260914-005 — Rolling Volatility-Breakout Evidence

**Experiment result:** PASS  
**Conclusion:** PROMOTE one serious Phase 4 research candidate  
**Protocol decision:** DEC-024 — APPROVED  
**Outcome decision:** DEC-025 — pending evidence-closure merge  
**Final-test touched?: NO**

## Authoritative execution

- implementation / benchmark commit: `3bf36186900f5065e9e3ddced0305865433b9d69`
- merged-main tests run: `34888225240` — SUCCESS; unit tests, workflow YAML validation, and compile PASS
- unchanged Phase 3 acceptance run: `34888225252` — SUCCESS
- authoritative Phase 4 benchmark workflow: `phase4-volatility-breakout`
- benchmark run: `34888225242` — SUCCESS
- benchmark protocol: `fmp-phase4-volatility-breakout-grid-v1`
- matrix: 3 pairs × 3 timeframes × development/validation = 18/18 cells successful
- benchmark rows: 162/162 independently inspected
- independent audit errors: zero
- development: 2015-01-01 through 2020-12-31 inclusive
- validation: 2021-01-01 through 2023-12-31 inclusive
- final untouched test: 2024-01-01 through 2026-08-20 inclusive

The benchmark used only the accepted Phase 2 processed artifacts and did not acquire source data. The result-producing workflow had read-only repository/action permissions, no OIDC permission, and no Dukascopy/Supabase acquisition surface.

## Accepted processed-data identities

- EURUSD: `fd7676282e6e667c39754b09b43a43288a0a877fec588cd2601a601e2b0edf6a`
- GBPUSD: `a6ee73e94781f48a43f2792328528d242455d4f7f4f2e0a5760446df21ba4d94`
- USDJPY: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`

## Authoritative artifact registry

Each artifact is a ZIP containing exactly `benchmark.json` and `manifest.json`. GitHub's recorded SHA-256 matched the independently recomputed ZIP SHA-256 in every inspected cell.

| Pair | TF | Split | Artifact ID | ZIP SHA-256 |
| --- | --- | --- | ---: | --- |
| EURUSD | 5m | development | `10366467996` | `f784c348b6e9bf3284e89693f75e04d95044739bfc5670f4aefb8f63c95aa74d` |
| EURUSD | 5m | validation | `10365422515` | `5b54cf08da3c44322e42b5d49a499e7d27a5c6742065600e9e2590b105167c8d` |
| EURUSD | 15m | development | `10366465911` | `261d7dc340c808975e85f91a22e82755bf52ea553812e126c006ebecb9df5509` |
| EURUSD | 15m | validation | `10366074161` | `b584a48f8b11961641dac60578ae62cfacb5f4b2738e2cd6bbe16a240653acbf` |
| EURUSD | 1h | development | `10365363928` | `2bee81a72b156cc29e56f87e2e56d41c0781870967a732d817b9f5bda305bfc4` |
| EURUSD | 1h | validation | `10365199306` | `be43932d1f0014fffccdf40af18bd5dac2a0894534ab4eae7980360a04f6090a` |
| GBPUSD | 5m | development | `10367085422` | `04d6d82441bcc9ff42da2bc3efebf0cef1d5699d192b707dd198c1ace2ac6fa3` |
| GBPUSD | 5m | validation | `10366073796` | `8285912c4c87280221a1b0537471a398864a43aa376ab66ec8460c5f4f0c4bee` |
| GBPUSD | 15m | development | `10365703022` | `dd4846e89de1a155fc20caaf97f5e4b32227a07e8a2f6ade1e9dec64bbe502d1` |
| GBPUSD | 15m | validation | `10365093476` | `44e0e4f6ad4a3ff5dd3c631769c38942f4c69fbca5e000dd0a02b0edd9740b79` |
| GBPUSD | 1h | development | `10365404922` | `eb5f8149ae889a09849e07b23d442c2cd833355d66819eae69020fd4687c84ac` |
| GBPUSD | 1h | validation | `10365477737` | `cd2f0564de3a63cfd6c153ff9206e11e2d6908618e5a47423ab54cea463c3a72` |
| USDJPY | 5m | development | `10365924547` | `115f05fa1061f1bd1aea80e246e2a4a1b14abbcc7994c3350a009b64b6e53e87` |
| USDJPY | 5m | validation | `10365703342` | `57bc214045f032f601f1536690f78a03187317fb9eafb2b6c30c9b350e77ae1e` |
| USDJPY | 15m | development | `10365846931` | `47b2d1c1ee5863d62fbc6d35fbcc19984031ff4c46f89bd0933f13153a7cb443` |
| USDJPY | 15m | validation | `10366201648` | `a485eb22d27c7acfa47e6ca4cf7c7cda359338931725f6d33567d7025eb4a960` |
| USDJPY | 1h | development | `10366003403` | `1d5714dc2257db353698ebe8419c10f4f01ecaf2134c161ebc4433b3a1946014` |
| USDJPY | 1h | validation | `10365463960` | `72cce7e015dbefab9091c3b6895ea1ce1ca83f558b5852eca883b451af67e4ff` |

## Independent integrity verification

The independent verifier checked all 18 ZIPs and all 162 configuration rows. It found zero discrepancies across:

- outer ZIP SHA-256 versus GitHub artifact digest;
- exact ZIP membership (`benchmark.json`, `manifest.json` only);
- inner benchmark SHA-256 and byte size;
- code commit, strategy family/version, benchmark protocol, canonical schema, symbol, timeframe, split, and accepted processed-manifest identity;
- exact frozen grid order of multipliers `1.0`, `1.5`, `2.0` × slippage `0.2`, `0.5`, `1.0`;
- requested risk fraction `0.0025`, starting equity `$100,000`, zero commission, zero financing, and exact slippage identity;
- candidate SHA/count/reason-count reuse across all three cost scenarios for a fixed cell/multiplier;
- candidate reason accounting and `trade_count + rejection_count == candidate_count` on every row;
- absence of any final-test split in the benchmark evidence.

## Frozen 0.2-pip promotion screen

Exactly **one of 27 pair/timeframe/multiplier points** satisfies the predeclared baseline gate on both development and validation:

**USDJPY 1h / 2.0x range-expansion multiplier**.

At 0.2-pip adverse slippage:

| Split | Trades | Net return | Expectancy/trade | Profit factor | Max DD | Sharpe | Sortino |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| development | 596 | +11.4235% | +$19.1670 | 1.2321 | 2.5228% | 0.8334 | 0.9761 |
| validation | 364 | +5.5971% | +$15.3766 | 1.1931 | 1.9853% | 0.7727 | 0.9921 |

No EURUSD or GBPUSD point survives the baseline development-and-validation gate. No USDJPY 5m or 15m multiplier survives it either.

## Cost robustness

The selected USDJPY 1h / 2.0x point remains positive on both splits at the required 0.5-pip robustness scenario:

| Slippage | Dev return | Dev exp. | Dev PF | Val return | Val exp. | Val PF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2 pip | +11.4235% | +$19.1670 | 1.2321 | +5.5971% | +$15.3766 | 1.1931 |
| 0.5 pip | +6.5350% | +$10.9648 | 1.1297 | +3.2953% | +$9.0530 | 1.1111 |
| 1.0 pip | -1.1416% | -$1.9154 | 0.9782 | -0.4304% | -$1.1825 | 0.9860 |

The 1.0-pip diagnostic therefore fails on both splits. This is a material cost-sensitivity limitation, but DEC-024 explicitly defines 1.0 pip as diagnostic rather than a universal promotion condition.

## Neighboring-multiplier and timeframe stability

Neighbor stability is the main weakness of the promoted point.

For USDJPY 1h at 0.2 pips:

- 1.0x: development -10.3040%, PF 0.9175; validation +1.1260%, PF 1.0180.
- 1.5x: development -0.9317%, PF 0.9896; validation +7.1428%, PF 1.1512.
- 2.0x: development +11.4235%, PF 1.2321; validation +5.5971%, PF 1.1931.

At 0.5 pips, both 1.0x and 1.5x are negative in development; 1.0x is also negative in validation. The same 2.0x point does not have cross-timeframe confirmation: USDJPY 15m / 2.0x is -3.9955% development at baseline despite +6.4811% validation, while USDJPY 5m validation is negative for every multiplier.

This parameter/timeframe isolation is retained as an explicit weakness rather than hidden by post-result expansion or retuning.

## Calendar distribution, sample size, drawdown, and winner dependence

At baseline 0.2-pip slippage, development is positive in every calendar year:

- 2015: +$1,290.10, 119 trades
- 2016: +$958.05, 66 trades
- 2017: +$707.52, 102 trades
- 2018: +$4,341.56, 87 trades
- 2019: +$1,227.23, 120 trades
- 2020: +$2,899.06, 102 trades

The largest positive development year, 2018, contributes about 38.0% of positive annual net PnL. Validation is mixed but not dependent on a single year:

- 2021: -$1,028.29, 139 trades
- 2022: +$4,397.49, 110 trades
- 2023: +$2,227.89, 115 trades

2022 contributes about 66.4% of validation positive annual net PnL. Validation therefore has a real 2021 regime weakness, while 2022 and 2023 both remain positive.

The sample is substantial: 596 development trades and 364 validation trades. Baseline max drawdown is 2.5228% development and 1.9853% validation; at 0.5-pip stress it is 2.7079% and 2.5944% respectively.

Winner dependence is very low. Measured from positive realized reward/risk values, the largest winner contributes about 0.44% of development positive R and 0.75% of validation positive R; the top three contribute about 1.30% and 2.22% respectively.

## Conclusion

`EXP-20260914-005` is **PASS / PROMOTE**. Retain **USDJPY 1h, 2.0x range-expansion multiplier, fixed 1.0R target** unchanged as a serious Phase 4 research candidate.

Promotion is justified because the exact predeclared point clears the baseline gate on both chronological splits with substantial margin, remains positive under 0.5-pip adverse slippage on both splits, has a large sample, low drawdown, positive results in all six development years, two of three positive validation years, and minimal top-winner dependence.

Promotion is not a claim of deployment readiness. Neighboring multipliers and adjacent timeframes do not confirm the development edge, validation is negative in 2021, and 1.0-pip cost stress fails. Those weaknesses remain attached to the candidate for later cross-family selection and any eventual final-test decision.

The existing frozen USDJPY 15m session-breakout / 5-pip / 1.5x candidate remains unchanged; EXP-005 adds a second serious Phase 4 candidate rather than superseding it. No post-result parameter expansion is authorized. Phase 4 remains ACTIVE and the next baseline family is the sixth planned **session high/low sweep/rejection** family. The 2024-01-01 through 2026-08-20 final test, Phase 5, broker/live integration, and real-money trading remain locked.