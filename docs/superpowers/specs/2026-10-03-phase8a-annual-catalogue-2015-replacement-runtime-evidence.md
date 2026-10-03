# Phase 8A — Automated 2015 Replacement Runtime Evidence

**Date:** 2026-10-03  
**Status:** READ-ONLY POST-RUN REVIEW / CONCRETE BINDING AUTOMATION  
**Decision:** DEC-513  
**Predecessors:** DEC-500, DEC-501, DEC-502, DEC-512

DEC-513 installs a read-only \`workflow_run\` reviewer for the successful 2015 replacement annual-catalogue run.

It runs only for annual workflow run number 2 and requires attempt 1, successful completion, branch \`main\`, and the exact target head. It also requires exactly one successful DEC-512 executor run at that same head.

The reviewer:
- fetches the exact target run, job inventory, and artifact inventory;
- downloads the annual-freeze artifact by ID;
- verifies the downloaded ZIP against GitHub's SHA-256 artifact digest;
- runs DEC-500 to review the exact successful replacement evidence;
- runs DEC-501 to freeze the reviewed runtime evidence;
- runs DEC-502 to create the canonical concrete 2015 runtime binding;
- uploads the run metadata, reviewed evidence, freeze, and binding as immutable workflow artifacts.

The workflow has only \`contents: read\` and \`actions: read\`. It cannot dispatch, rerun, retry, mutate the repository, open 2016 execution, promote strategies, access a broker, place orders, use real money, or trade.

## Next gate

\`READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_PREFLIGHT\`
