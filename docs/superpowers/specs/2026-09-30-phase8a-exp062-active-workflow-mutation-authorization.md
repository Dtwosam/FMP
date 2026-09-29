# Phase 8A — EXP-062 Active Workflow Repository-Mutation Authorization

**Date:** 2026-09-30  
**Status:** EXPLICIT INSTALL MUTATION AUTHORIZED / WORKFLOW STILL ABSENT  
**Decision:** DEC-423  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-422

DEC-423 consumes the concrete DEC-422 workflow-install action-preflight runtime
freeze and records explicit operator authorization for the repository mutation that
will install the active one-shot historical executor workflow.

It pins:

- DEC-422 runtime-freeze blob
  `65108857f15b6ab084bbb5f8a0358b7bbd4aaa59`;
- DEC-422 runtime-freeze fingerprint
  `cce3b8900f630ddf0e651af10ceba39311f1e00485f6bca99af28252195aae0f`;
- dormant executor template blob
  `51ce87584369be957482460d81649adb1cb9f05d`.

DEC-423 changes exactly one runtime authority boundary:
`historical_executor_workflow_install_authorized=true`.

The active workflow path must still be absent under DEC-423 itself. Installed state,
executor availability, historical-result dispatch, execute mode, rerun/retry/
replacement, reserved-data access, Phase 8B, demo/live, real-money, and trading all
remain false.

## Next gate

The next gate is the repository mutation that installs the active workflow from the
pinned dormant template. Installing the workflow does not itself authorize dispatch
or trading.
