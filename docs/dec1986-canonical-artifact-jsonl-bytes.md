# DEC-1986 — Audit canonical serialized JSONL row bytes

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2234 `6889646423b188c7ad669316dfdb34f5bf885b92`.

The Phase3 writer publishes sorted-key compact UTF-8 JSONL records, one per line terminated with a single LF. The opt-in audit previously validated decoded canonical fields and values but accepted a rehashed record with altered key order, whitespace or a missing final newline. The ordinary digest-only verifier still accepts any byte-for-byte manifest-consistent payload.

After parsing and bounded JSON tree validation, reserialize each trade/rejection record with precisely the writer's stable `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False)` algorithm plus LF. Refuse bytes differing from this canonical representation while preserving writer output. Three source-defined tests cover writer-compatible rows, a rehashed missing newline and a pretty-printed rejection row with a matching forged manifest.

Proposed source-defined methods **7,056** (+3). Own exact-head Phase3 and historical/general regression required before green claim; #2225–#2230 full CI PASS and #2231–#2233 full CI FAIL remain recorded exactly. #2234 full suite pending at documentation time.

No protected research/trading. Phase8A issues #779/#820/#821 plus eight independent external proofs remain unresolved. **DRAFT NEVER MERGE NEVER PROMOTE.**
