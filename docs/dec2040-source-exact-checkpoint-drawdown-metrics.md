# DEC-2040 — Exact installed-source checkpoint drawdown and recovery metrics

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent PR #2288 at `991e754a1ed8a693d80ca304edeeabd7b6138d40`.

The installed source metric writer walks the published chronological equity checkpoints to compute maximum drawdown in USD, the matching peak-relative drawdown fraction, and recovery factor from total net PnL divided by maximum drawdown. The optional artifact auditor rebuilds those values from the same checkpoint stream, with generic near-equality tolerance that can admit tiny self-rehashed source metric differences.

For the exact installed engine version, require each present drawdown/recovery metric to equal the source's reconstructed value exactly, retaining generic-report tolerance, the no-drawdown null recovery case and finite-number validation. This does not authenticate the quotes or broker history behind the checkpoints.

Four source-defined methods: valid source drawdown/fraction/recovery from a mixed winner/loser curve, manifest-rehashed 1e-9 max drawdown USD tamper, rehashed 1e-13 max drawdown fraction tamper, and generic metric tolerance preservation. **7,238 proposed cumulative source-defined methods** (+4). Exact-head Phase3 and full historical/general validation must pass independently, with older failures preserved and queued or running checks unconfirmed.

Phase8A blockers #779/#820/#821 and eight independent external security proofs remain outstanding. No protected annual research, installed workflow/ref/runner modifications, strategy promotion, brokers, orders, merges or real capital.
