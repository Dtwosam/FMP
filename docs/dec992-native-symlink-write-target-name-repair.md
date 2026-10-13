# DEC-992 — Repair native symlink write-event basename assertion

**DRAFT / NEVER MERGE / NEVER PROMOTE.** This is a strict one-commit tests-and-documentation child of DEC-991/#1212, preserving the original #1212 exact SHA rather than rewriting it.

On genuine Linux inotify, an ordinary file write through a symlink resolves to the target dentry. With the sample and containing directory both watched, a native write via a generated symlink `public-symlink-alias` emits the source `IN_MODIFY` and a **parent named `IN_MODIFY` for `sample`**, not for `public-symlink-alias`. A separate standalone disposable native reproduction confirmed the actual mask and target basename.

The initial DEC-991/#1212 test incorrectly expected the alias basename for this write. DEC-992 changes **only that assertion and clarifying comments** in `tests/test_dec991_native_symlink_create_only_inode.py`, corrects the associated DEC-991 Markdown explanation, and adds this repair ledger. It does **not** discard the kernel event, weaken the parser, modify observer runtime or change protected state.

The rest of DEC-991's original native case remains: default create-only symlink following returns `EEXIST` on an already watched target inode, separate create-only `IN_DONT_FOLLOW` succeeds on the link inode, unlinking the alias emits parent `IN_DELETE` and link `IN_DELETE_SELF`/`IN_IGNORED`, extra unknown WD records fail closed, and the original source watch still observes a real restore. The unchanged evaluator must stay `BLOCKED`, with `can_authorize_dispatch=false` and `independent_os_proof_verified=false` exactly.

Source-defined count stays **647**. The original #1212 exact head `0bcc31e4168cb34136512f56c8a0625c9d9cc7f7` remains in the lineage with its own immutable CI verdict, whether pending or failed; this new child requires **both** successful exact-head Phase 3 acceptance and complete historical regression, plus independent qualified security review. Earlier historical failures #1201–#1205 remain failed regardless of any descendant success.

Protected independently OS-enforced no-write DEC-650/#820 and exclusive immutable annual run385 admission DEC-651/#821/#779 remain **BLOCKED**. No protected evidence/sources, annual run/test/retry/dispatch/rerun, production refs/workflows/runners/rulesets/permissions, broker/trading operations, merge or promotion.