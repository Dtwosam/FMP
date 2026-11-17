# Historical trial inventory

The programme-wide trial count is unknown.

The ledger census leaves the programme-wide trial count null. Heading counts, pull requests, and verified local grids are not that total.

Experiment-log headings: 230.
Distinct experiment IDs in those headings: 84.
The heading count is not a trial count.

## Counting rules

- A programme-wide trial count stays unknown unless a source states that total.
- An experiment heading is not a trial.
- A printed configuration total is the only verified configuration count.
- A per-cell factor is recorded and is not multiplied into a total.
- A result row is a measurement dimension, not an additional trial.
- The same configuration cited by the ledger and the experiment log is one record.
- Repeated experiment IDs are kept apart and are not summed.
- Engineering, governance, and simulator checks are not market trials.
- A family can be sent to Benjamini-Yekutieli only when it is closed and every member has a valid p-value.
- A complete count does not make a p-value valid.

## Duplicate experiment IDs

EXP-20260927-062, EXP-20261002-067, EXP-20261003-100.
Repeated IDs stay as separate records. Their counts are not added together.

## Printed local counts

A number below is copied from the cited record. Adding these numbers does not produce an FMP-wide total.

Executed grids, where both a configuration total and a result-row total are printed:

- EXP-20260914-001#1: 81 configurations, 486 result rows.
- EXP-20260914-003#1: 54 configurations, 324 result rows.
- EXP-20260914-005#1: 27 configurations, 162 result rows.
- EXP-20260914-006#1: 27 configurations, 162 result rows.

Result rows printed without a configuration total:

- EXP-20260914-002#1: 324 result rows. The configuration total is not printed. A per-cell factor of 6 is printed and is not a total.
- EXP-20260914-004#1: 162 result rows. The configuration total is not printed.

Configuration totals printed for a search that the same record does not show as executed:

- EXP-20260922-013#1: 36 declared configurations. No executed trial count is stored.

## Data exposure

These market-trial records name a year from 2015 through 2022 in the data-range, train, or validation line, or the ledger marks that overlap. Those years are not untouched validation: EXP-20260914-001#1, EXP-20260914-002#1, EXP-20260914-003#1, EXP-20260914-004#1, EXP-20260914-005#1, EXP-20260914-006#1, EXP-20260915-007#1.
These records name both 2024 and 2025 in the data-range, train, or validation line. That window is not untouched validation: EXP-20260915-008#1.
A ledger trial count was present and was not stored as a configuration total:
- EXP-20260915-008#1: The trial count is the one frozen candidate carried into Phase 7, not the earlier 81-configuration search. Aggregate expectancy is not a trade-level distribution.
A missing period line stays unavailable. Protected historical artifacts were not opened.

## Multiple-testing readiness

Historical family status: INSUFFICIENT_TRIAL_CENSUS.
No historical p-value family is sent to the Benjamini-Yekutieli tool.
A verified local grid is one experiment's printed total. It is not a closed hypothesis family.
A later closed family can be assessed only by `family_correction_status` with its own members.

## Source-declared grids

A tuple in source is a declared parameter list. It is not evidence that the search was executed.

- MEAN_REVERSION_GRID in src/fmp/research/mean_reversion.py: 6 declared parameters.
- PREVIOUS_DAY_REJECTION_GRID in src/fmp/research/previous_day_rejection.py: 3 declared parameters.
- SESSION_BREAKOUT_GRID in src/fmp/research/session_breakout.py: 9 declared parameters.
- SESSION_SWEEP_REJECTION_GRID in src/fmp/research/session_sweep_rejection.py: 3 declared parameters.
- TREND_CONTINUATION_GRID in src/fmp/research/trend_continuation.py: 6 declared parameters.
- VOLATILITY_BREAKOUT_GRID in src/fmp/research/volatility_breakout.py: 3 declared parameters.
