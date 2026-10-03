# Phase 8A — Annual Workflow Validity and Run-Identity Recovery

**Date:** 2026-10-03  
**Status:** WORKFLOW REPAIRED / EXACT RUN IDENTITIES REBOUND  
**Decision:** DEC-520  
**Predecessors:** DEC-496, DEC-497 through DEC-519

DEC-520 repairs a workflow-validity defect discovered before the recovered 2015 replacement dispatch.

The DEC-496 workflow had three duplicate `include-hidden-files: true` keys in the preflight upload mapping. GitHub rejected that workflow on ordinary branch pushes and nevertheless advanced the workflow's global run number through 375. Those records were startup failures, not `workflow_dispatch` research attempts; the manual annual-dispatch inventory still contains only failed run 1.

The corrected workflow blob is:

`09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`

It contains exactly one hidden-file flag on each of the three artifact upload steps: preflight, cell product, and annual freeze. The malformed DEC-496 workflow is retained as a frozen historical fixture.

Because the corrected workflow no longer creates push-trigger startup failures, the next exact GitHub workflow identity is frozen as:
- recovered 2015 replacement: run 376 / attempt 1;
- future 2016 annual catalogue: run 377 / attempt 1.

The DEC-497→519 source and workflow chain is byte-rebound to those identities and the corrected workflow. Existing live inventory checks still require exactly one prior manual annual dispatch before run 376 and exactly two before run 377, so any unexpected intervening dispatch fails closed.

DEC-520 itself submits no workflow, authorizes no retry/rerun, opens no 2017+ execution, and grants no broker, order, real-money, or trading authority.
