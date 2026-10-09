# DEC-640 — Complete-leaf publication research (DRAFT / NEVER MERGE)

**Scope: uninstalled audit-only sandbox stacked on [draft #809](https://github.com/Dtwosam/FMP/pull/809).** Do not merge this PR or its parent. No installed 2023 runtime or workflow change, no annual dispatch, run385, retries, broker or trading actions.

## Reproducible correctness gap

The shared DEC-635–638 leaf `Path.open("x")` writer creates its final filename immediately, **before** writing its report bytes. Although this prevents overwrite of a previously created leaf, a simultaneous identical writer can see an empty or partial report and reject identical content, and a process interrupted during writing can leave a permanently partial final report. The existing tests covered a complete competing file inserted before exclusive open, not a real concurrent pending writer or a partial visible final report.

## Proposed replacement, separately reviewable

Keep the 23 calling CLIs unchanged. In the same shared helper, create a private sibling via `tempfile.mkstemp()`, write and `fsync` all report bytes, and **publish by `os.link(staged, target)`** in the same directory. Creating a hardlink fails with `FileExistsError` if the final leaf already exists, so conflicting reports are never replaced; identical existing reports still return without rewrite. Unlink the sibling in a `finally` clause after success, conflict, or normal failure. The result is fully written before its public filename is created. Private temp files use restrictive default permissions (typically 0600).

The static tests from DEC-635, DEC-636, DEC-637, DEC-638 and DEC-639 are updated to check the **actual new atomic no-overwrite mechanism**, not to insist on the old `target.open('x')` spelling. Original competing-file regressions now inject a competitor at the `os.link` publication point. Eight additional unit tests cover an explicitly verified invisible-until-complete publication, adversarial competing leaves, hardlink integrity, dangling symlinks, genuine simultaneous equal-content writers and simultaneous conflicting writers. The initial local standalone implementation passed **8/8** such tests and compileall; this is **not** substitute for exact-head full GitHub CI.

## Residual hazards

This is **leaf-level atomic publication**, not a defense against privileged attackers swapping parent-directory path components after checkout boundary resolution. It does not provide crash-durable directory entry semantics (directory fsync not performed), eliminate temporary siblings orphaned by a killed process, or prove safety on arbitrary filesystem / platform hardlink configurations. A filesystem that refuses hardlink creation fails closed rather than falling back to clobbering writes. No code here may become a live admission, dispatch or trading gate without an entirely separate independent security review. The original #796–800 review blocker and one-shot run385 hold persist.
