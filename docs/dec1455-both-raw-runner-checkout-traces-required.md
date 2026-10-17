# DEC-1455 — Require original supplied checkout log text for BOTH CI workflows

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1678 DEC-1454 at c150342c50bc81ba7eb1fc5b3d88ce6b2f77c25c. Eight new source-defined methods, **1,821 proposed methods**.

DEC-1454 supplies a narrow offline parser for the three reviewed GitHub Actions runner stages: immutable full fetched PR merge SHA, actual checkout of that PR merge ref, and short checked-out HEAD message containing the draft head/base parent identities. Before this child, DEC-1451/1452 combined review accepted caller-extracted field dictionaries without reconciling them with raw log text.

The composite now requires a separately provided raw runner-log string **for each** exact GitHub Actions workflow run ID. It parses both original checkout traces through DEC-1454, rejects duplicate/missing/reordered/wrong-ref evidence, and requires the SHA, prefix and checkout ref from each log to equal the already cross-validated run-specific CI metadata. Eight synthetic regression tests exercise missing logs, changed SHA or ref, reordered stages, and a forged field dictionary inconsistent with unchanged raw logs. A consistent composite result remains only a shape check on untrusted caller-supplied bytes; live runner log retrieval/authentication is independent.

Own head-associated PR merge-source-tree Phase3 and full historical/general CI plus qualified external review required. DEC-650/#820 actual protected original OS no-write and DEC-651/#821/#779 exclusive immutable one-shot 2023 run385/attempt1 server admission remain **BLOCKED**. No protected original/annual archive read, dispatch/retry, installed annual workflow, GitHub security settings, merge, deployment, or trading.
