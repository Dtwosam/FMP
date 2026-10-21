# DEC-1998 — Audit engine-compatible bounded decision metadata

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2246 at `d5faac0914a283993cdb0441a957ba305c192053`.

The Phase3 BacktestConfig freezes `decision_config` as a canonical JSON-like object, rejects all control characters in keys and string values, limits metadata nesting to 32 levels, consumes at most 8192 nodes and limits serialized JSON to 65536 bytes. A self-rehashed artifact can otherwise claim impossible decision metadata while passing manifest and generic audit consistency checks.

If run_identity.decision_config is supplied, require an ordinary JSON object, recurse with the engine's node/depth/printability constraints, use the original deterministic compact ASCII-escaped JSON representation to check the 64 KiB bound, and retain 512-bit integer and finite-float limits. Synthetic evidence that omits this optional identity field remains allowed. Five source-defined synthetic tests verify normal metadata, forged newline, empty nested key, deep nesting and oversized text after independent digest verification.

**7,094 cumulative proposed source-defined test methods** (+5). Exact-head Phase3 and historical/general CI mandatory. #2238–#2243 and #2246 have passed both workflows; #2244–#2245 full CI pending at this record; all past failed runs remain failed.

No workflow/ref/runner setting changes, protected research, demo/live brokerage or capital. Phase8A issues #779/#820/#821 and eight independent proof packages remain BLOCKED. **DRAFT NEVER MERGE NEVER PROMOTE.**
