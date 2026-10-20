# DEC-1806 — Independently re-derive historical workflow observations before JSON handoff

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of #2052 `a63a96d60f15bb719b89878abb5e6acc04b15b4b`.

DEC-1803 established exact nested pre-gate row types, field shape and indices; DEC-1805 pinned source fingerprints before JSON. A syntactically correct but altered command payload, job metadata, or matrix inventory from a drifted upstream producer could still be passed through by the JSON compiler despite the Markdown renderer re-deriving part of that data.

The compiler now performs an independent second **offline** read of the same historical fixture using the no-follow reader, verifies its pinned SHA-256 again, and compares every `observed_jobs`, `historical_matrix_inventory`, and `historical_pregate_payloads` value with fresh results from the original source-only extractors. Any altered string, extra metadata, changed matrix fact or command payload is rejected as `InvalidHandoff` before **either** output. This is not real runner observation or installed workflow attestation; a second read is for internal reporting consistency only.

Four adversarial methods (6,616 cumulative proposed source-defined) test plausible command substitution, extra matrix approval, extra job metadata and both invalid CLI formats returning 2 without stdout. Valid reports continue exit 3, explicitly BLOCKED. Does not alter actual workflows, GitHub protections, protected annual 2023/run385 attempt1, brokers, orders, demos, live capital or profitability. #779/#820/#821 and all eight independent external proof packages remain MISSING/BLOCKED. Exact-head Phase3/full regression CI and independent review required.
