# Phase 8A — Folded Post-Install 2016 Dispatch Plan

**Date:** 2026-10-03  
**Status:** READ-ONLY SECOND JOB / RUN-3 DISPATCH NOT EXECUTED  
**Decision:** DEC-519  
**Predecessors:** DEC-508, DEC-509, DEC-510, DEC-511, DEC-518

GitHub limits `workflow_run` chains to three successor levels. DEC-519 therefore runs as a second job inside the successful DEC-518 workflow instead of adding another `workflow_run` hop.

The DEC-519 job:
- requires the DEC-518 install job to finish successfully;
- overrides permissions to `contents: read` and `actions: read`;
- downloads the exact DEC-518 install artifact from the same workflow run;
- verifies the concrete DEC-508 receipt, concrete DEC-502 runtime binding, installed main commit, and exact installed 2016 gate/runtime blobs;
- fetches the exact two-run annual `workflow_dispatch` inventory;
- rebuilds DEC-509, DEC-510, and DEC-511 in order;
- freezes only ref `main`, `annual_segment_label=2016`, the exact successful 2015 predecessor run ID, and expected run 3 / attempt 1.

DEC-519 performs no repository mutation and no workflow dispatch. Retry/rerun, run 4+, 2017+, broker access, order placement, real-money action, and trading remain locked.

## Next gate

`EXACT_2016_ANNUAL_PATTERN_CATALOGUE_RUN3_ONE_SHOT_DISPATCH`
