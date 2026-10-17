# DEC-1521 — Repair inherited path-length boundary after UTF-8 component limits

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1766 at `09f884e8cff5fe807d78b98bb0c07cf1ffd82b5d`. Adds 9 synthetic methods; **2,451 proposed source-defined methods**.

At #1760 through #1766, Phase 3 passed while full historical/general CI failed inherited `test_exact_source_path_limit_is_lexically_permitted`. The original fixture used a single filename component of 4092 ASCII characters, valid under DEC-1495's whole-path character limit but correctly rejected by DEC-1514's stricter 255-byte per-component rule. This is an outdated positive test, not an implementation failure. Replace its positive case with **17 components of 240 bytes each and 16 separators (4096 total bytes)**. Replace its over-total test with the same valid-length components plus one extra byte, isolating the 4096-byte whole-path boundary without weakening either constraint.

Nine new synthetic methods cover exact/over total length, per-component caps, UTF-8 multibyte inflation, 4095-byte positive path, diagnostic precedence before nested review, no echo, and permanent false annual authorization. No protected annual execution, original OS isolation or provider authenticity follows from these tests.

Own exact-head Phase 3 and full historical/general CI plus qualified independent review mandatory. DEC-650/#820 independently witnessed original-file OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected run/retry, original/archive/artifact access, installed workflow/security change, merge, deployment or trading.
