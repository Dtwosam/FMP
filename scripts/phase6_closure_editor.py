from pathlib import Path

state_path = Path("docs/project-state.md")
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "**Phase status:** ACTIVE\n**Next milestone:** Implement and execute frozen `EXP-20260915-007`; final-test data remains locked",
    "**Phase status:** PASS\n**Next milestone:** Create immutable Phase 6 checkpoint; Phase 7 remains UNSTARTED and final-test data remains locked",
    1,
)
marker = "## Phase 6 — ACTIVE"
if marker not in state:
    raise SystemExit("Phase 6 ACTIVE section not found")
prefix = state.split(marker, 1)[0]
phase6 = """## Phase 6 — PASS

DEC-031 remains the frozen statistical / ML filter protocol for `EXP-20260915-007`. DEC-032 records the completed experiment outcome and Phase 6 acceptance without changing the protocol, strategy parameters, features, models, thresholds, gates, or Phase 3 execution/risk semantics.

- Candidate A: USDJPY 15m session breakout, 5-pip buffer, 1.5x target range — rule baseline retained unchanged.
- Candidate B: USDJPY 1h volatility breakout, 2.0x range expansion, fixed 1.0R target — rule baseline retained unchanged.
- feature checkpoint: `fmp-v1-phase5-features` at `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`
- feature schema: `fmp-feature-v1`, exact 48 feature values plus signal direction for modeling
- accepted USDJPY processed-manifest SHA-256: `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`
- experiment: `EXP-20260915-007` — PASS / ML overlay REJECT
- authoritative run: `34966406652` on `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c` — SUCCESS
- session-breakout evidence: artifact `10395810196`, ZIP SHA-256 `36cb9f80ca043da23250669dd974036eb9fb985c3f7f9ffd7844b9d99c96073d`; `ALL_NULL_FIT_COLUMN` on `minutes_since_new_york_open`; both models fail closed; all six variants not evaluated; `NO_ML_CHALLENGER`; validation unopened
- volatility-breakout evidence: artifact `10395670751`, ZIP SHA-256 `0cf71a4d725fb1e609a512bb95aa13e4ad8771ae2b5864dd09e2833fe160a8d2`; both models fit exactly once; all six variants fail the selection gate; `NO_ML_CHALLENGER`; validation unopened
- fit: 2015-01-01 through 2018-12-31 inclusive
- selection: 2019-01-01 through 2020-12-31 inclusive
- external validation: 2021-01-01 through 2023-12-31 inclusive; not opened because neither strategy produced a qualifying selection-period challenger
- no refit after selection; no post-result threshold widening or model/strategy retuning
- Final-test touched: NO
- checkpoint: PENDING (`fmp-v1-phase6-models`)

Phase 6 is formally PASS under DEC-032 because both frozen strategies completed the predeclared deterministic leakage-safe experiment and all negative evidence was preserved. No ML filter is promoted. Normal Phase 6 tooling still cannot open any required source or feature partition reaching 2024-01-01 or later. Phase 7 remains UNSTARTED. The final-test period, broker/live/demo integration, and real-money trading remain locked; DEC-008 remains unchanged.
"""
state_path.write_text(prefix + phase6, encoding="utf-8")

decision_path = Path("docs/decision-log.md")
decision = decision_path.read_text(encoding="utf-8")
index_old = "- DEC-031 — Phase 6 statistical / ML filter protocol — APPROVED\n"
index_new = index_old + "- DEC-032 — Phase 6 statistical / ML filter experiment outcome and acceptance review — APPROVED\n"
if index_old not in decision:
    raise SystemExit("DEC-031 index line not found")
if "- DEC-032 —" not in decision:
    decision = decision.replace(index_old, index_new, 1)
