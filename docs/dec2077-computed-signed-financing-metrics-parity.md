# DEC-2077 — End-to-end computed full metrics for signed financing

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #2325 at `0adc6d24dd824f0f94ad6b9cc02bc17458a97a64`.

The previous signed-financing drafts used optional subsets of source performance claims to isolate semantic audit behavior. This draft checks actual `compute_backtest_metrics` output **with all its fields** round-tripping through the installed artifact writer and independent read-only semantic audit. Four economic outcomes are covered separately: custom debit turns a gross winner into a net loser; custom credit turns a gross loser into a net winner; signed debit neutralizes a gross winner; signed credit neutralizes a gross loser. Every case has exactly one completed trade with source-native trade economics and realization checkpoints.

Six proposed tests cover four complete-producer-to-audit roundtrips and two independent digest-verified semantic rejections: a small forged aggregate explicit-cost drift, and a forged financing metric with reversed sign. This checks calculations and stored evidence as a whole rather than claiming profitability from synthetic financing assumptions. Production engine and verifier unchanged.

**7,392 proposed test methods** (+6). Exact-head Phase3 and full historical/general suite required before pass attribution. Historical failed runs remain failed, pending checks no green credit. Phase8A #779/#820/#821 and eight independent security proof packages BLOCKED. No protected annual research, installed workflow/ref/runner mutation, merging, strategy promotion, brokers, orders or real capital.
