# Phase 8A — 2018 Runtime Authorization Install Action

**Date:** 2026-10-04  
**Status:** SOURCE-READY EXACT ACTION / NOT APPLIED  
**Decision:** DEC-549

DEC-549 consumes only the successful DEC-548 install preflight from workflow run
`37231591329`, head `4f21ed0efa53beccc722a7180661e11603e6f14a`,
artifact `11314511176`, digest
`sha256:993afb2809aa675ee2df789a402cc736a5f4992f906394a2f9161ba66675887c`.

The compiled action inventory contains exactly two ordered repository mutations:

1. create `src/fmp/discovery/annual_pattern_catalogue_2018_runtime_authorization.py`
   from blob `cd50f50156cf74c34cd97d69d24291dc373b390f`;
2. update `src/fmp/discovery/annual_pattern_catalogue_runtime.py` from current
   blob `e9cbc76dc9e6866e80088d223498fbcc3b870fd1` to target blob
   `410180c34a9e3500bbbb42310a5253b993ac7785`.

The repository-hosted DEC-549 builder is contents/actions read-only and does not
apply the action. It requires the 2018 gate target to remain absent, the current
runtime to remain unchanged, annual history to remain exactly
`{1, 376, 377, 378, 379}`, and run 380+ to remain absent.

DEC-549 authorizes only the future exact two-file repository mutation. Runtime
installation is not yet complete, the runtime gate is not yet active, annual
dispatch remains false, and run 381+, 2019+, strategy/promotion, broker/order,
real-money, and trading remain locked.

## Next gate

`APPLY_EXACT_ANNUAL_PATTERN_CATALOGUE_2018_RUNTIME_AUTHORIZATION_INSTALL_ACTION_AFTER_DEC549`
