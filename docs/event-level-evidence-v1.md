# Event-level evidence V1

**Status:** source-only infrastructure. Synthetic observations only.
**Governing method:** discovery-first annual pattern catalogue research under DEC-469 / DEC-268.
**Pattern tool:** `event-level-evidence-v1`.
**Protocol:** `fmp-annual-pattern-catalogue-event-evidence-v1`.
**Parent protocol:** DEC-470, unchanged.

This contract preserves caller-supplied outcome events so a later milestone can measure overlap, episode structure, and uncertainty. It does not execute a catalogue, read a historical artifact, score DEC-470, or select a strategy.

## What annual records already store

`AnnualPatternRecord.event_fingerprint` is the SHA-256 of the sorted observation ids joined by newlines. The frozen DEC-472 cell schema stores that hash and the aggregate statistics. It does not store observation ids, availability timestamps, exit timestamps, or per-event nets.

Those fields cannot be reconstructed from the hash. Authentic event-level evidence therefore depends on the original observation rows. Those rows are historical artifacts. This module does not open them. `recover_event_ids_from_event_fingerprint` always fails closed.

Until a later decision authorizes those rows, the only admissible input is a caller-supplied synthetic `OutcomeObservation` (and, when supplied, a matching `FeatureObservation`).

## Event identity

A physical event is one observation inside one annual segment, symbol, timeframe, and horizon. Its identity is SHA-256 of the canonical JSON for that key, under scheme `observation-key-sha256-v1`.

The identity keeps the original `observation_id`. It is not an inversion of `event_fingerprint`. LONG and SHORT measurements of the same window share one identity. The same observation id on two horizons is two events, because the outcome definition differs. The same observation id on two symbols, timeframes, or segments stays unresolved: the events are not merged, and independence is not established.

## Outcome window

The window is the half-open interval `[available_at_utc, exit_timestamp_utc)`.

`exit_timestamp_utc` must equal `available_at_utc` plus the frozen horizon, which is the `OutcomeObservation` rule. Both timestamps must be UTC. The availability timestamp must fall inside the annual segment, and the exit timestamp must fall strictly before the segment end. A window that only touches the next window's start does not overlap it.

Overlap is evaluated on those timestamps. A connected episode group is a connected component of that overlap relation:

1. Sort events by availability time, then exit time, then event identity.
2. Start a group at the next event.
3. Add a later event while its availability is strictly before the group's maximum exit.
4. Otherwise start a new group.

The sweep counts overlapping pairs with an active-end list. It does not store the pair list.

## Five counts

Within one annual segment, symbol, timeframe, and horizon:

| Count | Meaning |
| --- | --- |
| Raw observation support | Supplied directional measurements. LONG and SHORT both count. |
| Unique observed events | Physical events after LONG and SHORT collapse. |
| Overlapping outcome intervals | Events that overlap at least one other event in the scope, and the number of overlapping pairs. |
| Connected episode groups | Components from the sweep above. |
| Candidate effective independent sample size | The number of those components. |

A pattern's candidate size is the number of scope-level episode groups its members touch. That can be smaller than the pattern's own direct-overlap component count. In a chain A–B–C, A and C do not overlap each other, but they still sit in one episode when B bridges them. Direct overlap is reported separately.

A sum of within-horizon candidate sizes is also reported. That sum is a descriptive total. It is not a global independent sample size.

## Dependence the counts leave in place

- A connected episode group is not treated as statistically independent of other groups. Adjacent groups that only touch can still be serially dependent.
- Cross-horizon overlap is reported on its own sweep. A 240-minute window can contain a 60-minute window. The within-horizon candidate ignores that dependence.
- Cross-symbol and cross-timeframe clock-time dependence is not measured. Independence is not established.
- Hypotheses that share an event, including LONG and SHORT of one window, are dependent. The DEC-470 Jaccard threshold is recorded and is not applied. No pattern is dropped.
- Overlapping observations remain separate observations in raw support. They are not counted as independent trials.

## Statistical limits

The document reports descriptive evidence. It performs no statistical inference.

- No p-value, confidence interval, standard error, or multiple-comparison adjustment is computed.
- Annual aggregate counts are not significance and are not evidence of profitability.
- The frozen search universe remains 89,460 directional hypotheses per annual segment.
- EXP-20261118-069 remains a constraint. Its synthetic false-pass counts, including 4,922 correlated zero-gross passes at 8 pips on seed 20261120, are not an acceptance threshold. DEC-470 was not retuned. The recorded gate constants are not applied to events.

A later uncertainty estimate needs four things this contract does not supply:

1. A serial-dependence model beyond geometric overlap, including dependence between episode groups.
2. A multiple-hypothesis correction that covers the full 89,460-hypothesis universe and hypotheses that share events. An uncorrected p-value is not evidence of profitability.
3. Selection-bias control for any threshold, rank, or shortlist chosen after seeing outcomes.
4. An effective-sample-size model that is stated and tested. Raw support and the candidate component count are not that model.

Structural validation recomputes the canonical document and its SHA-256. A passing check means the synthetic document is internally consistent. It is not independent validation of authentic frozen annual evidence.

## Integrity

Canonical JSON uses sorted keys, compact separators, and a trailing newline. `content_sha256` is the SHA-256 of that encoding of every field except `content_sha256`. Provenance carries a source label, a 40-character code commit, and a caller-supplied synthetic manifest SHA-256. Duplicate measurements, contradictory windows, contradictory nets, contradictory memberships, and malformed timestamps fail closed.

## Authorizations that stay closed

Historical artifact reads, catalogue execution, historical result production, cross-year result production, Strategy V1 synthesis, statistical promotion, workflow activation, DEC-629 adoption, DEC-630 adoption, annual run 385, broker mutation, and trading stay false.

No decision-log number is assigned. This contract does not amend DEC-470 or any locked gate.
