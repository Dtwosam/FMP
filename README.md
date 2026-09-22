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

Phases 0–7 are complete and preserved. **Phase 8A — Multi-pair, multi-strategy portfolio research** is active under DEC-039 / EXP-20260922-012.

The project still uses exactly EUR/USD, GBP/USD, and USD/JPY with the accepted Dukascopy historical dataset. The current build is adding a versioned strategy library, champion/challenger controls, multi-pair portfolio routing, and portfolio-level research before any new live-shadow campaign.

The previously prepared EXP-20260922-011 USDJPY-only shadow campaign was stopped before registration. Phase 8B live shadow, Phase 9 demo orders, and all real-money execution remain locked.

See `docs/project-state.md` for the current implementation milestone and `docs/superpowers/specs/2026-09-22-phase8a-portfolio-research-redesign.md` for the approved redesign.

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

`--recheck-not-found` is local-only in V1. Do not combine it with `--mirror-url`: canonical cloud manifests are first-write stable, so a previously persisted `not_found` manifest is not promoted in place to `complete` (DEC-013).

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
