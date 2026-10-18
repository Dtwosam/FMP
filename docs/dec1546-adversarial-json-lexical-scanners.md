# DEC-1546 — Adversarial lexical JSON scanner regression matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1792 at `2b7fc4d7e64b3c3d9d2cd0ccfcac4d248773b9d7`. Ten new synthetic unittest methods; **2,682 proposed source-defined tests**.

DEC-1542/1543 added independent predecoder lexical ceilings on JSON array and object member counts. These scanners must not treat punctuation inside quoted values or keys—including escaped quotes and backslashes—as structural syntax, while still refusing malformed closers and deferring duplicate decoded JSON keys to the postdecoder object-pairs hook. Add a focused all-synthetic regression matrix for these invariants, with no new parsing behavior or modified authorization surfaces.

Ten tests cover lengthy comma/bracket-like JSON string data and keys, escaped punctuation, many small empty containers, nested valid mixed structures, crossed/malformed closers, escaped Unicode duplicate keys, and stable source-consistency-only verdicts across key insertion/sorting. These tests never open protected originals, authenticate provider data, or grant annual run permission.

Own exact-head Phase 3/full historical-general CI with independent qualified review required. DEC-650/#820 independently witnessed protected-original OS no-write and DEC-651/#821/#779 immutable exclusive one-shot protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archives/artifacts, workflow/security changes, merges, deployment or trading.
