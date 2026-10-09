# DEC-643 — Actual shared audit writer anchored to directory descriptors (DRAFT / NEVER MERGE)

This is a **separate integration rehearsal**, stacked on [DEC-642 draft #812](https://github.com/Dtwosam/FMP/pull/812). Unlike isolated #812, the current preview **does change** the shared `write_once_external_report()` implementation used by all 23 2023 offline audit/report CLIs. The 23 CLI wrappers themselves remain byte-for-byte unchanged; their existing source-checkout denial and no-bytecode guards still apply. **Nothing in this draft is authorized for merge, deployment or annual dispatch.**

## Why integrate

Prior DEC-640/641 writers used `tempfile.mkstemp(dir=target.parent)` then `os.link(staged, target)` by mutable pathnames, permitting an external directory symlink swap after source checkout boundary validation to redirect a report into a synthetic checkout. DEC-642 demonstrated this in a disposable TemporaryDirectory-only negative witness. DEC-643 makes the CLI-imported shared helper call the validated rooted directory-descriptor writer, and updates that negative witness into a new **positive real-helper checkout protection test**.

## Mechanics

The shared helper delegates directly to `preview_write_once_external_report`. That module opens absolute directory path components one at a time using `os.O_DIRECTORY | os.O_NOFOLLOW` with parent `dir_fd`, optionally creating missing directories anchored to the opened parent. All final `stat`, byte-bounded file reads, exclusive 0600 sibling creation, `fsync`, hardlink publication and unlink operate on that same open directory descriptor. Its capability check is cached at import time to preserve deterministic patched syscall regressions; per-call constants are still inspected to reject missing nofollow/nonblocking flags. No fallback to unsafe pathname publication is allowed. Existing contents are accepted only for regular matching UTF-8 bytes; dangling/symlink/pipe/conflict leaves reject without clobbering.

The existing DEC-635/636/637/638/639 structural tests are **retargeted** from the old `os.link(staged, target)` spelling to shared-helper delegation, and still require `FileExistsError` conflict handling in the anchored module. Deterministic DEC-640/641 injected races now use the destination leaf name and preserve actual dir_fd semantics, rather than testing the outdated absolute destination spelling. Three new DEC-643 integration methods verify all 23 CLI guards and anchor operations, refusal of preexisting parent symlinks, and that a swapped parent **after the helper pins its directory FD** cannot redirect a report into a checkout.

## Limitations requiring independent review

- A directory renamed or deleted after the parent FD is opened may yield a report in the original detached directory rather than at the user's requested current pathname. This is fail-safe with respect to checkout redirection, not a delivery guarantee.
- Legitimate external symlinked parent paths are rejected; non-POSIX platforms lacking `os.supports_dir_fd`, O_DIRECTORY, O_NOFOLLOW or O_NONBLOCK reject rather than using an unsafe fallback. Platform/file-system compatibility has not been independently reviewed.
- Fully written files are published with private 0600 permissions, potentially tighter than earlier umask-dependent 0644 reports. This is a behavior change requiring reviewer approval.
- Crash durability for the directory entry, temporary siblings orphaned by SIGKILL, post-open directory ownership/trust, and adversarial external modifications of report bytes still require separate consideration.
- No live annual runtime, GitHub workflow files, tags/rulesets/branch protection, historical protected artifact, broker or trading action changed.

**Review/merge gate:** All original #796–800 exact-head independent reviews are still missing; Codex review bot previously reported usage limits. Main is unprotected with no rulesets at last check, and one-shot run385 is unconsumed. The entire #809–813 preview chain is DRAFT / NEVER MERGE pending separate independent security signoff, full exact-head CI and an authorized, reviewed landing plan.

## Evidence standard

Initial DEC-642 anchored proof passed seven local tests; the #813 branch tests the integration and must pass the full GitHub PR synthetic merge test workflow, Phase 3, and package compilation before any compatibility statement. Source vs GitHub synthetic merge SHA/parents/tree must be recorded. Author-side tests are not independent review.