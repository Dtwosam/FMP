# DEC-986 — Following a directory symlink keeps the target watch after alias deletion

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit Linux regression/documentation child of DEC-985/#1206.

This companion to the inherited DEC-980 assertion repair compares three **real** inotify instances on generated public `/tmp` files: an original source+parent witness, a second watch that **follows** a temporary symlink to the parent directory (`IN_CREATE | IN_DELETE | IN_ONLYDIR`), and a third watch on the **symlink inode itself** (`IN_DELETE_SELF | IN_DONT_FOLLOW`).

Real unlink of the symlink emits named `IN_DELETE` on both parent-inode instances. The no-follow symlink watch reports `IN_DELETE_SELF` and `IN_IGNORED` instead. After the pathname is absent, creating and deleting another disposable sibling still generates real named create/delete records on the **surviving followed-parent watch**, while the invalidated no-follow watch stays quiet. That is kernel watch identity, not a mocked receipt or independent no-write control.

Later distinct-byte sample writes and restoration still generate native source/parent evidence on the separate original dual watch; its unchanged evaluator must be `BLOCKED`, `can_authorize_dispatch=false`, `independent_os_proof_verified=false` exactly. Final public source+parent device/inode/mode and one-name inventory match, and all three native FDs close. The new Linux method brings this strict draft stack to **644 source-defined methods**.

DEC-985's preceding failed ancestors (#1201–#1205) remain **failed at their exact commits**; this child and DEC-985 need independently successful Phase 3 and full historical CI and qualified independent security review. Protected OS no-write DEC-650/#820 and exclusive immutable annual run385 admission DEC-651/#821/#779 stay **BLOCKED**. No protected data, annual test/dispatch/retry/rerun, production refs/workflows/runners/rulesets/permissions, broker/trading, merge or promotion.