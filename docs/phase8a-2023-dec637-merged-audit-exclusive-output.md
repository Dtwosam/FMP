# DEC-637 — Exclusive leaf-file creation for two merged audit CLIs

**DRAFT / NO MERGE / NO DISPATCH / NO TRADING.** This change is stacked directly on the current **unmerged PR #799** head `b89d8aa75320ecc721fd39a550111a2723f9026f`. It leaves the original PR untouched.

The DEC-630 checkout-output path restrictions on DEC-625 (`review_manifest_identity_separation`) and DEC-626 (`precheckout_job_if_preview`) had an external-report check-then-write race. A second process could create the previously absent output after `target.exists()` but before `target.write_text()`, allowing unintended overwrites.

Both CLI scripts retain their existing pre-import bytecode suppression, source checkout boundary guard and unchanged conflict message, and now use `fmp.discovery.annual_pattern_catalogue_2023_external_report_create.write_once_external_report`. The shared helper and its seven deterministic race/hardlink tests are the **same Git blobs** as those in stacked draft PR #805 (DEC-635) and #806 (DEC-636). The helper creates only an absent leaf using `Path.open("x")`, never rewrites an identical existing report, rejects conflicting concurrent creation, and fails closed on dangling target symlinks.

Updated the existing DEC-630 guard structural test to require the exclusive writer rather than asserting the intentionally removed `target.write_text`. Two new integration structural regressions require the guard to precede the helper call in both scripts and confirm no dispatch/network implementation was added. Existing real subprocess checkout-boundary tests should continue to pass.

**Limitations:** not parent-directory isolation under a malicious local actor, not atomic final publication under process interruption, and not GitHub ref/CI authentication. No annual 2023 workflow, historical protected artifact, run385/attempt 1, dispatch/retry, merge permission or trading action is touched or authorized.

The original independent review and exact-head CI gates still apply. The shared helper file and tests in drafts #805–807 must be reconciled when deciding landing order, not duplicated or treated as independent implementations. Safety tracking issue #779 remains OPEN.
