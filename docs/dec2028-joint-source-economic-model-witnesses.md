# DEC-2028 — Integrated source economic-model witness matrix

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2276 at `a8f1b6c81ee0a3836966a23180cb56899e9c58ec`.

DEC-2011, DEC-2006/2027, DEC-2007/2026, and DEC-2009/2025 validate distinct source-engine economic claims: published execution prices from declared pips, reference-price gross PnL, implied adverse slippage cost, and built-in fixed per-million commission. Individual synthetic fixtures were valid but generally exercised these restrictions in isolation. This test/docs-only draft creates one internally consistent installed-source-engine report that declares 1.5 pip adverse slippage, 25 USD per million per side, zero financing, matching source PnL, risk equity and checkpoint values.

Four source-defined methods: acceptance of the fully combined model; checksum-verified rehashed 1e-9 gross drift; checksum-verified rehashed 1e-9 slippage drift; and checksum-verified rehashed 1e-9 fixed commission drift. Each tamper passes manifest hash verification and the broad net arithmetic tolerance, but must fail its specific exact source-model reconstruction check. No source production changes.

**7,198 cumulative proposed source-defined test methods** (+4). Own exact-head Phase3 and full historical/general CI mandatory; historical failed #2266–#2269 runs remain failures, and newer drafts require their own full validations. Internal model consistency is not proof of authentic FX quotes, broker fee billing, actual fills or profitability.

Phase8A #779/#820/#821 plus eight independent external security proof packages remain blocked. No protected annual research, workflow/ref/runner changes, strategy promotion, mergers, brokers/orders or real capital.
