# Phase 8A — EXP-015 Stage A Reviewed Failure Freeze

**Date:** 2026-09-27  
**Status:** REVIEWED / CLOSED / FAILED / NO RETRY  
**Decision:** DEC-269  
**Experiment:** EXP-20260922-015  
**Scope:** Exact terminal review of the sole authoritative Stage A attempt

## Purpose

DEC-269 freezes the terminal result of the single DEC-264/267-authorized EXP-015 Stage A attempt. It does not repair, rerun, replace, or rescue the experiment.

The authoritative run is:

- run id: `36279397331`;
- workflow: `phase8a-exp015-stage-a`;
- path: `.github/workflows/phase8a-exp015-stage-a.yml`;
- event: `workflow_dispatch`;
- branch: `main`;
- head: `500f12ca5cb6e611f93b5d3a9eb52fb678e7774f`;
- attempt: `1`;
- conclusion: `failure`.

The one allowed Stage A slot is consumed permanently.

## Observed terminal result

The catalog job succeeded. Eight of nine Stage A cells succeeded and persisted exact non-expired artifacts.

The failed cell is **USDJPY / 1h**. Job `108508311714` failed in the actual `Run frozen EXP-015 Stage A cell` step. Its terminal traceback ends with:

`ValueError: daily start equity must be finite and positive`

This is a fail-closed research outcome: the reporting layer refused to emit ordinary performance metrics after the simulated account state reached a non-positive or non-finite daily-start-equity condition.

The final `stage-a-authorize` job was skipped. No Stage A authorization artifact exists. Therefore no authoritative aggregate survivor set exists.

## Exact persisted artifacts

DEC-269 binds exactly one catalog artifact and eight successful-cell artifacts:

- catalog `10918282455`, digest `sha256:78b7f008d5a0035d9acdb2a7169c206890c1b92ffd3a96575abc226adc212a89`;
- EURUSD 1h `10917993679`, digest `sha256:83c4109728f612743bed2efc0bb2da5b760a868d5498c57d9c39760de1874661`;
- EURUSD 15m `10918849922`, digest `sha256:c795e88b8bf0b08e39c155f279db546e93733a257d7a2cd9d12dfe46beed7091`;
- EURUSD 5m `10919892108`, digest `sha256:34eb6eb25c299c6230bc43d7ac00c476bb511c01b379468042712a46c153ddbc`;
- GBPUSD 1h `10919359533`, digest `sha256:83e3b02c93a74c4ebdd2bd9884fe6d59b89f07f114b75868e464848fb7ad49be`;
- GBPUSD 15m `10919473025`, digest `sha256:48081e99fa340f33309954e190ad3d16895cae92d76555484b11ec701bd591cb`;
- GBPUSD 5m `10921711075`, digest `sha256:3bf9f51ce7e6805efa8aee1911270f63c8c7a59d76326e2105b9d7bf33d909a6`;
- USDJPY 15m `10920831214`, digest `sha256:c93ed5f71ef0744f568c37c4b8c5cedd04c599e57c01dcec1d5bd629ee76510f`;
- USDJPY 5m `10921963807`, digest `sha256:00c9714813d24dfa02420b9a2c0f24120fc3e97b800c0243ed7b20d69c22c7df`.

There is no USDJPY 1h cell artifact and no Stage A authorization artifact.

## DEC-264 reviewer compatibility issue

The predeclared DEC-264 reviewer expected short matrix names such as `stage-a-cell (USDJPY, 1h)`. GitHub persisted the matrix jobs using expanded/truncated matrix-value names instead. That makes DEC-264's exact short-name inventory check incompatible with the real completed run.

DEC-269 does not weaken the experimental result. It replaces only the terminal evidence binding for this exact already-completed attempt by freezing immutable run id, head, attempt, exact job ids/conclusions, exact artifact ids/digests, the missing USDJPY 1h artifact, and the exact failure signature.

The guarded Stage A workflow is not changed.

## Closure semantics

DEC-269 records:

- Stage A successful aggregate result produced: **false**;
- authoritative survivor set produced: **false**;
- Stage A retry: **false**;
- Stage A replacement: **false**;
- Stage B source-open: **false**;
- Stage B execution: **false**;
- Stage C execution: **false**;
- portfolio selection: **false**;
- Phase 8A acceptance: **false**;
- Phase 8B: **false**;
- demo order placement: **false**;
- broker mutation: **false**;
- live orders: **false**;
- real-money action: **false**;
- trading: **false**.

The eight successful cell artifacts remain useful historical diagnostics only. They cannot be combined into an invented partial survivor set.

## Forward direction

EXP-015 is closed as pre-DEC-268 historical evidence. The project proceeds under DEC-268 discovery-first research. No new strategy search is derived from rescuing or retuning the failed EXP-015 run.
