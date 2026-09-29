# Phase 8A — EXP-062 Workflow-Install Action Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY INSTALL-ACTION CONTRACT / NO INSTALL OR DISPATCH  
**Decision:** DEC-417  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-416

DEC-417 consumes the concrete DEC-416 final-authorization proof runtime freeze and
adds only a source-level contract for a future workflow-install action.

It pins:

- DEC-416 runtime-freeze blob
  `23120b4a763fb1702d2f953c8cfb10db3ce6de27`;
- DEC-416 runtime-freeze fingerprint
  `3f90062e42cc36c61286b31fcd625a7e511140819c19f268e283be1807e2f0c7`;
- the dormant executor workflow template.

All seven predecessor source-only gates remain true. DEC-417 adds
`active_one_shot_historical_executor_workflow_install_action_contract_source_authorized=true`.

Actual workflow-install authorization remains false. The active executor workflow
path must remain absent. Installed state, executor availability, historical-result
dispatch, execute mode, reserved-data access, Phase 8B, demo, broker/live,
real-money, and trading remain locked.

## Next gate

A read-only current-main workflow-install action preflight. It may verify that the
action contract is still valid, but it cannot create the workflow or dispatch
historical discovery.
