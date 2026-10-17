# DEC-1476 — Second observed full CI source golden sample from recovered #1698

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child #1699 DEC-1475 at `2e7dcbab2aeb62ae5c66d7bf96bbcfef2c777045`. 12 new offline test methods; **1,998 proposed source-defined methods**.

## Independently inspected unprotected source records

Read-only GitHub REST job logs and Git commit objects for the corrected and fully dual-CI-successful draft **#1698**:
- Historical/general `tests` run **39030113645**, job **117388707144**, completed/success;
- Phase3 acceptance run **39030113556**, job **117388706485**, completed/success;
- The two actual checkout traces independently fetched temporary PR merge SHA `0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9` and checked out `refs/remotes/pull/1698/merge`;
- Immutable SHA Git objects: merge parents base `4d4fbbae069254fdc4da549daaa799ba3ec09f6d` and head `fa1cabab52e547b5f0a6f4cf39749df818529b59`, with **identical Git source tree SHA** `21b9e451c6e255c0dfb73910995670b11f240bf3` to the draft head;
- Phase3 logged its five-scenario acceptance index with `code_commit` equal to that *merge SHA*, and finalized/uploaded `phase3-backtester-acceptance-0cf9a4b788da6f9f3b4f4cdaeca90125742d8dc9` under artifact ID **12100346157**, size 23,491 bytes. No artifact was downloaded.

A second, differently dated and independently successful run-pair exercises the already source-tested checkout/acceptance parsers alongside original #1674 golden fixtures. The new tests embed only the observed three checkout lines for each workflow and five Phase3 index/upload lines. They reject divergent fetched SHA, wrong Git commit parent/tree, incorrect run attempt, a mismatched artifact URL and duplicate manifest-key tampering. The static sample itself is **not** an authenticated runner log provider, an OS confinement witness, proof of artifact bytes, or permission to run protected historical research.

This draft and every child require their own independent head-associated PR merge-source-tree Phase3 and full historical/general CI plus qualified review. The real protected annual prerequisites remain **BLOCKED**: DEC-650/#820 OS original no-write, DEC-651/#821/#779 immutable exclusive server-enforced one-shot GitHub admission for **2023 run385/attempt1**. No protected annual dispatch/retry, originals/archives/artifacts download, installed workflow/security changes, merging, deployment or trading.
