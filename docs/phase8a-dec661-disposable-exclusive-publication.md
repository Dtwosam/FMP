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

## DEC-662 disposable simultaneous-publication scheduling test

A second draft variant runs two *synthetic* publishers against the same fixed, external report filename with a concurrency barrier. Each contender stages a different public payload using its own directory FD and tries the link-if-absent step. Over eight disposable rounds, the regression requires exactly **one published winner** and **one FileExistsError loser**, an exact final payload from the winner set, and no remaining pending files. An accidental overwrite or duplicate success fails the test.

This is a scheduling witness of the underlying Linux exclusive hard-link name creation, not a proof of safety under hostile privileged sibling writers, cross-mount aliases, malicious directory replacement, crash recovery, or authentication of real report content. The documented **trusted single-writer assumption remains mandatory** for any actual annual-runner deployment design. One additional regression brings the source-defined total to 13.

## DEC-663 ambiguous publication outcome: fail closed, never retry

**Important distinction:** final-name creation by link-if-absent is atomic, but the durable outcome remains **unknown** after a successful link if a subsequent directory fsync fails or pending-file cleanup raises. Treating this as an ordinary unpublished error could encourage an unsafe replay. The implementation now marks post-link exceptions with **PublicationOutcomeUnknown**, explicitly saying DO NOT RETRY, rather than incorrectly representing the report as absent.

The function tracks whether it crossed the final-name link boundary. It attempts descriptor close and pending unlink separately, even if one fails, and retains the first error. If any error occurs **after** a successful link, it raises PublicationOutcomeUnknown; it does not unlink, overwrite or recreate the final name. Before the link, an error still blocks and attempts to remove the pending synthetic file, without pretending errors in cleanup were recovered.

Four additional fault-injection regressions bring the source-defined total to **17**: staged-file fsync failure leaves no final report, post-link directory fsync failure leaves a final report but raises the explicit ambiguity exception, post-link pending cleanup failure leaves an orphan and raises ambiguity, and all such failure results remain nonauthorizing. The tests assert that a naive second publication attempt receives FileExistsError and cannot overwrite the first bytes. They deliberately use only disposable directories and injected filesystem errors, not protected data or actual workflow artifacts.

This is a source-only negative fault witness, not a crash-recovery protocol, transactional GitHub artifact delivery, exclusive publisher proof or authorization for a second attempt after network ambiguity. An actual production uploader must have an independently specified failure/receipt policy and no automated retry on ambiguous delivery.

## DEC-664 separate cleanup durability and postpublication writer boundaries

Directory metadata changes have two distinct durability points: (a) creation of the final hard-link name, and (b) removal of the pending name. The DEC-663 implementation fsynced the directory **before** unlinking the pending staging filename. Under a crash, the deletion might not yet be durable. This revision adds a **second directory fsync after successful pending unlink**, without ever converting a post-link fsync failure into an ordinary clean abort. Any error after successful final-name link still produces PublicationOutcomeUnknown and the required DO NOT RETRY stop condition.

Two synthetic tests inspect both directory sync calls and inject a failure on **only the second one**: the final report exists, no pending name remains in the live directory listing, yet the result is **ambiguous and non-retryable**, not authorizing. This distinguishes observed state from guaranteed crash durability, and retains the usual limitations of mocked fsync results.

A third intentionally adversarial test exposes the trust assumption behind exclusive creation: after an exclusive file is published, **another actor with direct write authority to that final file can still change its bytes**. The test confirms a duplicate exclusive publication is rejected while a direct same-user write succeeds. Therefore **link-if-absent protects the final filename from publication collisions, not final content immutability**. Without real operating-system separation for the publisher/report and independent receipt verification, a clean local report is not trusted evidence.

There are now **20 source-defined synthetic regression tests** (no real annual dataset). None of these changes establishes a privileged single-writer external namespace, runner isolation, a secure upload receipt, atomic GitHub one-shot dispatch or trading authority. Independent exact-head CI and qualified review remain mandatory.

