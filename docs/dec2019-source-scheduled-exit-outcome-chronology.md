# DEC-2019 — Source scheduled exit chronology relative to its decision outcome

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2267 at `f0075337f9e93387915e8af0c4e74c4813ceb038`.

The installed `_scheduled_exit_map` requires each scheduled close to occur strictly after a directional decision's earliest executable timestamp. That executable timestamp is later than the input decision timestamp and, for a filled decision, becomes the trade's entry timestamp. Therefore a valid scheduled source exit must occur strictly later than the corresponding trade entry or, for a rejected directional decision, strictly later than the rejected decision's timestamp. An earlier STOP/TARGET may close before the schedule without violating the contract.

Build upon DEC-2018's validated source outcome membership index. For each source-version scheduled descriptor, compare the scheduled UTC instant against its published outcome's entry (trade) or original decision (rejection) timestamp; reject equality or backwards ordering. Synthetic other-version reports retain their prior flexibility. This check does not infer bars, fill prices, rejected decision earliest times, or independent provenance.

Four new source-defined methods: valid early TARGET with later planned schedule; checksum-verified forged schedule at the filled trade entry; checksum-verified forged schedule at a rejection's decision time; and generic same-time metadata compatibility. **7,164 cumulative proposed source-defined methods** (+4). Exact-head Phase3 and historical/general suite required. Older failed checks remain failures.

Phase8A #779/#820/#821 plus eight independent external security proof packages remain unresolved. No protected annual research, installed workflow/ref/runner changes, brokerage/orders, strategy promotion, real capital or merges.
