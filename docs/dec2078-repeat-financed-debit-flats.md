# DEC-2078 — Repeated financed debit-neutral closes preserve net outcomes

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2326 at `6287796c16d708042e600b0da14d78665143aae7`.

Three source-defined trades share one UTC exit instant and use the same permitted custom-financing debit to precisely offset their positive execution gross PnL. Realization IDs Z-FLAT, A-FLAT, M-FLAT publish canonically as A-FLAT, M-FLAT, Z-FLAT. Three repeated zero-change checkpoints preserve the exact close count and prove that realized equity never moved despite **three positive pre-cost gross trade fields**.

Five test methods cover this valid deterministic report and four digest-valid falsifications: forged winning rate, performance gross profit, three-trade winning streak, and numeric profit factor. The independent read-only audit must classify realized **net** outcomes, not gross execution fields. Trade count and win-rate denominator remain three; all three closes are neutral. No production changes, no source of trading authority.

**7,397 cumulative proposed test methods** (+5); own exact-head Phase3 and full historical/general suite required. Pending results do not imply passes, and old failed runs remain failed. Phase8A #779/#820/#821 and eight independent security proofs remain BLOCKED. No protected research, installed workflow/ref/runner changes, merging, strategy promotion, broker orders or real capital.