if "## DEC-032 — Phase 6 statistical / ML filter experiment outcome and acceptance review" not in decision:
    decision += """

## DEC-032 — Phase 6 statistical / ML filter experiment outcome and acceptance review

**Date:** 2026-09-15
**Status:** APPROVED

Authoritative `phase6-ml-filter` run `34966406652` on exact merged-main SHA `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c` completed SUCCESS for both frozen `EXP-20260915-007` strategy cells. Each cell used the accepted Phase 2 USDJPY processed identity and Phase 5 `fmp-feature-v1` checkpoint, executed twice with byte-identical evidence, passed the pre-2024 evidence lock, and uploaded an independently audited artifact. Final-test touched: NO.

For USDJPY 15m `session_breakout`, `minutes_since_new_york_open` is all-null across the 428 fit-period model rows. The DEC-031 preprocessing rule therefore fails closed with `ALL_NULL_FIT_COLUMN` for both frozen model families instead of inventing a fill value. Both models record zero fits, all six model/retention variants remain durable `NOT_EVALUATED_MODEL_FIT_FAILED` evidence, `selected_variant = NO_ML_CHALLENGER`, and validation is not opened.

For USDJPY 1h `volatility_breakout`, both frozen models fit exactly once on 374 fit rows with fit-only preprocessing and cutoffs and no refit. All six predeclared selection variants fail the frozen all-conditions financial gate on 2019-2020. In particular, `net_return_beats_baseline` is false for every variant. No variant qualifies for the deterministic tie-break, so `selected_variant = NO_ML_CHALLENGER` and validation is not opened.

No strategy parameter, feature definition, model family, hyperparameter, retained fraction, cutoff rule, selection gate, validation gate, risk rule, or execution semantic was changed in response to the results. The failed first orchestration run is debugging history only and its successful volatility output was not used for selection decisions. Both authoritative outcomes preserve negative evidence and reject the optional ML overlay while retaining the two frozen Phase 4 rule baselines unchanged.

Consequences: `EXP-20260915-007` is complete with experiment status PASS and ML conclusion REJECT. Phase 6 is formally PASS. Checkpoint `fmp-v1-phase6-models` is to be created only at the verified acceptance-closure merge commit after fresh source-free merged-main tests and Phase 3 acceptance succeed. Phase 7 remains UNSTARTED. The untouched 2024-01-01 through 2026-08-20 final-test period remains locked; broker/live/demo integration and real-money trading remain locked; DEC-008 remains unchanged. Detailed evidence is in `docs/phase6-ml-filter-evidence.md`.
"""
decision_path.write_text(decision, encoding="utf-8")

