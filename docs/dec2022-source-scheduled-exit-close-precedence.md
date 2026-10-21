# DEC-2022 — Exact scheduled-close precedence over stop/target exit

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2270 at `130b1b4a08dd53fa4d5eeceabb3845168999df78`.

The installed Phase3 engine processes existing positions at each supplied quote timestamp before new entries. If a position has a declared scheduled exit at that timestamp, `close_time_exit` is called and the branch `continue` skips `evaluate_exit`. The source's `_scheduled_exit_map` requires its planned close strictly later than earliest entry, so a record that closes **at its own scheduled timestamp** must have `ExitReason.TIME_EXIT`, regardless of whether stop/target would also have been reachable on that bar. A stop/target record can instead close before its scheduled time, and a scheduled timestamp without a quote bar does not establish that a time exit should have happened.

For exact installed-source reports, if `scheduled_exits[decision_id]` matches the trade's symbol and actual exit timestamp, require `exit_reason == TIME_EXIT`. Retain DEC-2015's converse check (`TIME_EXIT` requires an exact scheduled witness). Synthetic other-engine reports stay flexible. No external bar provenance, stop/target reachability or authentic order execution is asserted.

Four new source-defined tests check valid time exit or earlier target, rehashed TARGET with newly coincident schedule, rehashed ambiguous STOP with newly coincident schedule, and generic synthetic compatibility. **7,175 cumulative proposed methods** (+4). Own exact-head Phase3 and full historical/general suite mandatory. #2266–#2269 remain historical full-suite FAIL; #2270 full gate is separately pending.

Phase8A #779/#820/#821 and eight independent external security proof packages remain unresolved. No protected annual research, workflow/ref/runner mutation, strategy promotion, merges, broker orders or capital.
