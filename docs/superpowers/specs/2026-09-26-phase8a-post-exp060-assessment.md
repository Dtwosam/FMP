# Phase 8A — Post-EXP-060 Assessment and Remaining Research Gate

**Date:** 2026-09-26
**Status:** SOURCE-ONLY ASSESSMENT / PHASE 8A REMAINS ACTIVE
**Decision:** DEC-263
**Phase:** Phase 8A — Multi-pair, multi-strategy portfolio research

## Purpose

DEC-263 assesses the Phase 8A state after the sole EXP-060 historical result is frozen by merged DEC-262. It does not open a new model experiment, alter any historical result, dispatch any workflow, or authorize Phase 8B.

The assessment answers two questions:

1. Has the direct market-learning track now produced a complete research answer?
2. What exact unresolved gate prevents Phase 8A acceptance from running?

## Bound predecessor

DEC-263 binds merged DEC-262 commit:

`6d6c88426960b40293aa4b3f1f42d2e02911b375`

The DEC-262 reviewed result binds:

- EXP-060 run `36260155597`;
- result-producing head `0062546fda38bfc768122cf03b9a4d69d1b8e0b7`;
- attempt `1`;
- conclusion `success`;
- aggregate artifact `10912798284`;
- aggregate digest `sha256:9090a1a1c7849c703eaa38e5571a36a65f5a47f250c6c0e3a7e21777367b8bc9`;
- evidence fingerprint `52a840d0919992e1fe9ef3342ddefe46cfb1ad8ccd23c8dfe55963d4c1669b37`;
- zero selected cells and zero accepted model candidates.

EXP-060 is closed. No EXP-060 rerun, retry, replacement, threshold relaxation, or post-result rescue is authorized.

## Direct market-learning conclusion

The direct market-learning track has now answered its frozen historical question credibly.

EXP-060 completed the repaired regime-balance protocol technically successfully across all 18 cells. Exactly two USDJPY/5m/60m budget variants passed the aggregate gate, but both failed the unchanged temporal-stability gate. No model reached validation or retrospective holdout and no accepted model challenger exists.

For the Phase 8A acceptance criterion requiring the direct market-learning question to be answered under a frozen chronological protocol with either a qualified immutable challenger or a credible rejection retained as evidence, EXP-060 supplies the credible-rejection branch.

That conclusion does not itself complete Phase 8A because the separate rule-based portfolio research path remains unresolved.

## Remaining rule-based chain

DEC-043 / EXP-20260922-015 remains the frozen rule-based challenger-discovery protocol:

- exactly 567 immutable configurations;
- exactly EURUSD, GBPUSD, USDJPY;
- exactly 5m, 15m, 1h;
- exactly six existing deterministic rule families;
- Stage A: 2015-01-01 through 2018-12-31;
- Stage B: 2019-01-01 through 2022-12-31;
- Stage C: 2023-01-01 through 2026-08-20 inclusive;
- all evidence labeled retrospective/already seen;
- no post-result parameter expansion or threshold relaxation.

DEC-044 remains the pre-result arithmetic correction: Stage A may retain at most two survivors per exact symbol/family/timeframe cell, for a maximum of 108 Stage A survivors.

Current frozen workflow source identities are:

- Stage A `.github/workflows/phase8a-exp015-stage-a.yml` blob `e32e04c3afd8a8929dc60defd109788d4e7aa989`;
- Stage B `.github/workflows/phase8a-exp015-stage-b.yml` blob `50a5a32c7beb99df1fbbb8db89e88edae958ee7c`;
- Stage C `.github/workflows/phase8a-exp015-stage-c.yml` blob `abc946fb7684dec6174b2cdf9075092856b14f86`.

## Historical execution audit

The Stage A GitHub Actions history currently contains 12 old source-development runs. Each visible run is a failed push on branch `phase8a/exp015-stage-a`; these are not authoritative manual-main historical attempts and did not open the DEC-043 Stage A research interval under a reviewed result contract.

There is therefore no authoritative Stage A `workflow_dispatch` run from `main`.

Stage B reports zero workflow runs.

Stage C reports zero workflow runs.

This distinction is important: the old Stage A development failures remain historical CI evidence and must not be deleted or relabeled, but they do not consume a future explicitly authorized manual-main Stage A historical slot.

## Why DEC-042 and DEC-045 remain blocked

DEC-042 / EXP-20260922-014 portfolio selection requires the exact final EXP-015 shortlist. No Stage C final shortlist exists because no authoritative Stage A/B/C historical chain has run.

DEC-045 Phase 8A acceptance consumes exact DEC-042 selection evidence and can produce only:

- `PHASE8A_SHADOW_CANDIDATE_ACCEPTED`, freezing the selected historical-qualified strategies as an immutable shadow-candidate/champion set and authorizing Phase 8B design only; or
- `PHASE8A_RESEARCH_REJECTED`.

Without real EXP-015 results, neither DEC-042 nor DEC-045 may be executed or synthesized.

## Phase status

Phase 8A remains **ACTIVE**.

The direct market-learning branch is closed as a credible negative research result.

The remaining unresolved historical branch is EXP-015 rule-based challenger discovery, followed conditionally by DEC-042 portfolio selection and DEC-045 Phase 8A acceptance.

Phase 8B remains **LOCKED** because no DEC-045 acceptance result has frozen a shadow candidate.

## Next safe gate

Before any EXP-015 Stage A historical dispatch, execution governance must be modernized without changing DEC-043/044 research semantics.

The next gate must be source-only and should:

1. predeclare exact attempt-1 Stage A terminal review;
2. prove there is no prior authoritative manual-main Stage A historical attempt while preserving the 12 development-run records;
3. add a first-run guard requiring exact workflow identity, `main`, `workflow_dispatch`, and `run_attempt == 1`;
4. open at most one bounded Stage A historical-result slot;
5. keep Stage B and Stage C locked until exact upstream survivor evidence exists;
6. keep portfolio selection, Phase 8A acceptance, Phase 8B, demo, broker mutation, live orders, real-money action, and trading locked.

No Stage A dispatch is authorized by DEC-263 itself.
