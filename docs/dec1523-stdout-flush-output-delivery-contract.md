# DEC-1523 — Check stdout flush before offline verdict success

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent, one-commit tests/docs child of #1768 at `62ea2e0fb89c849b40b1d8bf04cd0bf7b5fca00c`. Nine new synthetic methods; **2,469 proposed source-defined methods**.

DEC-1501 required `write()` to report the full length of a serialized, fail-closed CI/source verdict before reporting local consistency success. A buffered standard text stream may accept the write, however, then fail during `flush()`. When the supplied stream exposes a standard callable `flush` method, invoke it after complete write and refuse any exception. A noncallable exposed `flush` attribute is also refused. Streams without a flush method retain the prior direct unbuffered-write contract; this change cannot guarantee durability or delivery to downstream readers beyond what the output stream reports. No retry or secondary write is attempted on failure.

Nine tests cover full flush once, broken pipe/runtime/assertion exceptions, noncallable/no-method cases, no flush after partial write, invalid JSON and clean synthetic consistency-only verdicts. Annual authorization stays false even when exit status is zero.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 original protected OS no-write and DEC-651/#821/#779 immutable exclusive protected 2023 run385/attempt1 GitHub server admission remain **BLOCKED**. No protected annual dispatch/retry, originals/artifacts, installed workflows/security modifications, merges, deployment or trading.
