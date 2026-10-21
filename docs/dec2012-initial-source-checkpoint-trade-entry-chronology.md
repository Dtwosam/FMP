# DEC-2012 — Source initial equity checkpoint versus trade entry chronology

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2260 at `1302c84cf311ad85b9db5e95d6a467aed1ee448a`.

The source Phase3 engine creates its first `EquityCheckpoint` at `bars[0].timestamp_utc` when it initializes `RiskState`, before any `fill_entry` can occur. The artifact auditor already checks checkpoint chronological ordering, starting-equity parity and each realized trade's close checkpoint; it did not independently reject an initial checkpoint timestamp *after* a recorded trade's entry but still before that trade's exit.

For an artifact declaring the exact installed source-engine version and starting equity, retain the earliest validated trade-entry timestamp and require the initial checkpoint timestamp to be no later than that entry. This is a source-defined relative ordering condition; it does not authenticate the underlying quote bars or infer the first-bar timestamp. Zero-trade and generic/synthetic reports remain unchanged.

Three new source-defined test methods cover a source-compatible initial checkpoint before the first entry, a self-rehashed initial checkpoint moved 30 seconds after entry that passes digest verification but fails the semantic audit, and generic synthetic checkpoint timing flexibility.

**7,136 cumulative proposed source-defined test methods** (+3). Own exact-head Phase3 acceptance and full historical/general CI required; older failed runs remain failed. No externally certified execution, quote provenance, profit or broker claim.

Phase8A #779/#820/#821 and eight independent security proof packages remain unresolved. No protected annual research, installed workflow/ref/runner change, broker order, real capital, strategy promotion or merge.
