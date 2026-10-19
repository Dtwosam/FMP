# DEC-1768 — No-follow ancestor-directory admission for both offline reports

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of PR #2014 at `f7eaf7fc672f3ef04b81f8701af18136c0abdd06`.

The no-follow reader introduced in DEC-1762 and DEC-1766 applied `O_NOFOLLOW` only to the **leaf** documentary file. A caller-supplied `--docs-root` or `--phase7-document` path could traverse an ancestor-directory symlink. This patch opens the absolute filesystem root and **each path component as a directory file descriptor using O_DIRECTORY | O_NOFOLLOW**, then opens the final regular leaf relative to the last verified directory FD with O_NOFOLLOW, O_NONBLOCK, fstat and bounded reads. It never `resolve()`s a symlink into a trusted path, and fails closed on OSes without required dir_fd/no-follow support.

The two readers continue to reject special files, empty/unbounded sources, and changed source bytes. Source SHA pins and exact historical research facts remain unchanged. Normal offline reports remain BLOCKED/RETROSPECTIVE with nonzero exit3; invalid or symlinked ancestors give explicit BLOCKED stderr/exit2/no stdout. No protected market files, runner/GitHub security API, or order execution is used.

Adds **6** focused path tests (**6449 proposed cumulative source-defined**) for each reporter's ancestor-symlink rejection, CLI no-output refusal and ordinary real-directory success. This is a local path safety improvement, not proof of effective installed runner OS isolation or administrator no-bypass controls. #779/#820/#821 still BLOCKED, and protected 2023/run385, strategy selection and all broker/demo/live trading remain unauthorized. Exact-head Phase3/full historical/general CI and independent review required.
