# DEC-2048 — Single-sided source performance-null boundary witnesses

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2296 at `faec945887aee3b8f3c197da3861efecc74b1800`.

The installed metrics writer distinguishes *undefined* aggregates from actual zero values. A single profitable source-engine trade has a valid 100% win rate and one winning streak, but has neither an average loss nor a meaningful profit factor (no losing denominator). A single source-engine losing trade has a valid zero win rate, zero profit and profit factor, a mean loss and one losing streak, but no mean win. The optional audit already reconstructs these semantics from canonical trade rows.

Four source-defined test methods exercise valid all-win and all-loss source reports, plus canonically self-rehashed false zero profit factor on a win-only run, false zero average loss on a win-only run, and false zero average win on a loss-only run. The evidence verifier must accept the manipulated manifest digest; the opt-in semantic audit must reject each forged interpretation. This test/docs-only change preserves the writer's strict pre-I/O checks and generic reporting behavior.

**7,264 cumulative proposed source-defined methods** (+4). Own exact-head Phase3 and full historical/general CI required; historical failed runs stay failed and no pending run counts as passed. No protected annual research, runner/ref/workflow changes, strategy promotion, merges, orders, brokers or real capital. Phase8A #779/#820/#821 and eight independent security proof packages remain outstanding.
