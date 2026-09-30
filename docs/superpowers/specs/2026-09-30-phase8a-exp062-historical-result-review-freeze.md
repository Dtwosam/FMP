# Phase 8A — EXP-062 Historical Result Review Freeze

**Date:** 2026-09-30  
**Status:** SOURCE-ONLY DETERMINISTIC RESULT FREEZE / NO DOWNSTREAM AUTHORIZATION  
**Decision:** DEC-441  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-440

## Purpose

DEC-441 deterministically freezes the reviewed DEC-440 EXP-062 historical result.
It preserves the exact successful historical-run identity, aggregate artifact,
aggregate JSON hash, evidence fingerprint, and reviewed result counts in one
canonical fingerprint.

DEC-441 does not reinterpret the result and does not authorize another experiment,
a rerun, candidate compilation, reserved-data access, promotion, Phase 8B, or any
trading surface.

## Frozen reviewed result

The freeze requires DEC-440 to have reviewed exactly:

- historical run `36714210992`;
- run #2 / attempt 1;
- head `013395092804de6b0ef51537081ab8443b8b91be`;
- aggregate artifact `11096592737`;
- artifact digest `sha256:077535bc6e9d9a1d6e8693f873b7552cf8028d793ef79eab175dbbd9970430bc`;
- aggregate JSON SHA-256
  `bfdf9787e9ee32c30ff29aa70594d7404bc7fc2cb573a60068802d2aacbaa6f3`;
- aggregate evidence fingerprint
  `b8019226fb7fce14c6711834fe16cdbb52795d9ca8996b1ed98ede7ecfba9506`;
- 18 verified cells;
- 67 discovery-shortlist entries;
- 11 confirmation-frozen candidates;
- 0 validation-accepted candidates;
- evidence label `RETROSPECTIVE_ALREADY_SEEN`;
- `untouched_oos=false`.

The DEC-440 reviewer source blob is pinned as
`17facb0f77f6419de5f8a74f80019bb7289fe984`.

## Deterministic freeze

A valid reviewed object is serialized as canonical JSON and hashed with SHA-256.
The resulting `freeze_fingerprint_sha256` is the immutable identity for any later
post-EXP-062 research-direction decision.

## Locks preserved

DEC-441 keeps false:

- rerun;
- retry;
- replacement run;
- reserved 2023-2026 robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

After DEC-441 is merged, a separate explicit post-EXP-062 research-direction
decision is required. The zero validation-accepted result does not itself authorize
changing thresholds, mining additional data, entering Phase 8B, or promoting any
confirmation-frozen pattern.
