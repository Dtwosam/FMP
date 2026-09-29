# Phase 8A — EXP-062 Active One-Shot Historical Executor Workflow Installation

**Date:** 2026-09-30  
**Status:** ACTIVE WORKFLOW INSTALLED / DISPATCH STILL LOCKED  
**Decision:** DEC-424  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-423

DEC-424 performs the explicitly authorized repository mutation and installs the
active one-shot historical executor workflow at:

`.github/workflows/phase8a-exp062-one-shot-historical-executor.yml`

The installed file is byte-for-byte identical to the pinned dormant template and
therefore has Git blob SHA:

`51ce87584369be957482460d81649adb1cb9f05d`

DEC-424 pins the DEC-423 mutation-authorization source blob
`df6a80d1f6ee6315f3e3095433ed6704666ccd33`.

Installation changes repository state as follows:

- workflow-install authorization remains true;
- workflow installed state becomes true;
- historical executor availability becomes true;
- historical-result dispatch authorization remains false;
- historical execute mode remains false;
- rerun/retry/replacement remain false;
- reserved-data, Phase 8B, demo/live, real-money, and trading authority remain false.

The workflow is manual-only via `workflow_dispatch`; it has no push or pull-request
trigger. DEC-424 does not dispatch it.

## Next gate

A separate explicit one-shot executor dispatch authorization is required before the
installed workflow may be run.
