# DEC-2009 — Reconcile source built-in commission and financing economics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2257 at `a7d0e107d2f6f59e42ae2ff41982ff2c2e068ff1`.

Phase3's source run identity declares commission and financing model configurations. Prior audit checks those model config shapes but does not compare the stored per-trade commission and financing amounts to their **declared built-in model**. An artifact could be rehashed to claim zero broker costs while recording commission, or falsely attribute an arbitrary commission to a fixed-rate model, without violating net PnL arithmetic.

For exact installed source-engine reports with a known built-in cost model, check per-trade zero_commission => commission 0, fixed_per_million_per_side => commission 2*(abs(units)/1e6*rate) (source entry and exit commission call), zero_financing => financing 0. Preserve custom model flexibility and any synthetic identity without engine version. Source cost calculations are not independently authenticated broker costs.

Four synthetic source-defined tests cover versioned zero costs, a forged+rehashed cost swap preserving net PnL, a source-compatible fixed-per-million model, and falsely rehashed zero financing against an existing credit. Cumulative **7,127 proposed source-defined tests** (+4). Exact-head Phase3/full historical-general suite mandatory. Old failures remain failures; #2253–#2257 runs must be verified on exact commit.

Phase8A issues #779/#820/#821 and eight external independently supplied security proofs remain blocked; no protected annual research, installed workflows/refs/runners, brokers/orders, strategy promotion, real capital, or merges.
