# Phase 8A — EXP-062 Final Workflow-Install Authorization Contract

**Date:** 2026-09-29  
**Status:** SOURCE-ONLY FINAL AUTHORIZATION CONTRACT / NO INSTALL OR DISPATCH  
**Decision:** DEC-411  
**Experiment:** EXP-20260927-062  
**Predecessor:** DEC-410

## Purpose

DEC-411 creates the source-only final workflow-install authorization contract after
the complete source-preflight proof/recovery lineage has been concretely bound.

It pins:

- DEC-410 runtime-freeze blob
  `705c08d50a8dfcae5391a0b240d78fea5716a8de`;
- DEC-410 runtime-freeze fingerprint
  `77fa5c98293226176d71a759af44f23e434987a57c66d343c13f7f727202e853`;
- dormant executor workflow template blob
  `51ce87584369be957482460d81649adb1cb9f05d`.

The DEC-410 lineage includes both the genuine failed DEC-404 proof run #1 and the
successful DEC-407 recovery run #2.

## Authority boundary

The six predecessor source-only gates remain true. DEC-411 adds only:

`active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized=true`.

Actual workflow-install authorization remains false. The active executor workflow
path must remain absent.

Installed state, historical executor availability, historical-result dispatch,
execute mode, rerun/retry/replacement, reserved 2023-2026 access, candidate
compilation/promotion, Phase 8B, demo, broker/live, real-money, and trading remain
false.

## Next gate

The next safe gate is a read-only current-main final workflow-install authorization
preflight. It may verify that the final source contract remains valid, but it cannot
install the workflow or dispatch historical discovery.
