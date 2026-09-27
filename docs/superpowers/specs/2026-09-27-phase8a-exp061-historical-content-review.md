# Phase 8A — EXP-061 Historical Result Content Review

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY PREDECLARED CONTENT REVIEW / NO RESULT ACCEPTANCE  
**Decision:** DEC-291  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-290

## Purpose

DEC-291 freezes the content-validation step that follows a structurally successful DEC-290 terminal review.

It is read-only and can only be used after all 18 cell evidence objects plus the aggregate evidence have been obtained from the exact run #2 artifact set.

It does not accept a strategy, authorize candidate compilation, open reserved 2023-2026 history, or unlock any trading path.

## Exact inputs

DEC-291 requires:

- exactly 18 cell evidence objects;
- exactly one aggregate evidence object;
- caller-supplied exact historical run head.

Every cell is revalidated through the frozen DEC-272 cell-evidence validator.

Every cell must:

- carry the exact expected code commit;
- have one of the exact 18 DEC-270 cell identities;
- appear exactly once.

The aggregate is revalidated through the frozen DEC-274 aggregate validator and must carry the same exact code commit.

## Independent recomputation

DEC-291 then recompiles aggregate evidence directly from the 18 independently validated cell evidence objects using the frozen DEC-274 compiler.

The provided aggregate must equal the independently recomputed aggregate exactly.

This rechecks:

- exact 18-cell inventory;
- exact Phase 2 processed-manifest identities;
- exact feature/outcome evidence fingerprints;
- exact feature/outcome manifest consistency across horizons;
- every cell evidence fingerprint;
- discovery shortlist inventories;
- confirmation-frozen inventories;
- validation-accepted inventories;
- global 180 discovery-shortlist cap;
- global 54 frozen-pattern cap;
- global 54 accepted-pattern cap;
- reserved robustness block remains unopened;
- candidate/trading authorizations remain false.

## Content classification

After exact content validation, DEC-291 records one of:

`HISTORICAL_CONTENT_VALID_NO_VALIDATED_PATTERNS`

or

`HISTORICAL_CONTENT_VALID_WITH_VALIDATED_PATTERNS`

based only on the frozen aggregate validation count.

It records the exact:

- discovery shortlist count;
- confirmation frozen count;
- validation accepted count.

A positive validation count is still only retrospective historical evidence.

DEC-291 does not itself set:

- historical result accepted;
- pattern hypotheses accepted;
- candidate compilation authorized;
- promotion authorized.

A later reviewed-result decision remains required.

## Frozen implementation

Reviewer:

`src/fmp/discovery/historical_result_content_review.py`

Git blob:

`cacdfc7a7d9a97b054c256879152067b2fe43c41`

Read-only CLI:

`scripts/phase8a_exp061_historical_content_review.py`

Git blob:

`35612d98d3cb9463a2e67ad5bc0e9c6c84015fd2`

Focused tests:

`tests/test_phase8a_exp061_historical_content_review.py`

Git blob:

`361d71fb7b82723f9fde0a10ed53697f301ab6b8`

The tests prove exact deterministic recomputation, order independence, missing/duplicate cell rejection, cell/aggregate commit drift rejection, aggregate forgery rejection, and downstream locks.

## Locks preserved

DEC-291 keeps false:

- historical result accepted;
- pattern hypotheses accepted;
- reserved robustness access;
- candidate compilation;
- promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

The evidence remains labeled:

`RETROSPECTIVE_ALREADY_SEEN`

and may not be described as untouched OOS.

## Next gate

If DEC-290 reports structural success and DEC-291 validates all content, a later result-specific reviewed decision may freeze the exact counts and exact surviving pattern-hypothesis fingerprints.

If no validation patterns survive, the historical experiment closes with no candidate.

If patterns survive, they remain hypotheses only; candidate compilation, robustness, prospective shadow/demo learning, and all trading actions require later separate gates.