## DEC-667 incomplete staging cleanup after a pre-link failure

Before DEC-667, the publisher retained the *first* exception from the publication attempt. If a final-name collision raised FileExistsError and subsequent pending-file cleanup also failed, the caller still received **only FileExistsError**, concealing the leaked temporary report and possibly encouraging a retry. The same flaw applied to a staged-write failure followed by failed cleanup.

DEC-667 adds **PublicationCleanupIncomplete**, used when final-name linking did not succeed but descriptor close or pending-file unlink failed. It explicitly says **DO NOT RETRY** and chains the cleanup cause. This is distinct from **PublicationOutcomeUnknown**, which still means the final report name *was linked* but durability/cleanup is uncertain. A normal, clean collision with successful cleanup still raises FileExistsError; a failed cleanup cannot be reported as a clean collision.

Two additional fault-injection regressions bring the synthetic suite to **22 defined tests**, reproducing (a) an existing final name plus deliberately orphaned pending file and (b) staged-write failure plus deliberately orphaned pending file, without any annual data. Both must surface PublicationCleanupIncomplete, leave existing final bytes intact when applicable, and never be treated as safe automatic retries.

Neither exception certifies the actual state of GitHub artifact publication. Both are local source-only stop signals and cannot replace trusted receipt inspection, independent OS isolation, immutable single-authority annual dispatch, or separate authorization.

## DEC-668 verify that final report name refers to the staged inode

The previous publisher exclusively created a pending file and then linked the **pending pathname** to the final report name. A directory actor able to replace the pending pathname *after staging but before the link* can cause the final name to refer to a different inode or even a symlink. O_EXCL on the pending file alone does not bind the later pathname lookup to the original open descriptor. The old implementation could report local publication success without checking that identity.

The new post-link inspection opens the final name using O_NOFOLLOW and O_NONBLOCK, checks its device+inode numbers match the still-open original staged FD, checks both are bounded regular files of expected length, and compares final bytes against the exact public synthetic payload. A failed check **after successful link** raises PublicationOutcomeUnknown with the existing DO NOT RETRY rule; a clean report still does not authorize any annual action.

Four new negative/positive tests bring the source-defined count to **26**. Two use a patched deterministic link boundary to substitute the pending name immediately before the real link syscall: a public symlink and a different public regular inode with even identical bytes. Both must result in explicit publication uncertainty, not a false success. Two test the identity/byte verifier directly. Tests use only disposable public files.

**Limitations:** Post-link verification is a point-in-time check. A privileged or same-UID actor with direct write access can change the report before, during or after that check; this does not establish immutable published content, a trusted observer, host OS separation, remote receipt or production authorization. Reviewers must independently verify source correctness and actual annual-runner control boundaries.

## Precise limitations

This demonstration assumes its generated external directory is a trusted single-writer namespace. An adversarial privileged sibling could change directory contents or aliases; the code does not prove race-safe cleanup, absence of writable checkout aliases, durable delivery to GitHub artifacts, actual production runner permissions, rollback on fsync errors, or correctness of cross-filesystem publication. os.link requires pending/final files on the same filesystem; failures are BLOCKED and must never be silently retried.

The demonstration's file is a trivial public synthetic report, not a real annual result. A trusted uploader, independently authenticated observer and independent OS acceptance matrix across preflight + 18 cells + freeze still require separate reviewed implementation. A completed local demo or green CI is not DEC-650 approval.

The separate DEC-651 draft #821 and issue #779 mutable-main exclusive one-shot dispatch race remain BLOCKED. Nothing in this draft is a dispatcher.

Hard stops: never merge/promote, access protected data, dispatch/test/retry annual run385, change installed workflow or ref/rulesets/permissions/runner settings, or perform broker or trading actions. Independent code/security review remains required.
