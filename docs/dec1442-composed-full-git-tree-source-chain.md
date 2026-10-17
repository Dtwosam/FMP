# DEC-1442 — Mandatory full changed-file Git tree chain in combined review

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit source-only tests/docs child #1665 DEC-1441 at f2459aaecc9c9641fae04c7263f3549e51ff20bc. Adds eight unittest methods, **1,676 proposed source-defined methods**.

DEC-1440 previously composed exact-head PR/CI evidence, CI job steps, Git compare counts, flat changed-file modes, byte-matched blobs and CI workflow file identity. DEC-1441 demonstrated that independently supplied flat path-node metadata does not prove that the changed blob actually belongs to the alleged commit root tree.

The composite now **requires full caller-supplied Git tree objects**, bound by exact parent-child SHA pointers to every changed source blob, with regular tree/file modes, no missing/duplicate/truncated entries and byte-matched Git blob identities. Eight new synthetic tests ensure a wrong or missing child SHA, incomplete snapshot, altered blob, symlink, or duplicate entry blocks the entire composite even if the other reviewers still pass. When every synthetic source check passes, original OS security proof and immutable annual server admission flags still remain explicitly false.

All of this remains in-memory review-shape logic; the caller must independently authenticate exact GitHub tree objects and Git source. Its own exact-head Phase3/full historical CI and external qualified review are mandatory. DEC-650/#820 actual OS protected-original no-write and DEC-651/#821/#779 immutable exclusive 2023 run385/attempt1 server admission are still **BLOCKED**. No protected data, annual dispatch/retry, installed security/workflow change, merge, promotion or trading.
