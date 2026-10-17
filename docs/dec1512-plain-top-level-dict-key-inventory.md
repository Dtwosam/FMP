# DEC-1512 — Plain top-level evidence keys before set comparison

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit forward-only tests/docs child #1757 at exact parent `47956a598e102ef881ff22a0918d431dbb7f7f57`. Nine new synthetic regression tests: **2,362 proposed source-defined methods**.

The direct-memory evidence entry point required a native dictionary but immediately built `set(envelope)` to compare top-level keys against the mandatory schema. A dictionary may contain custom Python key objects whose `__hash__` or `__eq__` methods perform unreviewed operations if the inventory comparison touches them. Reject any top-level key whose exact type is not plain `str` before building a set or using any untrusted key as a lookup; return only the existing safe `BUNDLE_KEY_INVENTORY_UNREVIEWED` verdict. The already-enforced full key inventory check, schema/category contracts, nested graph type guard and all false protected-annual authorization flags remain.

Nine synthetic tests cover integer, None, subclassed string, and custom key objects with sensitive/exceptional methods; no hashing or rendering of unexpected keys, missing/extra validly typed keys, dictionary-subclass precedence and clean consistency-only evidence. This is a local trust boundary, not original OS file protection, GitHub provider authentication or authorization of protected annual execution.

Own exact-head Phase 3 and full historical/general CI plus qualified independent review required. DEC-650/#820 independently witnessed original protected OS no-write and DEC-651/#821/#779 exclusive immutable protected 2023 run385/attempt1 GitHub admission remain **BLOCKED**. No protected annual dispatch/retry, originals/archive/artifacts, installed workflow/security modifications, merges, deployment or trading.
