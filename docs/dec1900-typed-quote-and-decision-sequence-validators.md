# DEC-1900 — Typed Phase3 quote-bar and decision collection validators

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent source-only child of #2148 `efb45eab9bfbdc7635a2ec2f126b025878646ff4`.

The Phase3 collection validators previously accessed `.timestamp_utc` or `.decision_id` of each item without checking that the input was actually a sequence of canonical QuoteBar/Decision records. An unexpected `None`, dictionary or text item could leak an AttributeError, and a noniterable could throw TypeError rather than rejecting unsupported source data with a clear ValueError. Add an early fail-closed type boundary for ordinary Sequence inputs (excluding strings/bytes) and exact canonical dataclass instances; keep existing duplicate quote identities, timestamp/symbol ordering and duplicate decision IDs unchanged.

Three new source-defined tests (**6,871 proposed cumulative**) exercise malformed collections, malformed members and valid duplicate detection. This is local synthetic data consistency, not an installed security gate, authenticated market source, strategy selection or trading authorization. No protected 2023/run385/attempt1, broker/demo/live/capital, or GitHub ref/workflow/ruleset/runner modification.

#779/#820/#821 and all eight independently acquired administrator/OS/provenance/fresh inventory/human proof packages remain MISSING/BLOCKED. All branches DRAFT/NEVER MERGE/NEVER PROMOTE, exact-head Phase3/full CI and qualified independent review required.
