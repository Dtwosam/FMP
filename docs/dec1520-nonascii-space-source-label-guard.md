# DEC-1520 — Reject ambiguous non-ASCII Unicode spaces in source paths

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict one-commit tests/docs child of #1765 at `51044377f65b7bf84323538a3f28faa1919212c2`. Eleven new synthetic unittest methods; **2,442 proposed source-defined methods**.

The source-path validator already forbids invisible format/control characters and Unicode separator categories Zl/Zp, but admits the Zs class of Unicode space separators, including nonbreaking, narrow no-break, thin, en and ideographic spaces. These glyphs can be hard to distinguish from ordinary ASCII spaces during manual inspection and in machine-readable source inventories. To preserve portable and unambiguous evidence path identity, forbid category Zs characters except U+0020 ASCII space, which remains allowed internally (but already rejected at the end of a path component). Keep all previous Unicode, segment, casefold and byte-length restrictions.

Eleven synthetic tests cover representative Unicode spaces, internal/trailing ASCII space controls, both source-byte maps, safe stdin output and an unchanged clean source-consistency-only fixture. This is only lexical review of supplied source labels, not provider authentication, protected original OS no-write or exclusive immutable protected annual admission.

Own exact-head Phase 3/full historical/general CI and qualified independent review required. DEC-650/#820 protected-original independently witnessed OS no-write and DEC-651/#821/#779 exclusive immutable 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archive/artifacts, installed workflow/security changes, merges, deployment or trading.
