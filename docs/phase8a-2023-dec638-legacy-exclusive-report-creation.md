# DEC-638 — Exclusive external report creation for ten legacy offline audit wrappers

**DRAFT / DO NOT MERGE / NO ANNUAL DISPATCH OR TRADING.**

This source-only change is built **directly from unmerged PR #800** head `335149e3087a56fa7c0122b6c16ae44292509748` and does not change #800's exact head or its review evidence.

## Scope

The ten CLI scripts that DEC-631 hardened against source-checkout output writes still used `exists() -> write_text()` for new external reports, exposing an intervening-file overwrite race. They include DEC-613 admin lock handoff, dispatch/immutability/preflight research reports, runtime authorization planning, installation previews and receipts. Names such as "dispatch" in these files describe **offline preflight models**; this change does not call GitHub workflow dispatch, install the annual runtime, or trade.

Each existing CLI retains its checkout-local output prohibition and `sys.dont_write_bytecode=True` initialization. New external report creation now delegates to `fmp.discovery.annual_pattern_catalogue_2023_external_report_create.write_once_external_report`. Where an existing CLI uses an internal `_write_json` function, the source-checkout check remains in the outer command handler before invoking the function. All prior conflict messages and return codes are retained.

The identical helper and its seven deterministic tests are also proposed in separately stacked draft PRs #805, #806 and #807 for other CLI families. Reviewers must reconcile the shared helper/test Git blobs when selecting a landing order rather than installing multiple implementations.

Three additional regressions inspect all ten wrappers, rejecting any return to direct leaf `write_text` calls; ensure each still uses its original source-checkout guard and disables Python bytecode writes; and verify nested `_write_json` helpers are invoked only after the guard in source control flow. Full CI and the existing DEC-631 real CLI subprocess regression suite are required to verify integration.

## Residual threat model

Exclusive file creation prevents a conflicting external file created between a prior existence check and opening a target leaf from being truncated. It is **not** a complete filesystem concurrency lock or atomic finalized-report publication, does not prevent malicious parent-directory substitutions or hostile symbolic link races between resolution and access, and does not sign or authenticate untrusted audit inputs.

No workflow YAML, installed 2023 runtime, protected historical artifacts, main/tag/rulesets, one-shot annual run385, broker, orders, or trading permissions are changed. The merge/review and irreversible-dispatch blocks of issue #779 remain in force.
