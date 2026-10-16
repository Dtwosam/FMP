# DEC-1420 — Fail-closed unknown matrix row field diagnostics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1643 DEC-1419 at 4d46caa12afa84dfb82305a22f250ce570ddbd7f. Seven new unittest methods, **1,445 proposed source-defined methods**.

DEC-1410's source matrix reviewer appended a MATRIX_FIELDS_DRIFT finding when a seven-field row contained an unknown or substituted field name. It then accessed required keys with direct dictionary indexing. An unrecognized replacement for feature_artifact_id, outcome_zip_sha256, symbol, or timeframe could therefore raise a KeyError rather than produce the promised fail-closed diagnostic. This patch makes unknown/missing row key inventories return an immediate MATRIX_FIELDS_DRIFT finding before downstream identity checks, and adds synthetic source mutations showing the error is contained across base matrix, source literal pin and strategy wrapper reviews.

This corrects **only the source-only test reviewer** and improves reviewer output on unrecognized YAML syntax; it does not change the installed annual workflow, validate an actual remote artifact, prevent GitHub's run-number race, or prove an OS original no-write policy. No protected data access, annual dispatch/retry, settings/ruleset/branch mutation, production or trading work was performed.

Requires independent code review and its own exact-head Phase 3 plus full historical CI. The prior failed #1634–#1636 exact heads remain failed. DEC-650/#820 actual original protected OS isolation and DEC-651/#821/#779 immutable exclusive 2023 run385/attempt1 server-side admission remain BLOCKED.
