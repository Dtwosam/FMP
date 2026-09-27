# Phase 8A — EXP-061 Read-Only Gate-Proof Operator

**Date:** 2026-09-27  
**Status:** SOURCE-ONLY OPERATOR / NO EXECUTE MODE / NO DISPATCH AUTHORIZED  
**Decision:** DEC-278  
**Experiment:** EXP-20260927-061  
**Predecessor:** DEC-277

## 1. Purpose

DEC-278 adds a read-only planner for the future EXP-061 gate proof.

It does not dispatch anything.

## 2. Plan inputs

The operator requires:

- current `main` branch metadata;
- current workflow-run listing for the EXP-061 workflow surface;
- an exact expected main head supplied by the caller.

The current main commit must equal that expected head.

## 3. Missing-run state

When no matching manual-main EXP-061 workflow run exists, the operator returns:

`EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED`

and exposes only the planned command:

`gh workflow run phase8a-exp061-discovery.yml --ref main`.

The report still records:

- proof dispatch authorized: false;
- execute mode available: false;
- historical result dispatch: false;
- historical discovery execution: false;
- discovery result: false;
- trading: false.

## 4. Existing-run state

If any matching manual-main EXP-061 workflow run exists, the operator returns:

`EXP061_PROOF_RUN_PRESENT_REVIEW_REQUIRED`

and removes the dispatch command.

It never plans a second proof run automatically.

## 5. No execute mode

The CLI `scripts/phase8a_exp061_proof_operator.py` implements only:

`plan`.

There is no `execute`, `advance`, `dispatch`, or retry command.

## 6. Frozen implementation identities

- operator: `src/fmp/discovery/proof_operator.py`;
- operator blob: `b8af93555656d4da57ead8fc4b66ae66e62a2de7`;
- CLI: `scripts/phase8a_exp061_proof_operator.py`;
- CLI blob: `4f074f5abecd006d032f9897a1e527aa694a233d`;
- focused tests: `tests/test_phase8a_exp061_proof_operator.py`;
- focused-test blob: `9f4a678e4a3ed6d37216387796d00da28620cd30`.

## 7. Next gate

After DEC-276/277/278 are merged green, a later decision may bind the exact merged-main head, require a fresh missing-run plan twice, and authorize exactly one proof dispatch.

That later authorization must still keep the historical discovery/result gate false.
