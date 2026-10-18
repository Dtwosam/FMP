# DEC-1548 — Deterministic lexical/decoder JSON consistency matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** One-commit tests/docs child of #1794 at `8f509ce8420f4b6eaca09edaf16d21cc5725de6c`. Eight all-synthetic test methods; **2,698 proposed source-defined methods**.

The predecoder object/array scanners must count structural punctuation only, even when standard `json.dumps` produces Unicode escapes, literal Unicode scalars, backslash-quote parity, newlines, indentation, compact separators or nested punctuation-dense strings. This static corpus checks agreement between both lexical scanners and the standard JSON decoder on small valid documents. Invalid nonstandard numerical constants and unterminated escaped strings must still fail closed with safe JSON diagnostics.

The clean synthetic CI/source fixture continues to prove *source consistency only*, not independent protected-original OS no-write, exclusive immutable server admission or permission to execute annual backtests. No parser limits, production code, workflow or authorization controls are changed.

Own exact-head Phase 3/full historical-general CI and independent qualified review required. DEC-650/#820 and DEC-651/#821/#779 gates remain **BLOCKED**. No protected execution/retry, originals/archive/artifact access, workflow/security-control change, merge, deployment or trading.
