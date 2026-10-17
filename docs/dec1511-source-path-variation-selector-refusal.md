# DEC-1511 — Variation-selector and grapheme-joiner source-path refusal

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict exact-parent one-commit tests/docs child of #1756 at `7e1021af2c02edf466b9047e29d498ab9b3c522c`. Ten additional synthetic regression methods; **2,353 proposed source-defined methods**.

Unicode general category checks for invisible source-label characters do not include every default-ignorable selector: the combining grapheme joiner U+034F, Mongolian free variation selectors U+180B–U+180D, and BMP/supplementary Unicode variation selectors U+FE00–U+FE0F and U+E0100–U+E01EF can be classified as combining marks instead of control/format characters. These characters can change glyph appearance without creating a visibly distinct source filename. Refuse them lexically as noncanonical source-map path labels in addition to DEC-1509's category checks, before Base64 decode or nested review. No on-disk normalization or filename access occurs.

Ten synthetic tests cover early/late variation selector ranges, combining grapheme joiner, plain Unicode positive controls, safe stdin refusal without echo, and a clean caller-supplied source-consistency-only fixture. No provider authentication, independently witnessed OS isolation or protected annual execution admission is implied.

Own exact-head Phase 3/full historical-general CI with independent qualified review required. DEC-650/#820 protected-original witnessed OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub admission remain **BLOCKED**. No protected annual dispatch/retry, original/archive/artifact access, installed workflow/security setting changes, merges, deployment or trading.
