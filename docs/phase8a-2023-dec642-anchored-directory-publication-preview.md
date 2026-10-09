# DEC-642 — Anchored-directory report publication proof (DRAFT, NEVER MERGE)

**This is an isolated source-only research module and test suite** stacked on [draft #811](https://github.com/Dtwosam/FMP/pull/811), not a replacement of its shared report writer. All 23 actual CLI wrappers continue using the original helper. There are no workflow, annual runtime, protected-data, broker or trading changes.

## Demonstrated parent-directory race

The existing DEC-640/641 helper first resolves and checks the output path but later calls `tempfile.mkstemp(dir=target.parent)` followed by `os.link(staged, target)` with pathnames. In a deterministic **TemporaryDirectory-only** regression, an attacker swaps the intended external output parent for a symlink to a synthetic checkout immediately before `mkstemp`: the existing helper then creates the public audit report **inside that synthetic checkout**, despite the earlier boundary check. A separate locked inventory file stays unchanged. The test is deliberately a negative witness of the *prior* implementation's vulnerability, not evidence that the production helper has been fixed.

## Separate anchored proof

`annual_pattern_catalogue_2023_dirfd_publication_preview.py` is deliberately never imported by the 23 CLIs. It traverses the absolute output parent path from the root using successive `os.open(component, O_DIRECTORY|O_NOFOLLOW, dir_fd=...)` calls, creating absent directory components with `os.mkdir(..., dir_fd=...)` anchored to the opened parent; it does not follow directory symlinks. The final opened parent directory descriptor is then used for `os.stat`, bounded regular-file reads, exclusive random private-stage creation, `fsync`, `os.link` publication, and temporary-file unlink. Names are resolved relative to the **same opened directory inode**, not by re-reading the possibly-swapped parent pathname.

Portability checks reject platforms missing nofollow/nonblocking flags or descriptor-relative operations; no silent fallback to unsafe pathname-based publishing. The output basename remains valid up to the filesystem limit and all writes are exclusive; equal-content repeats preserve the original inode. Other platforms/filesystems are **not** certified.

## Local tests and outcomes

The seven initial proof tests passed locally, including eight competing equal writers, eight competing different writers, long 250-character leaf, matching/conflicting/dangling existing leaves, and parent symlink insertion both before and **after** directory descriptor acquisition. Adding the explicit prior-helper negative witness brings the GitHub candidate to **eight tests**; full GitHub CI must validate the exact head before any claim of merged-tree compatibility.

## Residual limitations / future integration work

- **Not integrated into live audit CLIs.** The current shared helper remains vulnerable to adversarial parent-directory replacement; the prototype addresses only the isolated algorithm.
- Even descriptor-anchored publication cannot stop an attacker from moving/removing the directory after open; a successful report may be placed into a renamed, unreachable original directory. It prevents being redirected into the replaced path but does not guarantee the user sees the report at the pathname afterward.
- Parent path symlinks (including legitimate external symlinks) are rejected, so it changes compatibility; directory traversal needs execute/read permission and POSIX `dir_fd` support.
- Mode-0600 outputs, full-directory crash durability, temporary files after abrupt process termination, output-root ownership/trust, and checkout-boundary enforcement are not resolved or independently reviewed.
- Existing independent reviews for #796–800 are absent due to Codex usage-limit replies, main remains unprotected with no rulesets, and **annual run385 must not be dispatched or retried**.

Never merge this draft or #809–811 on the basis of proof results. No changes to external data, annual executions, tags, rulesets, branch protections, PR merges, or trading are authorized.