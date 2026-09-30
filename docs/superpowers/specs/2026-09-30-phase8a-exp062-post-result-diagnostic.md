# Phase 8A — EXP-062 Post-Result Diagnostic

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY POST-RESULT DIAGNOSTIC / NO SUCCESSOR AUTHORIZATION  
**Decision:** DEC-442  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-441

## Purpose

DEC-442 diagnoses why the 11 EXP-062 confirmation-frozen patterns produced zero
validation-accepted candidates. It uses only the immutable historical evidence
already reviewed and frozen by DEC-440/441.

It does not rerun EXP-062, redefine a pattern, relax a threshold, open reserved
2023-2026 robustness data, authorize successor protocol source, execute research,
compile candidates, promote, enter Phase 8B, or touch any trading surface.

## Frozen source

DEC-442 binds:

- DEC-441 merge `d5e8ad7cd98ec1511742d1b266e6779852155c96`;
- DEC-441 source blob `ae0353fce77e9ff03536f2323820804dbda7241c`;
- historical run `36714210992`;
- historical head `013395092804de6b0ef51537081ab8443b8b91be`;
- aggregate evidence fingerprint
  `b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506`.

The six exact cell artifacts containing all 11 confirmation survivors are pinned by
artifact id/digest, exact cell JSON SHA-256, and cell evidence fingerprint in the
DEC-442 source.

## Frozen validation gate

The diagnostic preserves the original validation criteria:

- minimum total support: 200;
- minimum support in each validation year: 40;
- minimum positive validation years: 3 of 4;
- positive aggregate mean net pips at 0.5-pip cost;
- no pattern redefinition during validation.

No criterion is changed by DEC-442.

## Diagnostic result

All 11 confirmation survivors are 240-minute-horizon patterns. They occur only in
EURUSD and GBPUSD across 5m, 15m, and 1h cells:

- EURUSD 15m: 3;
- EURUSD 1h: 2;
- EURUSD 5m: 2;
- GBPUSD 15m: 2;
- GBPUSD 1h: 1;
- GBPUSD 5m: 1.

There are zero USDJPY confirmation survivors and zero 60-minute-horizon survivors.

All 11 had sufficient confirmation support and positive confirmation mean net pips.
In 2019-2022 validation:

- all 11 have non-positive aggregate mean net pips;
- all 11 have fewer than three positive validation years;
- one candidate, GBPUSD 1h / 240m, also has a minimum yearly support of 29, below
  the required 40;
- the other ten do not fail the yearly-support minimum.

DEC-442 therefore classifies the result as:

`CONFIRMATION_EDGE_DID_NOT_PERSIST_THROUGH_2019_2022_VALIDATION`

The evidence does not indicate a broad validation sample-size shortage. The dominant
failure is temporal/economic non-persistence after confirmation, not an execution,
adapter, or artifact failure.

## Guardrails preserved

DEC-442 keeps false:

- rerun;
- retry;
- replacement run;
- threshold relaxation;
- pattern redefinition;
- reserved robustness access;
- successor protocol source opening;
- successor result execution;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

The next safe gate is a separate explicit post-EXP-062 research-direction decision
that may use this immutable diagnostic. DEC-442 itself does not choose or authorize
a successor protocol.
