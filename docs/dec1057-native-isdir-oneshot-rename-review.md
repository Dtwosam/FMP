# DEC-1057 — One-shot rename pair evidence across files and directories

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit documentation-only child of DEC-1056/#1277. The stack remains at **691 source-defined test methods**. No runtime code, executable tests, CI workflow, protected annual evidence/source, production ref, runner, ruleset, permission, broker or trading change.

## Native Linux cookie and type evidence belong to event records, not to inferred complete transactions

| Case | Parent-only one-shot subscription | Actual first kernel one-shot buffer | Separate independent native parent buffer | Why it is incomplete |
| --- | --- | --- | --- | --- |
| DEC-1052/#1273 | `IN_MOVED_FROM | IN_ONESHOT` for **regular file** | `IN_MOVED_FROM` with nonzero cookie and original basename; then `IN_IGNORED` | Genuine paired `IN_MOVED_FROM` and `IN_MOVED_TO`, same nonzero cookie | First one-shot matching event removes watch **before destination event** is delivered |
| DEC-1054/#1275 | `IN_MOVED_TO | IN_ONESHOT` for **regular file** | `IN_MOVED_TO` with nonzero cookie and destination basename; then `IN_IGNORED` | Genuine paired FROM/TO, same nonzero cookie | Filter excludes SOURCE half of rename; TO event alone does not identify source path |
| **DEC-1055/#1276** | `IN_MOVED_FROM | IN_ONESHOT` for **directory entry** | **`IN_MOVED_FROM | IN_ISDIR`** with nonzero cookie and old directory basename; then `IN_IGNORED` | **`IN_MOVED_FROM | IN_ISDIR`** and **`IN_MOVED_TO | IN_ISDIR`** with same positive cookie | Directory type bit confirms named entry type, not completion of two-event rename pair |
| **DEC-1056/#1277** | `IN_MOVED_TO | IN_ONESHOT` for **directory entry** | **`IN_MOVED_TO | IN_ISDIR`** with nonzero cookie and new directory basename; then `IN_IGNORED` | Full FROM/TO **with `IN_ISDIR`** and same positive cookie | Directory rename destination alone cannot establish actual source path or uninterrupted parent watch |

All four tests use actual Linux kernel event buffers and successful `os.rename` on newly generated, disposable PUBLIC `/tmp` data. Directory tests additionally verify stable nested public marker file and restored parent/child device, inode and mode. Distinct native inotify instances, rather than `dup()` aliases, supply independently readable experiment controls. The original source+parent watcher receives both sides of a rename, each with a matching nonzero cookie and correct directory type flag when applicable. In every one-shot case, actual `IN_IGNORED` marks the automatic loss of the partial-observer watch, and genuine later renames remain visible only on the still-live full watcher.

A kernel `IN_ISDIR` action modifier on a rename is not the same as `IN_ONLYDIR`, which is a **registration-only guard**. Likewise a nonzero rename cookie identifies a kernel pairing relationship only if the matching counterpart is actually present and coherently observed. Do not fabricate a missing counterpart, infer full provenance from `IN_IGNORED`, or treat clean final bytes/identities as independently OS-enforced write confinement.

## Unchanged evaluator and exact-head review

The unchanged two-watch public evaluator must remain `status=BLOCKED` with `can_authorize_dispatch=false` and `independent_os_proof_verified=false` for witnessed native rename/namespace activity. A coherent empty disposable receipt is only `LOCAL_DISPOSABLE_WITNESS_UNVERIFIED`, also nonauthorizing, as corrected in DEC-1047/#1268 without touching the observer runtime. Neither local inotify evidence class can independently authorize protected annual execution.

- DEC-1054/#1275 exact SHA `f916bd2830e35819ae0091f619335e4886a9bc74` **passed both required Phase 3 and full historical CI suites**.
- DEC-1055/#1276 exact SHA `945fc550f1936c5fb82813c9c3fb39f8472e880e` had Phase 3 success and historical in progress at preparation. DEC-1056/#1277 exact SHA `c35ef87c1a9ae89d48b939684df36c90dba94f83` had both suites in progress. This documentation-only child must also earn its **own exact-head Phase 3 AND full historical regression**. Pending is not passed.
- Original failed exact historical commits #1201–#1205, #1212, #1237 and #1261–#1267 remain FAILED, regardless of successful repair or descendants. Qualified independent security review is a separate requirement.

Every PR is **DRAFT / NEVER MERGE / NEVER PROMOTE**. Protected independent OS-enforced no-write DEC-650/#820 and immutable exclusive annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected annual evidence/sources, run385 execution/test/retry/rerun/dispatch, production refs/workflows/runners/rulesets/permissions changes, broker/trading, merge, promotion or authorization.