experiment_path = Path("docs/experiment-log.md")
experiments = experiment_path.read_text(encoding="utf-8")
heading = "### EXP-20260915-007 — Phase 6 statistical / ML candidate filters"
if heading not in experiments:
    experiments += """

### EXP-20260915-007 — Phase 6 statistical / ML candidate filters

- Date: 2026-09-15
- Status: PASS
- Hypothesis: A predeclared supervised outcome model may filter lower-quality entries from either frozen Phase 4 serious rule candidate and improve financial quality without changing the strategy, execution, or fixed-risk contract. No model improvement was assumed.
- Code commit: `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c`
- Data manifest/version: Phase 5 `fmp-feature-v1` checkpoint `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`; accepted USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d`; authoritative Phase 5 USDJPY 15m artifact `10374600839` ZIP `2e9b19935fc2699c94e5c3b91675c332892da9448e994438e479cf501e3c6215`; USDJPY 1h artifact `10374645600` ZIP `3db4d9d4fd4613c9e91f4c3fc1d815750038e33ea993608513066cec53aa617f`.
- Pair(s): USDJPY
- Timeframe(s): 15m session breakout and 1h volatility breakout
- Data range: accepted pre-2024 data only; fit 2015-2018 and selection 2019-2020 were opened. The predeclared 2021-2023 validation split remained unopened because neither strategy produced a qualifying selection-period challenger.
- Train period: fit 2015-01-01 through 2018-12-31 inclusive; selection 2019-01-01 through 2020-12-31 inclusive
- Validation period: 2021-01-01 through 2023-12-31 inclusive, gated and not opened
- Final-test touched?: NO
- Strategy/model: unchanged USDJPY 15m session-breakout 5-pip/1.5x rule and USDJPY 1h volatility-breakout 2.0x/1.0R rule; exact L2 logistic regression and shallow histogram gradient boosting challengers.
- Features: exactly 48 frozen `fmp-feature-v1` values plus signal direction; exact observation/availability join; no outcome/PnL/future feature input.
- Parameters/search space: exactly two model families × retained fractions 0.75, 0.50, and 0.25 per strategy; cutoffs derived from fit scores only; no post-result widening, extra model, or rescue search.
- Random seed (if relevant): `20260915`
- Spread/cost model: historical BID/ASK spread; zero commission; zero financing.
- Slippage model: 0.2 pips per fill for selection; 0.5-pip validation robustness only for a selected challenger; 1.0 pip diagnostic only. Validation was not opened because no challenger survived selection.
- Risk assumptions: unchanged Phase 3 contract: 0.25% requested risk, 0.50% hard per-trade max, 1.00% simultaneous max, 1.50% UTC day-start realized-loss halt.
- Trade count: selection rule baselines were 192 session-breakout trades and 222 volatility-breakout trades; no filtered candidate was promoted.
- Net return after costs: selection rule baselines were +3.8558% session breakout and +3.8457% volatility breakout at 0.2-pip adverse slippage. No session ML variant was fit; all six volatility filtered variants were below the volatility baseline net return.
- Expectancy/trade: selection rule baselines +$20.0822 session breakout and +$17.3228 volatility breakout. Best volatility filtered expectancy was +$21.0354 for logistic 0.50, but that variant still failed the all-conditions gate because its +2.7136% net return was below baseline.
- Profit factor: selection rule baselines 1.3010 session breakout and 1.2014 volatility breakout. No session model fit; volatility filtered PF ranged 0.9703 to 1.2101 and did not produce a qualifying all-conditions variant.
- Max drawdown: selection rule baselines 1.4390% session breakout and 1.4105% volatility breakout; drawdown improvement alone could not rescue a variant that failed another frozen selection condition.
- Key subperiod results: no validation subperiod result exists because DEC-031 forbids validation from rescuing a strategy without a qualifying selection-period challenger.
- Robustness/cost sensitivity: validation and the 0.5-pip robustness gate remained unopened for both strategies; no 1.0-pip diagnostic result was used.
- Result summary: authoritative run `34966406652` completed SUCCESS with double execution, byte-identical evidence, and locked pre-2024 coverage. Session breakout failed closed for both models on `ALL_NULL_FIT_COLUMN` / `minutes_since_new_york_open`, leaving all six variants not evaluated. Volatility breakout fit both models once, but all six variants failed selection and every variant had `net_return_beats_baseline = false`. Audited artifacts are session `10395810196` / ZIP `36cb9f80ca043da23250669dd974036eb9fb985c3f7f9ffd7844b9d99c96073d` and volatility `10395670751` / ZIP `0cf71a4d725fb1e609a512bb95aa13e4ad8771ae2b5864dd09e2833fe160a8d2`.
- Conclusion: REJECT
- Reason: neither frozen strategy produced a valid ML challenger under the predeclared selection protocol; `NO_ML_CHALLENGER` is the authoritative outcome for both.
- Follow-up: retain both frozen Phase 4 rule candidates unchanged, close Phase 6 as PASS because the deterministic leakage-safe experiment completed correctly with negative evidence preserved, create `fmp-v1-phase6-models` only after verified acceptance-closure merge, keep Phase 7 UNSTARTED, and keep the final-test period locked. Detailed evidence: `docs/phase6-ml-filter-evidence.md`.
"""
experiment_path.write_text(experiments, encoding="utf-8")
