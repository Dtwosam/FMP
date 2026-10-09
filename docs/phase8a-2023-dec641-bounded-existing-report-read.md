# DEC-641 — Bounded, nonblocking existing audit report reads (NEVER MERGE)

**DRAFT research-only change stacked on [#810](https://github.com/Dtwosam/FMP/pull/810).** This is not a candidate for automatic merge or an authorization change. All 23 assess-only CLI callers, installed workflows, annual runtime, 2023 run385, and broker/trading components are untouched.

## Confirmed defect

The exclusive and atomic helpers (DEC-635–640) determine whether a pre-existing external report is identical using `target.read_text(encoding="utf-8")`. An output path chosen by a caller can be a POSIX named pipe, not a regular file. Calling the reader on an existing FIFO without a writer **blocks indefinitely**; a one-second real subprocess reproduction against the previous helper timed out. Special devices and gigantic regular files also must not be read as unbounded report content.

## Narrow solution

Change only the shared existing-output comparison routine, keeping DEC-640's private staging/atomic `os.link` publication unchanged. Open an existing leaf via `os.open` using read-only `O_NONBLOCK` and `O_NOFOLLOW` flags where available, then inspect **the open file descriptor** with `os.fstat` and reject non-regular file types without reading. Require exact UTF-8 byte-size equality to the already calculated report content, and perform at most `len(expected_bytes)+1` bytes of reading before comparison. For non-regular, missing, unreadable, symlinked, corrupt or mismatching output, keep the caller's existing conflict error and never rewrite any inode.

This check covers both a pre-existing leaf found by `target.exists()` and one that appears during the `os.link` publication race. It does not grant any permission to replace a pre-existing output. Legitimate matching regular-file content (including hardlinks) remains idempotent without changing mtime.

## Regression

Six focused new unit methods: a real FIFO subprocess with an explicit three-second timeout, matching regular report preservation, direct symlink refusal, oversized report refusal, mismatch preservation, and a named-pipe competitor inserted at the final link race. The combined local DEC-640+641 focused suite passed **20/20 tests**. Prior to this fix, an actual subprocess using the old helper with an existing FIFO timed out after one second. Full exact-head GitHub CI is separately required; local tests do not establish a landing gate.

## Limits and landing blocks

On platforms missing `O_NONBLOCK` or `O_NOFOLLOW` flags, the helper cannot claim the same nonblocking/nofollow syscall properties; independent portability review remains needed. Parent-directory replacement between checkout output boundary check and report publication remains out of scope. A privileged actor may change a regular file after it is opened or measured; this proposal prevents unbounded special-file reads and overwrites, not external actor tampering. Existing DEC-640 mode-0600 published output and possible crash-orphan temporary-file semantics remain subject to review.

Do **not** merge this draft or parent rehearsals #809/#810. Original #796–800 still require exact-head independent review; Codex code-review usage limits previously blocked those requests. Protected immutable-ref admission, main branch protection/rulesets, and annual run385/attempt1 remain independently blocked. No GitHub workflow dispatch, protected historical-data access, merge, tag/ruleset or trading operation is authorized.
