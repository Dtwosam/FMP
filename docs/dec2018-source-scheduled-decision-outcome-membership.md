# DEC-2018 — Scheduled source decision membership in outcome evidence

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2266 at `f339db31dea395f3e9538e2372b0bc70eff0acb4`.

The Phase3 source's `_scheduled_exit_map` accepts scheduled exits only for known *directional* input decisions. `run_backtest` later records one outcome per directional decision: either a `RejectionRecord` or a filled position with a `TradeRecord`, which is closed by target, stop, scheduled time or end of data. The artifact auditor already requires source TIME_EXIT close records to match a scheduled descriptor, but a rehashed manifest can introduce additional scheduled descriptors referring to non-existent or wrong-symbol decisions.

For the installed source-engine version only, build a decision-to-symbol index of validated trade and rejection evidence. Every canonical `scheduled_exits` descriptor must reference a decision ID present in that index with the same symbol. A matching scheduled decision may still end as a rejection or exit earlier via stop/target, so this rule does not require a TIME_EXIT outcome. Generic envelopes remain unaffected.

Four source-defined tests: positive source scheduled decision rejected before entry, rehashed orphan scheduled descriptor, rehashed wrong-symbol scheduled rejection descriptor, and generic synthetic orphan compatibility. **7,160 cumulative proposed source-defined methods** (+4). No external quote evidence or broker execution is implied. Exact-head Phase3 and full historical/general regression suites must pass independently; older failed runs remain failed.

Phase8A #779/#820/#821 plus eight independent external security proof packages remain outstanding. No protected annual research, installed workflow/ref/runner changes, merges, strategy promotion, broker orders or real capital.
