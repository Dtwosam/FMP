# DEC-1444 — Enforce computed Git tree object IDs through source chain

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit source tests/docs child #1667 DEC-1443 at 9ac75c02073b7b91473c9f609eee3d75f8c705e1; six new methods, **1,700 proposed methods**.

DEC-1441 and its composite in DEC-1442 required parent-child tree SHA pointers but accepted a full tree JSON object even if its contents did not hash to its purported Git object identifier. DEC-1443 introduced a stand-alone canonical wire-object SHA utility. This forward correction makes the byte-recomputed tree object ID mandatory for every root/subtree encountered in the chain, rejecting missing, malformed, reordered or modified entries whose SHA is stale.

The two synthetic suites now build all fixture tree identities bottom-up from their true wire entries, rather than using arbitrary 40-character placeholder strings. Additional regression tests verify mismatched source listings and composite diagnostics for reordered entries and extra tree children. Source review does not independently authenticate the GitHub server, access protected originals, enforce OS permissions or authorize protected annual dispatch.

Its own exact-head Phase3/full historical CI and independent qualified review are mandatory. DEC-650/#820 real original no-write isolation and DEC-651/#821/#779 exclusive immutable one-shot run385/attempt1 server admission remain **BLOCKED**. No protected original/archive read, annual dispatch/retry, installed workflow/security changes, merge, deployment or trading.
