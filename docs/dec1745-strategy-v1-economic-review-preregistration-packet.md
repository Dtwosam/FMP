# DEC-1745 — Pre-register the economic tests before considering Strategy V1

**DRAFT / NEVER MERGE / NEVER PROMOTE — SOURCE-ONLY STRATEGY REVIEW TEMPLATE.**

## Purpose and non-goals

The current project is still Phase 8A annual pattern discovery. A machine-readable annual readiness graph (DEC-1742/1744), pre-authority proofs (#779/#820/#821), and 6,000+ source-defined methods do **not** imply a viable forex strategy. This document provides a **future research-and-risk review template**, not a current economic result, a profitability target, a portfolio suggestion or execution permission.

The governing discovery method is DEC-268/DEC-469: independent 2015–2025 annual pattern catalogues plus the approved 2026-to-2026-08-20 partial segment, including unsuccessful patterns, **before** cross-year pattern comparisons and Strategy V1 selection. Historical 2015–2022 is accepted through 2022 run384. **2023 run385/attempt1 remains blocked**, so none of the cross-year measurements below can honestly be filled from this draft.

## Separate review decisions — no automatic advancement

1. **Independent administrative gate:** effective exclusive no-bypass reviewed ref/SHA/workflow/runtime controls, three-job precheckout/preinstall/preaccess admission, privileged OS isolation, fresh one-shot annual inventory and separate exact run385 human decision. A green CI test or draft PR is not sufficient.
2. **Annual discovery acceptance:** independently freeze each segment, every one of the 18 cells, positive and negative patterns, coverage, data quality, timestamp identity and source provenance. Never skip a year to accelerate promotion.
3. **Cross-year candidate synthesis:** pre-register *how* stable patterns will be matched, how researcher choices and multiple comparisons are counted, what counts as a recurrence/failure, and how candidate selection will work. Do not optimize thresholds on a final untouched evaluation segment.
4. **Economic and risk review:** below are mandatory **categories**, but **numerical pass thresholds remain unset** until independently registered *before* seeing strategy-dependent results. Avoid after-the-fact chosen threshold lines.
5. **Frozen Strategy V1:** if a candidate survives, record an immutable strategy identity, risk/execution rules and a genuine fresh forward-test design. Phase 8B order-impossible shadow requires separate permission.
6. **Subsequent phases:** separately review fixed-version demo fills, execution failures and reconciliation, then Phase10 readiness. **Only an explicit Phase11 human approval can authorize real-money risk**.

## Required review evidence

| Evidence group | How to examine it | Status now |
| --- | --- | --- |
| `pre_registered_hypothesis_space` | pattern family lineage, all tested candidates and search count, registration date before strategy selection | **NOT EVALUATED** |
| `time_safe_signal_and_execution` | signal known at prior permissible timestamp, bid/ask side, earliest fill, ambiguity policy | **NOT EVALUATED** |
| `complete_annual_pattern_catalogue` | all 2015–2025 annual patterns and 2026 partial segment independently accepted before cross-year aggregation | **NOT EVALUATED** |
| `negative_pattern_and_failure_years` | negative candidates, years without a recurrence, reversals and unfavorable regimes included | **NOT EVALUATED** |
| `multiplicity_and_winner_selection` | predefined correction or honest uncertainty bound for all trials, researcher degrees of freedom disclosed | **NOT EVALUATED** |
| `independence_and_uncertainty` | appropriate block or cluster resampling respecting serial dependence; interval for net expectancy | **NOT EVALUATED** |
| `trade_support_and_pnl_concentration` | trade counts, effective sample size, winning-outlier concentration, by-year/by-pair decomposition | **NOT EVALUATED** |
| `costs_under_adverse_conditions` | spread, slippage, commissions, financing, adverse cost distributions and break-even sensitivity | **NOT EVALUATED** |
| `portfolio_usd_correlation_and_exposure` | cross-pair correlated USD risk, net/leverage, tail co-movement and overlap | **NOT EVALUATED** |
| `drawdown_and_tail_risk` | worst episodes, loss runs, gap/rollover tail exposure, capital preservation under stress | **NOT EVALUATED** |
| `execution_and_capacity` | market hours, order type, fill assumption, market impact, rejections, operational failure response | **NOT EVALUATED** |
| `holdout_contamination_accounting` | document historical windows already seen by Phase7 and do not re-label as untouched final test | **NOT EVALUATED** |
| `immutable_strategy_v1_spec` | exact rule version, entry exit/no-trade, risk sizing, freeze hash and selection decision | **NOT EVALUATED** |
| `prospective_order_impossible_shadow` | separately approved read-only fresh quotes; forward record cannot place any order | **NOT EVALUATED** |
| `separate_demo_live_decisions` | independent demo reconciliation, Phase10 review and explicit Phase11 real money authorization | **NOT EVALUATED** |

Each group has status `NOT_EVALUATED`, `evidence_ref=null` and `signoff=null` in the companion JSON. Do **not** turn a checkbox into accepted economic proof without independent underlying artifacts and qualified review. Rejection and more-data-needed must remain valid outcomes.

## Known benchmark, not Strategy V1 results

The earlier frozen Phase 7 session breakout benchmark reported aggregate historical **net returns** of +0.757266% at 0.2-pip slippage, +0.262176% at 0.5-pip, and **−0.562118% at 1.0-pip** (199 historical trades). Those observations are cost-sensitive and **not** current income, an approved Phase 8A strategy, or a slippage break-even forecast. The Phase 7 tested years and any other historically inspected windows must be logged as *previously seen*; they may not silently become a pristine final holdout for new strategies.

Do not fill `profitability_measurements` from the historical benchmark, assert `annual_catalogues_complete`, or generate an approved strategy identity. Their `null` and `false` states are deliberate, not missing work the test suite is entitled to guess.

## Roles, execution boundary and acceptance

**Administrator/security reviewer:** supply authentic continuous ref lock, independently approved SHA/runtime and runner-host OS evidence; do not place secrets in PRs. **Annual research custodian:** independently accept each year's source evidence and complete inventory. **Researcher:** provide pre-registered hypotheses, all trial counts and after-cost statistics. **Independent risk reviewer:** evaluate concentrated/correlated losses, tail risk, execution/ops and whether the candidate deserves *fresh* shadow, rather than inferring approval from CI.

**No automatic PASS.** In the absence of independently validated annual/Strategy V1 evidence, the only current disposition is `MORE_INDEPENDENT_EVIDENCE_REQUIRED`. Unknown metrics are `null`, not 0 and not claimed profit. Even a favorable future historical review would authorize neither Phase 8B nor demo nor Phase11 by itself.

Source context: `docs/research-testing-standard.md`, `docs/build-order.md`, `docs/phase7-walk-forward-evidence.md`, `docs/dec1715-economic-evidence-milestone-ledger.md`, `docs/dec1739-phase8a-economic-evidence-before-shadow.json` and `docs/dec1742-phase8a-blocked-dependency-graph.json`. **Issue #779, DEC-650/#820 and DEC-651/#821 still BLOCKED.**

Docs only. No new tests, production, parser, workflow, runner, ruleset, original/archived/protected data, annual dispatch/retry, trading strategy promotion, broker demo/live or real-money actions. Exact-head Phase 3/full historical/general CI and independent qualified review still required.
