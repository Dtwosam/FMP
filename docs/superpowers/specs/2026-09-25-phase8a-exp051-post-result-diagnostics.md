# Phase 8A — EXP-051 Post-Result Diagnostics

**Date:** 2026-09-25
**Status:** APPROVED POST-RESULT DIAGNOSTIC / SUCCESSOR SOURCE DESIGN MAY OPEN
**Decision:** DEC-162
**Source experiment:** EXP-20260924-051
**Predecessor comparison:** EXP-20260924-050

## 1. Purpose

DEC-162 compares the immutable reviewed EXP-050 and EXP-051 results after DEC-161 closes the single EXP-051 run slot.

The comparison is descriptive only.

It may guide the source design of a later successor protocol, but it does not authorize:

- another EXP-051 run;
- replacement execution;
- historical result production;
- model fitting;
- promotion;
- shadow/demo execution;
- broker mutation;
- live orders;
- real-money action;
- trading.

## 2. Exact EXP-051 source binding

DEC-162 binds:

- source result decision: `DEC-161`;
- source experiment: `EXP-20260924-051`;
- model run: `36066217609`;
- execution commit: `3443b95ae3c524c74df4b2daebe9c526eb01ec9c`;
- aggregate evidence fingerprint: `7dd836ed1c76c8eefd09b2b75e1eef9e875f5c6261c6fbb2cac8e3209781aaea`;
- DEC-161 merge: `0a67a2353f3f2f2c5106074bd9e7e620a37d1649`;
- DEC-161 result-decision blob: `14bc6f2e9172aa325aeb556b7abeacf2c756c475`.

## 3. Exact EXP-050 comparison binding

DEC-162 also binds:

- predecessor result decision: `DEC-148`;
- predecessor diagnostic decision: `DEC-149`;
- predecessor experiment: `EXP-20260924-050`;
- predecessor model run: `36049824739`;
- predecessor execution commit: `25d48828b981c4309f4a859d2a33a56094638f21`;
- predecessor evidence fingerprint: `866b4a8f26553bad8c80a7b2e0e68aedb50bfa42b3c767ce91478c9dfd720023`;
- DEC-149 merge: `d8874bf213c420fb506cc9ee8c4dfb2caffbb9e1`;
- DEC-149 diagnostic blob: `f23465ca30249ce8abab3c9fdf07ce39a8679a9a`;
- DEC-148 result-decision blob: `70402f6c21f4ed22b4991025c98e6c1664215215`.

## 4. What calibration did not change

EXP-051 intentionally preserved EXP-050 raw directional eligibility and budget anchors.

The reviewed evidence confirms that invariance exactly:

| Metric | EXP-050 | EXP-051 | Delta |
| --- | ---: | ---: | ---: |
| total variants | 54 | 54 | 0 |
| available variants | 28 | 28 | 0 |
| unavailable budget variants | 26 | 26 | 0 |
| utility-eligible selection rows | 26,392 | 26,392 | 0 |
| stable-selection-pass variants | 0 | 0 | 0 |

Therefore the calibrated percentile layer changed candidate ranking, not row eligibility or budget availability.

## 5. Aggregate-pass contraction

Aggregate-selection-pass variants changed from:

- EXP-050: `3`;
- EXP-051: `1`;
- delta: `-2`.

Both experiments concentrate aggregate passes in exactly one cell:

`USDJPY 5m / 60m`

EXP-050 aggregate-pass budgets:

- 250;
- 500;
- 1000.

EXP-051 aggregate-pass budgets:

- 250 only.

No 240m variant passes the aggregate gate in either experiment.

## 6. Budget-250 calibrated ranking effect

Both experiments select exactly 250 candidates for the shared aggregate-pass variant.

### EXP-050

- total net pips: `612.8999999999933`;
- mean net pips: `2.451599999999973`;
- LONG candidates: `249`;
- SHORT candidates: `1`;
- candidate identity digest: `63b8b9d3c451df82724d55878f00cf16888060e1358724bb2d7846580cf3879c`.

### EXP-051

- calibrated cutoff: `0.9971023442510035`;
- raw cutoff: `1.852905399735933`;
- total net pips: `1288.1000000000117`;
- mean net pips: `5.152400000000047`;
- LONG candidates: `239`;
- SHORT candidates: `11`;
- candidate identity digest: `e3d0dd4e6881726ba015b6e35d39c5ba0e08642c566adb0eeaef5dbf0e6da5cd`.

### Delta

