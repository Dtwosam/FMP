# DEC-1494 — Cross-platform source path ambiguity and Unicode-normalization guard

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict forward-only one-commit tests/docs child of #1739 at `6a28f987a45c65a4c8d751897cea48c8523e995b`. Adds **12 synthetic unittest methods**; **2,188 proposed source-defined test methods**.

The offline CI source reviewer compares caller-supplied repository source-path labels. A label may be valid on POSIX yet collide or be unsafe on other filesystems: decomposed Unicode (NFD versus NFC), Windows device names (CON, PRN, AUX, NUL, COM1–9, LPT1–9, with suffixes), colon/drive-relative spellings, path components ending in space or dot, and invisible bidirectional override/isolate characters. To keep evidence labels unambiguous, extend only the existing source-map label validator; do not dereference paths, inspect the local filesystem or normalize and silently rewrite a value.

Twelve synthetic regression tests cover each rejected ambiguity, accepted composed Unicode and ordinary words, source-map rejection before binary decoding, non-disclosing stdin output and a clean positive fixture. All annual execution, independent OS proof, and exclusive dispatch authority flags stay false.

Own exact-commit head-associated Phase 3 and full historical/general CI with qualified independent review required. DEC-650/#820 protected-original OS no-write and DEC-651/#821/#779 immutable exclusive one-shot protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No annual dispatch/retry, protected originals/archive/artifacts, installed workflow/security modifications, merges, deployments or trading.
