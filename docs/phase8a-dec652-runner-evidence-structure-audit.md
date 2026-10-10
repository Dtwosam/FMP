# DEC-652 — Offline annual-runner evidence structure audit

**DRAFT / NEVER MERGE / source-only / non-authorizing.**

This executable checker complements [DEC-650 runner-isolation contract](https://github.com/Dtwosam/FMP/pull/820). It only reads two local JSON files (a source-identity policy and a submitted evidence ledger) and writes a JSON diagnostic to stdout. It never runs a historical workflow, reads protected datasets, contacts GitHub, acquires privilege or touches trading systems.

## Output is never approval

- **BLOCKED** (exit 2): missing, conflicting, skipped, failed or structurally unsafe evidence.
- **STRUCTURALLY_COMPLETE_UNVERIFIED** (exit 0): every specified field is present and consistent in *untrusted JSON*. This is **not a security PASS**.
- Both states **always** include can_authorize_dispatch=false and independent_os_proof_verified=false.

An actor may fabricate plausible observations, check statuses and hashes. This code cannot independently authenticate those statements. The actual DEC-650 reviewer must verify real OS mounts, capabilities, inherited descriptors, checkout inventories, report receipts, kernel measurements and observer provenance. This checker is neither an OS enforcement mechanism nor a GitHub dispatch admission control. Passing it can **never** consume or authorize run 385.

## Reviewed policy and ledger shape

The **policy** JSON has schema=dec650-structural-ledger-v1, repository=Dtwosam/FMP, a 40-hex source_commit/source_tree/workflow_blob, explicit workflow_ref, segment=2023, **exact integer run_number=385**, **previous_freeze_run_id=37663157285**, and run_attempt=1. The reviewer must separately authenticate its *exact raw-byte* SHA-256 before providing --policy-sha256. Self-generating a matching policy and hash does not establish independent authority.

The **ledger** repeats each policy identity and includes **20 uniquely identified job records**: one preflight, one freeze, plus 18 distinct cells spanning 3 symbols (EURUSD, GBPUSD, USDJPY), 3 timeframes (5m, 15m, 1h) and two horizons (60, 240). These coordinates reflect the committed annual workflow matrix at Git blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1. No job is launched to collect data.

Each job requires a positive unique job_id, kind and exact matrix coordinates (null for non-cells), runner_image/kernel/mount_namespace/mountinfo_sha256/source_mount_id, non-root restricted_uid, no_new_privs=true, effective_capabilities="0" (normalized), checkout_mount_readonly=true, empty writable_checkout_aliases and unapproved_inherited_fds, safe standard_streams for FD 0/1/2, and equal 64-hex checkout before/after digests. These values are unverified *claims* supplied by the ledger author.

Every job must contain exactly twelve checks, each with status=PASS, skipped=false, privileged_test_executed=true, and a 64-hex evidence_sha256:

- source_mount_enforced_readonly, checkout_path_write_denied, chmod_or_privilege_recovery_denied
- directory_reparent_denied, writable_alias_denied, inherited_fd_contained, stdio_fd_0_1_2_contained
- credential_leak_denied, checkout_inventory_unchanged, exclusive_external_publication
- concurrent_publication_conflict_denied, failure_cleanup_clean

A missing or duplicate job, wrong identity, wrong 385/2022 predecessor, wrong attempt, root actor, writable alias, leaked descriptor, skipped/failed check, missing evidence hash, changed checkout digest or mismatched policy digest yields BLOCKED. None of the data can be promoted from structural completeness to real OS proof without a separate trust mechanism and independent review.

## Local commands

Only use previously collected, non-protected, independently permitted inputs:

    python -B scripts/dec650_ledger_structure_audit.py \
      --policy /outside/review-policy.json \
      --policy-sha256 REVIEWER_AUTHENTICATED_64_HEX_DIGEST \
      --ledger /outside/runner-ledger.json

Run the 32 synthetic regression cases without root, network, historical data or GitHub authorization:

    python -B -m unittest discover -s tests -p 'test_dec650_ledger_structure_audit.py' -v

Inputs over one mebibyte, non-regular files (including FIFOs/directories), symbolic-link leaves and malformed JSON job kinds fail closed with structured BLOCKED results. The input opener uses nonblocking/no-follow descriptor flags and checks the opened inode with fstat; platforms lacking these safeguards reject the input rather than falling back to an unsafe open. These are **input robustness checks**, not filesystem isolation of an annual workflow. JSON decoding additionally rejects duplicate object keys at any nesting depth and non-standard NaN/Infinity literals, so contradictory attestations cannot be silently normalized by the parser. Deeply nested evidence that exceeds the JSON decoder's recursion limit is reported as structured BLOCKED rather than terminating with an unhandled traceback. The synthetic success fixture explicitly demonstrates that **fabricated complete JSON still has no authorization authority**. The regressions also exercise missing/duplicated matrix jobs, identity drift, privilege skips, unsafe FD aliases, bad inventory, false capability policy and invalid reviewer policy digest.

## Scope and hard stops

No installed workflow or runtime authorization, branch/tag/ruleset, CI workflow, protected-data path, broker connection, or trading strategy is changed by this PR. The tests execute only against disposable synthetic fixtures. Original PRs #796–800 remain unreviewed; [issue #779](https://github.com/Dtwosam/FMP/issues/779) still blocks immutable/exclusive one-shot dispatch; [DEC-651 #821](https://github.com/Dtwosam/FMP/pull/821) is a design, not a deployed control. All annual security/authorization gates remain BLOCKED; run 385 must remain unconsumed.