- total net pips: `+675.2000000000185`;
- mean net pips: `+2.7008000000000743`;
- LONG candidates: `-10`;
- SHORT candidates: `+10`.

The candidate digest changes, proving that calibrated ranking materially changes the selected set.

For the top 250 candidates, realized financial quality improves substantially.

## 7. Temporal distribution remains the blocking problem

The improved top-tail result does not produce early temporal support.

### 2021 H1

- EXP-050 candidates: `0`;
- EXP-051 candidates: `0`.

### 2021 H2

- EXP-050 candidates: `0`;
- EXP-051 candidates: `0`.

Calibration therefore does not repair the complete absence of selected candidates across 2021 for the shared budget-250 variant.

### 2022 H1

EXP-050:

- candidates: `0`;
- total net pips: `0.0`.

EXP-051:

- candidates: `3`;
- total net pips: `-28.100000000000477`;
- mean net pips: `-9.366666666666825`;
- candidate share: `0.012`.

The three newly ranked 2022 H1 candidates fail both share and financial requirements.

### 2022 H2

EXP-050:

- candidates: `250`;
- total net pips: `612.8999999999933`.

EXP-051:

- candidates: `247`;
- total net pips: `1316.2000000000123`.

Delta:

- candidates: `-3`;
- total net pips: `+703.300000000019`.

The calibrated rank therefore improves financial concentration mainly inside the already dominant 2022 H2 window rather than broadening support into 2021.

## 8. Broader budgets degrade

The calibrated rank is not uniformly better as candidate count expands.

### Budget 500

EXP-050:

- total net pips: `247.4000000000135`;
- aggregate gate: PASS.

EXP-051:

- total net pips: `-766.5999999999894`;
- aggregate gate: REJECT.

Delta:

`-1014.000000000003` pips.

### Budget 1000

EXP-050:

- total net pips: `504.3000000000052`;
- aggregate gate: PASS.

EXP-051:

- total net pips: `-3.200000000010732`;
- aggregate gate: REJECT.

Delta:

`-507.5000000000159` pips.

Thus the out-of-fit percentile calibration improves the extreme top tail but degrades broader calibrated ranking enough to remove the 500- and 1000-budget aggregate passes.

## 9. Diagnostic classification

DEC-162 classifies the result as:

`TOP_250_FINANCIAL_QUALITY_IMPROVED_BUT_EARLY_TEMPORAL_COVERAGE_UNCHANGED_AND_BROAD_BUDGETS_DEGRADED`

The evidence supports three simultaneous conclusions:

1. calibration changes ranking while preserving eligibility;
2. the highest-ranked 250-candidate tail becomes financially stronger;
3. temporal coverage remains concentrated in late 2022, while broader ranks become weaker.

The remaining blocker is therefore not simply raw utility scale mismatch.

It is the lack of robust temporal support in the ranked candidate set.

## 10. Guardrails

DEC-162 does not authorize any of the following as a shortcut:

- lower the frozen 10% stability-share floor;
- relax the stability financial signs;
- remove the 2021 stability windows;
- recalibrate using selection windows;
- use realized selection outcomes in ranking;
- lower directional utility positivity;
- lower the aggregate 250-candidate floor;
- add smaller budget anchors merely to bypass the existing gate;
- rerun EXP-051;
- replace the consumed EXP-051 run.

## 11. Successor source gate

DEC-162 opens only:

`SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = true`

It keeps false:

- successor historical result execution;
- successor model fitting;
- promotion;
- shadow;
- demo order;
- broker mutation;
- live order;
- real-money action;
- trading.

A later successor may change ranking mechanics only through a separately frozen protocol.

## 12. Frozen implementation

Diagnostic source:

`src/fmp/market_learning/model_successor_temporal_calibrated_utility_post_result_diagnostics.py`

Git blob:

`00b9cbb5b0c95bd161d429d1f973d1e807f02a48`

Focused tests:

`tests/test_phase8a_exp051_post_result_diagnostics.py`

Git blob:

`4c914eb34b5413ae26455f05b6ea6f347a995d1e`

## 13. Next gate

The next safe step is a source-only successor protocol designed explicitly around **fit-only temporal support in ranking/calibration**, while preserving:

- raw positive unanimous direction eligibility;
- accepted historical source artifacts;
- aggregate financial gate;
- four half-year stability windows;
- validation/holdout chronology;
- no-refit forward semantics.

No successor fit or historical execution may occur until that protocol and a later training core are independently frozen.
