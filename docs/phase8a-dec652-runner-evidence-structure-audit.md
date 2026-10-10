# DEC-652 — Offline annual-runner evidence structure audit

**DRAFT / NEVER MERGE / source-only / non-authorizing.**

This executable checker complements [DEC-650 runner-isolation contract](https://github.com/Dtwosam/FMP/pull/820). It only reads two local JSON files (a source-identity policy and a submitted evidence ledger) and writes a JSON diagnostic to stdout. It never runs a historical workflow, reads protected datasets, contacts GitHub, acquires privilege or touches trading systems.

## Output is never approval

- **BLOCKED** (exit 2): missing, conflicting, skipped, failed or structurally unsafe evidence.
- **STRUCTURALLY_COMPLETE_UNVERIFIED** (exit **3**, deliberately nonzero): every specified field is present and consistent in *untrusted JSON*. This is **not a security PASS**. A wrapper which executes `if audit; then ...` must never treat this unverified evidence as success.
- Both states **always** include can_authorize_dispatch=false and independent_os_proof_verified=false.

An actor may fabricate plausible observations, check statuses and hashes. This code cannot independently authenticate those statements. The actual DEC-650 reviewer must verify real OS mounts, capabilities, inherited descriptors, checkout inventories, report receipts, kernel measurements and observer provenance. This checker is neither an OS enforcement mechanism nor a GitHub dispatch admission control. Passing it can **never** consume or authorize run 385.

## Reviewed policy and ledger shape

The **policy** JSON has schema=dec650-structural-ledger-v2, repository=Dtwosam/FMP, a 40-hex source_commit/source_tree/workflow_blob/**synthetic_merge**, exact workflow_ref=refs/heads/main for the **currently installed workflow** (any future reviewed tag amendment requires a new contract), independent_reviewer_identity, an **independent_review_receipt_sha256** required in both the reviewed policy and ledger, an exact reviewed env_allowlist_keys list restricted to conservative safe variable **names** and repeated identically at ledger top level, segment=2023, **exact integer run_number=385**, **previous_freeze_run_id=37663157285**, and run_attempt=1. The reviewer must separately authenticate its *exact raw-byte* SHA-256 before providing --policy-sha256. Self-generating a matching policy and hash does not establish independent authority.

The **ledger** must repeat **every** policy identity, including the reviewer-receipt digest and ordered environment allowlist, and includes **20 uniquely identified job records**: one preflight, one freeze, plus 18 distinct cells spanning 3 symbols (EURUSD, GBPUSD, USDJPY), 3 timeframes (5m, 15m, 1h) and two horizons (60, 240). These coordinates reflect the committed annual workflow matrix at Git blob 09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1. No job is launched to collect data.

Each job requires a positive unique job_id, kind and exact matrix coordinates (null for non-cells), runner_identity/runner_image/kernel/mount_namespace and mountinfo SHA-256, explicit source/input/output mount IDs, observer_identity and manifest digest, UID/GID maps, non-root restricted UID and GID, empty supplementary groups, no_new_privs=true, all effective/permitted/ambient capabilities recorded zero, and seccomp mode `filter` or `strict`. It also requires absolute working directory and executable names with NUL bytes rejected, argv digest, a nonempty exact-match list of environment variable names pinned to the reviewed policy and restricted to PATH/LANG/LC_ALL/TZ/HOME/TMPDIR/PYTHONPATH/PYTHONDONTWRITEBYTECODE/PYTHONHASHSEED, explicit outside-checkout cwd, read-only inputs, external output and separately isolated publisher, empty privileged_skips and unresolved_exceptions, empty writable_checkout_aliases and unapproved_inherited_fds, safe standard_streams for FD 0/1/2, equal 64-hex checkout before/after digests, and observer/attempt/race/external-publication/cleanup SHA-256 receipts. These values remain unverified *claims* supplied by the ledger author; a claimed independent reviewer name or SHA-256 receipt is **not an authenticated signature or approval**. A safe environment variable **name** can still carry an unsafe value: the checker cannot observe or attest process contents. Checking whether fields exist does **not** establish real isolation, independent attestation or byte-level authenticity.

Every job must contain exactly twelve checks, each with status=PASS, skipped=false, privileged_test_executed=true, and a 64-hex evidence_sha256:

- source_mount_enforced_readonly, checkout_path_write_denied, chmod_or_privilege_recovery_denied
- directory_reparent_denied, writable_alias_denied, inherited_fd_contained, stdio_fd_0_1_2_contained
- credential_leak_denied, checkout_inventory_unchanged, exclusive_external_publication
- concurrent_publication_conflict_denied, failure_cleanup_clean

A missing or duplicate job, wrong identity, wrong 385/2022 predecessor, wrong attempt, root actor, nonempty supplementary groups, unconfined seccomp, unaccounted permitted or ambient capabilities, missing observer or race-replay receipt, unsafe environment variable name, writable alias, leaked descriptor, skipped/failed check, missing evidence hash, changed checkout digest or mismatched policy digest yields BLOCKED. None of the data can be promoted from structural completeness to real OS proof without a separate trust mechanism and independent review.

## Local commands

Only use previously collected, non-protected, independently permitted inputs:

    python -B scripts/dec650_ledger_structure_audit.py \
      --policy /outside/review-policy.json \
      --policy-sha256 REVIEWER_AUTHENTICATED_64_HEX_DIGEST \
      --ledger /outside/runner-ledger.json

Run the 48 synthetic regression cases without root, network, historical data or GitHub authorization:

    python -B -m unittest discover -s tests -p 'test_dec650_ledger_structure_audit.py' -v

Inputs over one mebibyte, non-regular files (including FIFOs/directories), symbolic-link leaves and malformed JSON job kinds fail closed with structured BLOCKED results. The input opener uses nonblocking/no-follow descriptor flags and checks the opened inode with fstat; platforms lacking these safeguards reject the input rather than falling back to an unsafe open. These are **input robustness checks**, not filesystem isolation of an annual workflow. JSON decoding additionally rejects duplicate object keys at any nesting depth and non-standard NaN/Infinity literals, so contradictory attestations cannot be silently normalized by the parser. Deeply nested evidence that exceeds the JSON decoder's recursion limit is reported as structured BLOCKED rather than terminating with an unhandled traceback. Error diagnostics do **not** include arbitrary untrusted job kinds or matrix coordinate values: malformed inputs are reduced to fixed internal labels before constructing the JSON findings or emitting CLI stdout. This prevents a submitted canary or accidental secret-like value from being reflected into CI logs, but it does not authenticate the input. The synthetic success fixture explicitly demonstrates that **fabricated complete JSON still has no authorization authority**. The regressions also exercise missing/duplicated matrix jobs, identity drift, privilege skips, unsafe FD aliases, bad inventory, false capability policy and invalid reviewer policy digest.

## Scope and hard stops

No installed workflow or runtime authorization, branch/tag/ruleset, CI workflow, protected-data path, broker connection, or trading strategy is changed by this PR. The tests execute only against disposable synthetic fixtures. Original PRs #796–800 remain unreviewed; [issue #779](https://github.com/Dtwosam/FMP/issues/779) still blocks immutable/exclusive one-shot dispatch; [DEC-651 #821](https://github.com/Dtwosam/FMP/pull/821) is a design, not a deployed control. All annual security/authorization gates remain BLOCKED; run 385 must remain unconsumed.
