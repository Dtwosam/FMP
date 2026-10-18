# DEC-1609 — Commit root pointer, flat Git tree root and full tree snapshots must agree

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1855 at `106d6f9b62a92e8605a89a25c0b4298c56ebab44`. Fifteen synthetic methods (**3,330 proposed source-defined tests**).

A perfectly canonical changed-source Base64 map and valid flat Git leaf nodes do not rescue a contradictory root. Test missing, false/null/list/empty, underlength and overlength commit tree SHA pointers, syntactically valid but incorrect commit root SHAs, and mismatched or falsely truncated independent flat-tree root records. Require the reviewed `TREE_CHAIN_ROOT_SHA_UNREVIEWED`, `TREE_CHAIN_TREE_OBJECT_UNREVIEWED`, or `COMMIT_TREE_ROOT_UNREVIEWED` code across direct-memory, JSON and bounded stdin. Keep the full Git tree snapshots and exact source bytes unchanged. A clean control remains source-consistent only, with all protected fields false.

Synthetic caller-supplied review is not independently authenticated GitHub object or protected original OS evidence. Own exact-head Phase 3/historical general CI and qualified independent review required. Tests/docs only; no production/parser/resources/workflow/security/admission changes, protected originals/archives/artifacts, annual execution/retry, merge, deployment or trading. DEC-650/#820 and DEC-651/#821/#779 remain **BLOCKED**.
