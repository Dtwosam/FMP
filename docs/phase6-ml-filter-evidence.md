# Phase 6 Statistical / ML Candidate Filters — Acceptance Evidence

**Review date:** 2026-09-15
**Result:** PASS
**Decision:** DEC-032 — APPROVED
**Experiment:** `EXP-20260915-007`
**Checkpoint:** `fmp-v1-phase6-models` — CREATED at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`
**Final-test touched?: NO**

## Acceptance gate

DEC-031 explicitly permits Phase 6 to PASS whether an ML filter is promoted or all challengers are rejected, provided both frozen strategies complete the predeclared deterministic, leakage-safe experiment and failed variants remain evidence. That gate is satisfied. The experiment completed with no ML challenger for either frozen strategy; the Phase 4 rule baselines remain unchanged.

## Authoritative execution

The corrected authoritative manual `phase6-ml-filter` workflow run `34966406652` executed on exact merged-main SHA `2dccb0f00d2a443bc41646ac1b3b494d81e1f13c` and completed **SUCCESS** for both frozen cells:

- `session_breakout`: USDJPY 15m, 5-pip breakout buffer, 1.5x target range.
- `volatility_breakout`: USDJPY 1h, 2.0x range expansion, fixed 1.0R target.

Both cells pinned the accepted Phase 2 USDJPY processed-manifest SHA-256 `e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d` and Phase 5 checkpoint `fmp-v1-phase5-features` / `e0b2fc7bf12b0c9cd9d76668564df6b7714b1fe0`. Each cell executed the complete frozen experiment twice, byte-compared the resulting evidence, passed the semantic pre-2024 lock, and uploaded one evidence artifact.

The previously failed orchestration run `34965595086` is retained as debugging history only. Its successful volatility output was not used to make a model-selection decision. The accepted outcome is run `34966406652` after the fail-closed result path was made durable without changing preprocessing, models, cutoffs, strategy parameters, or gates.

## Authoritative artifacts

| Strategy | Artifact ID | GitHub / independently recomputed ZIP SHA-256 | Outcome |
| --- | ---: | --- | --- |
| `session_breakout` | `10395810196` | `36cb9f80ca043da23250669dd974036eb9fb985c3f7f9ffd7844b9d99c96073d` | `NO_ML_CHALLENGER` |
| `volatility_breakout` | `10395670751` | `0cf71a4d725fb1e609a512bb95aa13e4ad8771ae2b5864dd09e2833fe160a8d2` | `NO_ML_CHALLENGER` |

Independent ZIP inspection found exactly `manifest.json`, `selection.json`, and `result.json` in each artifact. Inner SHA-256 values also matched the artifact manifests:

- session `selection.json`: `caed70bd4f947207e5089b8b497f1a8331853f5e73c767dcb00145820f3f5d42`; `result.json`: `4ddbe1fc8382182c85ce809da88ba93d9f2cc02fd0ebb147706684cc44c54aa0`.
- volatility `selection.json`: `b29b731431c420b0f9dbd59c460444bc2d0f3796c9b44606e6118214e0cbe285`; `result.json`: `9d3b2de8f83f271bdd68d8755a33f74cadeecc8ce91be90a50d99f081f29aecd`.

Both manifests bind `EXP-20260915-007`, `fmp-feature-v1`, the accepted Phase 5 checkpoint, the accepted USDJPY processed identity, and runtime versions Python 3.12.14, NumPy 2.5.3, Polars 1.44.2, scikit-learn 1.9.1, and SciPy 1.18.1.

## Session-breakout outcome

Fit-period evidence contains 1,043 strategy candidates, of which 428 directional candidates joined to the exact 49 model inputs and received resolved labels; 615 candidates were explicit `NO_TRADE`. Selection-period evidence contains 523 candidates, 192 joined/labeled directional rows, and 331 `NO_TRADE` candidates. Candidate, joined-frame, and labeled-row digests are persisted for both periods together with exact feature-availability and label-resolution ranges.

The fit-period input `minutes_since_new_york_open` is null on all 428 model rows. DEC-031 requires an all-null fit column to fail closed rather than inventing a fill value. Both frozen model families therefore record `PREPROCESSING_FAILED / ALL_NULL_FIT_COLUMN`, `fit_count = 0`, and `refit_after_selection = false`. All six model/retained-fraction variants are retained as `NOT_EVALUATED_MODEL_FIT_FAILED` evidence.

The frozen 0.2-pip selection baseline itself remains valid: 192 trades, +3.8558% net return, +$20.0822 expectancy/trade, 1.3010 profit factor, and 1.4390% max drawdown. No ML score is substituted for the failed preprocessing path. `selected_variant = NO_ML_CHALLENGER`, and validation remained unopened.

## Volatility-breakout outcome

Fit-period evidence contains 1,043 strategy candidates, 374 joined/labeled directional model rows, and 669 explicit `NO_TRADE` candidates. Selection-period evidence contains 523 candidates, 222 joined/labeled directional rows, and 301 `NO_TRADE` candidates. Both frozen model families fit exactly once on the fit period, use only fit-derived preprocessing and cutoffs, and record `refit_after_selection = false`.

The unchanged 0.2-pip selection baseline produced 222 trades, +3.8457% net return, +$17.3228 expectancy/trade, 1.2014 profit factor, and 1.4105% max drawdown. All six frozen filtered variants fail the predeclared selection gate:

| Model | Retained fraction | Trades | Net return | Expectancy | Profit factor | Max DD | Selection result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| logistic regression | 0.75 | 169 | +2.6999% | +$15.9756 | 1.1675 | 1.3059% | FAIL |
| logistic regression | 0.50 | 129 | +2.7136% | +$21.0354 | 1.2101 | 1.3059% | FAIL |
| logistic regression | 0.25 | 69 | -0.2463% | -$3.5692 | 0.9703 | 1.8022% | FAIL |
| histogram gradient boosting | 0.75 | 178 | +3.0536% | +$17.1548 | 1.1823 | 1.4105% | FAIL |
| histogram gradient boosting | 0.50 | 137 | +1.3427% | +$9.8008 | 1.0925 | 1.9254% | FAIL |
| histogram gradient boosting | 0.25 | 63 | +0.3704% | +$5.8802 | 1.0515 | 1.1360% | FAIL |

Most importantly, `net_return_beats_baseline` is false for every one of the six variants. The logistic 0.50 variant improves expectancy and profit factor while reducing drawdown, but it still fails the frozen all-conditions gate because +2.7136% net return is below the +3.8457% baseline. Other variants fail additional conditions. No tie-break is reached because there is no qualifying variant. `selected_variant = NO_ML_CHALLENGER`, and validation remained unopened.

## Section 17 evidence audit

The accepted evidence binds the complete approved evidence contract: exact strategy configuration; fit/selection split identities; candidate, joined, labeled, and unlabelable counts and digests; feature-availability and label-resolution ranges; exact 49 model input columns; Phase 2 and Phase 5 source identities; preprocessing null counts/state; transformed-matrix identities; exact model configuration and global seed; fit status and fit-row accounting; score digests; fit-derived cutoffs and retained fractions; all six selection variants per strategy; financial metrics and gate criteria; selected-variant status; validation-loaded status; and zero-refit accounting.

The workflow and independent audit found no 2024-or-later opened feature artifact, source partition, label-resolution timestamp, or financial evidence. The normal Phase 6 data surfaces still reject any required 2024+ access before opening the partition. **Final-test touched?: NO.**

## Closure checkpoint

The source-free Phase 6 acceptance closure merged to `main` at `5d387b7ca93d04c498eb04c376e0dd92f1fe1953`. Fresh verification on that exact merge commit completed successfully before checkpoint creation:

- tests run `34972534430` — SUCCESS, 573/573 tests PASS, workflow YAML PASS, compile PASS.
- Phase 3 acceptance run `34972534435` — SUCCESS.
- Phase 1 source-capable workflows remained suppressed by the `[phase1-no-source]` closure path.

The immutable lightweight checkpoint `fmp-v1-phase6-models` was then created and independently verified to resolve directly to commit `5d387b7ca93d04c498eb04c376e0dd92f1fe1953` (`type = commit`). No Phase 7 work, final-test access, broker/live/demo integration, or real-money trading was opened by checkpoint creation.

## Acceptance conclusion

`EXP-20260915-007` completed under the frozen DEC-031 protocol and rejects the ML overlay for both serious Phase 4 candidates. The negative result is accepted evidence, not a protocol failure. The USDJPY 15m session-breakout and USDJPY 1h volatility-breakout rule baselines remain frozen unchanged; no model is promoted.

Phase 6 is therefore formally **PASS**. Checkpoint `fmp-v1-phase6-models` is **CREATED** at the verified closure merge `5d387b7ca93d04c498eb04c376e0dd92f1fe1953` after tests run `34972534430` and Phase 3 acceptance run `34972534435` both succeeded. Phase 7 remains UNSTARTED. The final-test period remains locked, and no broker/live/demo integration or real-money trading is authorized.
