# DEC-661 — Disposable exclusive external report publication witness

**DRAFT / NEVER MERGE / source-only / nonauthorizing.**

This is a narrow synthetic implementation rehearsal for the external report boundary requested in DEC-650 draft #820. It is not deployed in an annual workflow or trading runtime and cannot authorize annual run 385.

## Source-only behavior

The CLI has no user-controlled file or directory destination. Default invocation prints a BLOCKED JSON result and exits 2:

    python -B scripts/dec661_disposable_exclusive_publisher.py

Explicit opt-in creates only a new disposable checkout and output directory under fixed /tmp:

    python -B scripts/dec661_disposable_exclusive_publisher.py --execute-disposable-demo

It writes a constant, public synthetic JSON payload into a randomly named, exclusive-created pending file under the external directory using a directory descriptor, O_EXCL and O_NOFOLLOW. After writing all bytes and fsyncing that file, it publishes with os.link to the fixed external result name: a final file, symlink or FIFO collision is rejected instead of replaced. There is no fallback rename-overwrite. It verifies exact report bytes, collision resistance, unchanged symlink target, synthetic failure cleanup, and unchanged fake checkout contents and inventory.

Results are only:
- BLOCKED, exit 2, on any missing/unreliable synthetic property or unsupported platform.
- LOCAL_DISPOSABLE_WITNESS_UNVERIFIED, exit 3, if this local scenario is internally consistent. It is NEVER a security PASS.

Every result includes can_authorize_dispatch=false and independent_os_proof_verified=false.

The 12 synthetic-only regressions cover exact bytes, collision, symlink/FIFO non-follow, empty/oversized payload, partial/failed writers, non-progress, cleanup, inert default CLI, unsupported environment and nonzero opt-in behavior. No protected or historical artifact is loaded.

## Precise limitations

This demonstration assumes its generated external directory is a trusted single-writer namespace. An adversarial privileged sibling could change directory contents or aliases; the code does not prove race-safe cleanup, absence of writable checkout aliases, durable delivery to GitHub artifacts, actual production runner permissions, rollback on fsync errors, or correctness of cross-filesystem publication. os.link requires pending/final files on the same filesystem; failures are BLOCKED and must never be silently retried.

The demonstration's file is a trivial public synthetic report, not a real annual result. A trusted uploader, independently authenticated observer and independent OS acceptance matrix across preflight + 18 cells + freeze still require separate reviewed implementation. A completed local demo or green CI is not DEC-650 approval.

The separate DEC-651 draft #821 and issue #779 mutable-main exclusive one-shot dispatch race remain BLOCKED. Nothing in this draft is a dispatcher.

Hard stops: never merge/promote, access protected data, dispatch/test/retry annual run385, change installed workflow or ref/rulesets/permissions/runner settings, or perform broker or trading actions. Independent code/security review remains required.
