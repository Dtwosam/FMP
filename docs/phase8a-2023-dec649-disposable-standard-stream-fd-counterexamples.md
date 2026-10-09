# DEC-649 — Preopened standard-stream descriptor counterexamples (DRAFT / NEVER MERGE)

Source-only follow-up stacked directly on [draft #818](https://github.com/Dtwosam/FMP/pull/818), exact parent head `d6519a3c774fe2a78601ccdaac80fd9c76451bcb`. **No installed GitHub workflow, annual runner, wrapper, report writer, main, tag, ruleset, checkout, protected evidence, broker or trading changes.** Only the previously disposable DEC-647/648 test module and this new document change.

## Finding: standard descriptors evade ordinary FD closure

Even when `subprocess.run(close_fds=True)` drops ordinary inherited descriptors and the child has `NoNewPrivs=1`, `CapEff=0` and a restricted UID, descriptors **0 (stdin), 1 (stdout), and 2 (stderr)** are separate channels. A privileged parent may connect them to an already-open protected file, enabling a restricted child to read or write without gaining permission to open that file by path. An environment allowlist does not fix this.

The normal **disposable test helper** now explicitly supplies `stdin=subprocess.DEVNULL` while retaining `capture_output=True`, `close_fds=True`, the fixture `cwd`, the existing three-key synthetic environment and `setpriv` identity/capability drop.

Four new root+`setpriv`-gated test cases use **only** disposable synthetic fixtures:
1. Normal restricted test child observes UID 65534 and reads EOF from stdin.
2. A separate, deliberately unsafe child reading a root-owned synthetic `0600` canary passed as `stdin` receives its bytes **despite** UID/capability restrictions and `close_fds=True`.
3. Control: the restricted actor receives `PermissionError` trying to create a checkout-local synthetic file by path.
4. **Deliberate checkout inventory violation in the synthetic fixture only:** privileged setup opens `synthetic-preopened-stdout.txt` *inside the disposable root-owned checkout*; a UID-65534 child successfully writes through FD 1, despite denial by path. The synthetic checkout's separate inventory sentinel stays unchanged, but the additional file demonstrates the security issue.

One always-run static regression verifies that the **normal** child helper explicitly sets DEVNULL stdin, captures stdout/stderr, closes other descriptors, and does not pass file descriptors into the child. The module now has **20 tests: 15 root-gated and 5 always-run**. On normal GitHub unprivileged runners, **15 skips are expected**; green CI with skips does not certify production isolation.

## Evidence and limitations

A standalone disposable local Linux root+`setpriv` probe reproduced the stdin, by-path, and preopened-stdout counterexamples. Exact new source/merge CI and full-module execution must be checked independently. No tests initiate privilege escalation, networking, protected data reads, annual workflow dispatch or actual checkout mutation.

This is a **negative fixture**, not a production repair. In particular, a checkout that the restricted child cannot modify by path may still be modified through a writable preopened descriptor. Conversely, ensuring `stdin=DEVNULL` and `capture_output=True` in *this testing helper* is not evidence that actual FMP jobs protect all standard descriptors or execute an OS-enforced privilege boundary. Review inherited stdio, `pass_fds`, checkout-parent writable aliases, runner sudo/remount capability, user namespace, token/external-secret FD inheritance and output collection across all three jobs before authorization.

## Hard stop

Independent reviews for original #796–800 are still missing. These stacked source experiments #809 onward are all **DRAFT / NEVER MERGE**. [Tracking issue #779](https://github.com/Dtwosam/FMP/issues/779) still blocks the mutable-main server-side dispatch race and run 385. No merge, 2023 annual dispatch/retry, permission/ruleset/tag changes, protected data manipulation, broker execution or trading authority is granted by this experiment.
