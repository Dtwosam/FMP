# Phase 8A — Run-378 Evidence Successor Recovery

**Date:** 2026-10-04  
**Status:** SOURCE-READY ONE-SHOT SUCCESSOR RECOVERY / 2017 LOCKED  
**Decision:** DEC-533

## Live evidence

Annual catalogue run `37206992367` is exact global run 378 / attempt 1 on
`2524fde355349581c9440a172d0384c3cbce31ed` and completed successfully.

Its 2016 catalogue inventory is complete:

- 20 successful jobs;
- 20 unexpired artifacts;
- one successful 2016 freeze artifact;
- exact DEC-532 dispatch provenance from post-install recovery run
  `37206963024`;
- exact DEC-532 dispatch artifact `11304832641` with SHA-256 digest
  `7be017eeeedf1ccacb87182971a24914772821a7c77a5b9b17d73d320c3ce3e6`.

The automatic DEC-522 `workflow_run` successor did not start.

## Recovery

DEC-533 is a path-scoped push workflow whose only Actions-write operation is one
manual dispatch of the already-installed DEC-522 reviewer workflow. It requires:

- its own exact first push run / attempt 1;
- the exact successful run-378 identity above;
- the exact 20-job/20-artifact run-378 inventory;
- exact DEC-532 recovery run and artifact provenance;
- zero prior automatic or manual DEC-522 reviewer runs;
- byte-exact active annual workflow, DEC-522 source, DEC-522 workflow, and
  DEC-532 recovery workflow.

After DEC-522 completes, DEC-533 downloads the exact runtime-binding artifact,
verifies its ZIP digest, and requires a concrete DEC-522 binding for run 378 with
all 2017+, strategy, promotion, broker, order, real-money, and trading flags
false.

DEC-533 never dispatches the annual catalogue and never mutates repository
contents.

## Next gate

`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_PREFLIGHT`
