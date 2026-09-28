# Phase 8A — EXP-062 Historical Terminal Review Contract

**Date:** 2026-09-28  
**Status:** SOURCE-ONLY PREDECLARED TERMINAL REVIEW / NO RESULT YET  
**Decision:** DEC-334  
**Experiment:** EXP-20260927-062

## Purpose

DEC-334 freezes how the sole future EXP-062 historical workflow run #2 / attempt 1
will be judged before that run exists.

It authorizes no dispatch and cannot create a result.

## Reviewable runtime identity

A reviewable historical run must be:

- workflow `phase8a-exp062-discovery`;
- path `.github/workflows/phase8a-exp062-discovery.yml`;
- event `workflow_dispatch`;
- branch `main`;
- exact caller-supplied executor merged-main head;
- workflow run #2;
- attempt 1;
- terminal `completed`;
- distinct from frozen proof run `36358289723`.

## Success shape

A successful run is accepted only with the exact DEC-298 inventory:

- preflight job;
- all 18 expanded cell jobs;
- aggregate job;
- 20 total jobs;
- every job success;
- exactly 20 non-expired expected artifacts;
- no unexpanded matrix placeholder.

A structurally complete success is classified
`EXP062_HISTORICAL_RESULT_SUCCESS_COMPLETE_REVIEW_REQUIRED`.
Aggregate/cell contents still require separate evidence review and candidate
compilation remains locked.

## Non-success shape

Any terminal non-success is classified
`EXP062_HISTORICAL_RESULT_NON_SUCCESS_TERMINAL_CLOSED`.

The historical-result slot is consumed permanently. Partial expected evidence may be
preserved, but rerun, retry, and replacement remain false.

For GitHub matrix compatibility, one literal unexpanded skipped matrix-template job is
allowed only for non-success, only when skipped, and only when no expanded cell jobs
coexist with it.

## Safety boundary

DEC-334 keeps false:

- rerun / retry / replacement;
- reserved 2023-2026 robustness access;
- candidate compilation / promotion;
- Phase 8B;
- demo orders;
- broker mutation;
- live orders;
- real-money action;
- trading.

## Next gate

DEC-334 must be green before the one-shot historical executor is allowed to reach
`main`. After run #2 becomes terminal, this exact contract is applied to the actual
run/jobs/artifacts before any downstream gate opens.
