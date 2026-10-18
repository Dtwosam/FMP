# DEC-1536 — Plain-key inventory gate on nested source-review verdicts

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Strict exact-parent one-commit tests/docs child of #1781 at `55deb887cc4d7366f71617ae036e8caea145a2f2`. Nine additional synthetic tests: **2,589 proposed source-defined methods**.

The source-review envelope already requires exact plain-string top-level evidence dictionary keys before comparing the inventory. However, the **returned** nested reviewer verdict was checked using `set(verdict)` before confirming that all dictionary keys were exact plain strings, potentially invoking arbitrary custom-key hashing or equality methods in an untrusted mocked return value. Validate every nested verdict key's exact type before materializing its key set; refuse unknown keys or subclasses with the existing safe `BUNDLE_RESULT_SHAPE_UNREVIEWED` code. No key, custom-object representation or input evidence is echoed. Keep existing exact verdict inventory, boolean authority guards, diagnostics allowlist and consistency rules unchanged.

Nine tests cover integer/None/subclassed/custom keys, no rehash or rendering, unexpected ordinary keys, dict subclass precedence, known source-only diagnostic acceptance and clean nonauthorizing success. These are local result-shape tests, not provider-origin attestation, original OS proof or annual admission.

Own exact-head Phase 3/full historical/general CI and independent qualified review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 server admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archives/artifacts, installed workflow/security changes, merges, deployment or trading.
