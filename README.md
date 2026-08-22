# FMP — Forex Trading Engine V1

FMP is a forex-only systematic trading research and execution project.

The goal is not to build an impressive AI bot. The goal is to build a reproducible system that can discover, test, reject, and—only after passing strict evidence gates—eventually execute forex strategies with positive expected value after realistic trading costs.

**No profitability is assumed or guaranteed.**

## V1 scope

- EUR/USD
- GBP/USD
- USD/JPY
- Canonical data: 1-minute bid/ask OHLC
- Derived research timeframes: 5m, 15m, 1h
- Development budget: $0 until any real-money deployment is separately approved
- Historical research first; live money last

## Start here

1. `AGENTS.md` — rules for any future coding/agent session
2. `docs/project-state.md` — current phase and next action
3. `docs/master-spec.md` — permanent V1 product/architecture contract
4. `docs/build-order.md` — phase-by-phase implementation sequence
5. `docs/data-spec.md` — canonical market-data contract
6. `docs/research-testing-standard.md` — anti-leakage, backtest, and experiment rules
7. `docs/risk-execution-policy.md` — risk and execution constraints
8. `docs/decision-log.md` — approved decisions and amendments
9. `docs/experiment-log.md` — experiment record format
10. `docs/source-register.md` — external foundations and what each source is allowed to support

## Non-negotiable rules

- Do not add indices, crypto, gold, commodities, or extra FX pairs to V1.
- Do not pay for data, APIs, hosting, databases, or AI services during the research build.
- Do not manually edit raw market data.
- Do not use future information in features, labels, preprocessing, or trade decisions.
- Do not backtest with a frictionless single price; bid/ask and trading costs matter.
- Do not use martingale or loss-chasing.
- Do not promote a strategy because the equity curve looks good.
- Do not connect real money before every earlier gate is passed and a separate explicit approval is recorded.

## Current status

Phase 0 is frozen. **Phase 1 — Historical Data Acquisition** is active and its code/golden-sample gates are passing. Phase 2 remains locked until the full historical snapshot is acquired and provenance-verified.

### Phase 1 developer quick start

FMP Phase 1 has no runtime Python dependencies beyond the standard library.

Run unit tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Acquire one pair for an explicit UTC date range (`--end` is exclusive):

```bash
PYTHONPATH=src python -m fmp.data.cli fetch --pair EURUSD --start 2024-01-02 --end 2024-01-03 --out data
```

Acquire all V1 pairs for the frozen snapshot range:

```bash
PYTHONPATH=src python -m fmp.data.cli fetch \
  --pair ALL \
  --start 2015-01-01 \
  --end <EXCLUSIVE_LATEST_COMPLETE_DATE> \
  --out data
```

If a previously recorded 404 should be checked again because source history may have appeared later:

```bash
PYTHONPATH=src python -m fmp.data.cli fetch \
  --pair ALL \
  --start 2015-01-01 \
  --end <EXCLUSIVE_LATEST_COMPLETE_DATE> \
  --out data \
  --recheck-not-found
```

Summarize acquisition manifests:

```bash
PYTHONPATH=src python -m fmp.data.cli coverage --out data
```

Prove every planned chunk has consistent acquisition provenance and every completed raw file still matches its SHA-256 manifest:

```bash
PYTHONPATH=src python -m fmp.data.cli verify \
  --pair ALL \
  --start 2015-01-01 \
  --end <EXCLUSIVE_LATEST_COMPLETE_DATE> \
  --out data
```

`verify` returning `ready: true` means the Phase 1 snapshot is acquisition-complete and provenance-consistent. It does **not** mean the market data is clean; Phase 2 owns gap classification, quote sanity, bid/ask alignment, normalization, and derived-bar validation.

Raw files and manifests are intentionally ignored by Git.

Canonical repo: https://github.com/Dtwosam/FMP
