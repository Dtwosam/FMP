# DEC-1435 — Strict draft changed-file Git tree mode/ancestry review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1658 DEC-1434 at 588a78181638bc48f1b0eb4a369ef67aac374d46. 16 new methods, **1,587 proposed source-defined methods**.

Canonical docs/ and tests/ changed paths alone do not establish the Git object type. In Git, 120000 is a symlink, 160000 is a gitlink/submodule, and 100755 is an executable. Read-only GitHub tree review of #1658 observed a 040000 tests directory at SHA 740d61e6c4dac48e3e602bf22824d342331fbe91 and ordinary 100644 blobs for changed tests. This sample is not a general future-PR proof.

This conservative no-network checker consumes independently supplied PR/compare/commit/root-tree and path-node snapshots, reuses the prior ancestry/path reviewer, and requires root tree identity, a nontruncated tree, regular 100644 changed leaves, and 040000 tree ancestors. Deleted files, missing nodes, executable/symlink/gitlink changes and malformed ancestry fail closed. Callers must obtain and authenticate complete exact-tree evidence separately. A synthetic result is neither a remotely attested Git object inventory nor operational approval.

Its own exact-head Phase3 and full historical/general CI plus qualified review are mandatory. Protected historical original OS no-write DEC-650/#820 and immutable exclusive server-side 2023 annual run385/attempt1 DEC-651/#821/#779 remain BLOCKED. No annual dispatch/retry, protected artifact access, installed workflow/security mutation, merge, deployment, broker or trading.
