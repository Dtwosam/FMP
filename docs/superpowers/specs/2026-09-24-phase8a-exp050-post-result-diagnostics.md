# Phase 8A — EXP-050 Post-Result Temporal-Jackknife Utility Diagnostic

**Date:** 2026-09-24
**Status:** POST-RESULT DIAGNOSTIC; NO NEW MODEL EXECUTION AUTHORIZED
**Decision:** DEC-149
**Source experiment:** EXP-20260924-050
**Source result:** DEC-148

## 1. Purpose

DEC-149 freezes the post-result diagnostic over the completed EXP-050 temporal-jackknife utility experiment before any later successor protocol is written.

The diagnostic uses only immutable reviewed evidence from DEC-148. It performs no new fit, changes no gate, and authorizes no historical result execution.

The purpose is to separate three observed facts:

1. the EXP-050 jackknife construction increases utility-eligible selection coverage relative to EXP-049;
2. every aggregate-selection pass is concentrated in one USDJPY 5m / 60m cell; and
3. all three aggregate passes still fail the unchanged temporal-stability gate because the early 2021 windows do not contain durable candidate coverage.

This is descriptive evidence, not a causal market claim.

## 2. Source binding

DEC-149 is bound to:

- source result decision: `DEC-148`
- source workflow run: `36049824739`
- source execution commit: `25d48828b981c4309f4a859d2a33a56094638f21`
- source evidence fingerprint: `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`
- DEC-148 merged commit: `50ae34098ece275959d52ca9d104a07374a7ff6a`
- DEC-148 reviewed-result source blob: `70402f6c21f4ed22b4991025c98e6c1664215215`

EXP-050 remains closed to rerun or replacement.

## 3. Budget-availability accounting

The frozen EXP-050 universe contains 54 predeclared cell/budget variants.

- unavailable because the frozen utility-eligible selection set does not reach the requested budget: 26
- available: 28
- available variants passing the unchanged aggregate selection gate: 3
- available variants rejected at the aggregate selection gate: 25
- stable-selection passes: 0

Relative to the immediately preceding EXP-049 result:

- available variants increase from 23 to 28
- unavailable budget variants decrease from 31 to 26
- utility-eligible selection rows increase from 14,158 to 26,392, a descriptive increase of 12,234 rows

These count changes do not establish that the jackknife construction causes a more durable edge. The downstream stability result remains zero accepted challengers.

## 4. Aggregate-pass concentration

All three aggregate-selection passes belong to the same cell and horizon:

| Cell | Budget anchor | Selection candidates | Selection total net pips | Stable |
| --- | ---: | ---: | ---: | --- |
| USDJPY 5m / 60m | 250 | 250 | 612.9 | NO |
| USDJPY 5m / 60m | 500 | 501 | 247.4 | NO |
| USDJPY 5m / 60m | 1000 | 1000 | 504.3 | NO |

There are:

- three 60-minute aggregate passes
- zero 240-minute aggregate passes
- one cell with any aggregate pass
- zero stable-selection passes

The result therefore does not show cross-pair, cross-timeframe, or cross-horizon confirmation.

## 5. Temporal-stability diagnostic

The unchanged four-window stability screen remains decisive.

### 2021 H1

All three aggregate-pass variants contain zero directional candidates.

This alone prevents every aggregate pass from meeting the frozen candidate-share requirement and from demonstrating usable early-window coverage.

### 2021 H2

- budget 250: zero candidates
- budget 500: zero candidates
- budget 1000: one candidate and failure of both the share and financial-sign requirements

Therefore all three variants remain unstable across the first year of the stability screen.

### 2022 H1

The budget-500 and budget-1000 variants have positive financial signs but still miss the frozen 10% candidate-share floor.

DEC-148 does not authorize reinterpretation of that floor as optional simply because the financial signs are positive.

### 2022 H2

All three variants pass the frozen stability window.

That later-window success does not override the failed 2021 windows.

## 6. Diagnostic classification

DEC-149 records:

`UTILITY_COVERAGE_INCREASED_BUT_EARLY_TEMPORAL_COVERAGE_LIMITED`

This classification means only that:

- utility-eligible coverage and budget availability are higher than in EXP-049;
- aggregate passes are concentrated in USDJPY 5m / 60m;
- the three passes have no candidates in 2021 H1;
- candidate coverage remains insufficient in 2021 H2;
- later 2022 evidence is not enough to satisfy the predeclared full-window gate.

It does not claim a market regime cause, a model defect, or a valid rescue parameter.

## 7. Guardrails

DEC-149 does **not** authorize:

- lowering the 10% candidate-share floor
- weakening per-window financial requirements
- removing either 2021 stability window
- changing the three temporal-jackknife views
- replacing unanimous positive-utility consensus with majority voting
- lowering the positive-utility requirement
- adding smaller budget anchors as a result-producing rescue
- rerunning EXP-050
- replacing the consumed EXP-050 run
- authoritative successor fitting
- successor historical result execution
- promotion
- shadow or demo execution
- broker mutation
- live orders
- real-money action
- trading authorization

## 8. Successor boundary

DEC-149 opens only separately frozen successor-protocol source work.

A later decision may define a new post-result-informed protocol, but it must bind this diagnostic and the immutable DEC-148 result. It cannot silently mutate EXP-050 or reinterpret failed stability windows as passing.

Any later result-producing path still requires the repository's normal source, training-core, artifact, workflow, terminal-review, one-run authorization, operator, and reviewed-result gates.

## 9. Frozen implementation

The diagnostic source is:

`src/fmp/market_learning/model_successor_temporal_jackknife_utility_post_result_diagnostics.py`

Focused tests are:

`tests/test_phase8a_exp050_post_result_diagnostics.py`

The next gate after DEC-149 is a separately frozen successor protocol source. No model fit or historical result execution is opened by this decision.
