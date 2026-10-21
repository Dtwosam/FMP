# DEC-1980 — Canonical value domains for stored Phase3 trades

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2228 at `3b43da78450789dfd4498bf9e0ea1c5e46a91612`.

Although the separate read-only audit checks each stored TradeRecord's exact JSON field names, PnL, risk equity, timing and ids, a fully rehashed adversarial artifact could change a trade's symbol, direction, size, exit_reason, price or ambiguity flag to an impossible value without invalidating those checks.

Recheck stored trade symbol membership in the source-defined FX symbol set, LONG/SHORT direction, exact positive 64-bit units, ExitReason enum value, Boolean ambiguity and finite strictly positive entry/exit/reference/stop/optional target prices. The canonical writer already checks these domains; preserve optional null target price.

Four synthetic methods cover an unsupported symbol/direction, Boolean or zero size, nonpositive/Boolean price, and invalid exit reason/ambiguity, each rehashed to pass the low-level SHA256 verifier while failing the opt-in audit.

**7,040 cumulative proposed source-defined test methods** (+4). Independent exact-head Phase3/full historical/general CI and review remain required. Historical full-suite failures #2221–#2224 remain failures. Phase8A #779/#820/#821 eight independent security proofs missing. No protected 2023/run385/attempt1, research, Strategy V1, installed runner/ref/workflow mutations, broker or capital promotion.
