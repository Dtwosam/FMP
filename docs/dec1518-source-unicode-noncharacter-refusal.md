# DEC-1518 — Refuse Unicode noncharacters in portable source labels

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent one-commit tests/docs child of #1763 at `1149cadd99dbe4510751e5e9c247f82f021f7713`. Ten additional synthetic methods, **2,420 proposed source-defined methods**.

The portable source-label guard already rejects Unicode control/format characters and variation selectors, but still permits noncharacter code points such as U+FDD0–U+FDEF and the final two scalar values in each Unicode plane (U+FFFE, U+FFFF, U+1FFFE and U+10FFFF). Unicode reserves these code points for internal use; accepting them in source inventory names can undermine portability or make evidence strings hard to review across systems. Refuse them by scalar range/mask only in lexical source-path validation, before decode or comparison, without opening any repository file.

Ten synthetic tests cover BMP and supplementary-plane noncharacters, both source-byte maps, sanitized stdin diagnostics, and ordinary Unicode/positive source-consistency-only behavior. No GitHub provider authenticity, witnessed original OS isolation, protected annual run permission or workflow dispatch authority is established.

Own head-associated Phase 3/full historical-general CI and qualified independent review required. DEC-650/#820 original OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual execution/retry, original/archive/artifact access, installed workflow/security changes, merges, deployment or trading.
