# DEC-1362 — Forward-only CI repair for source reads and hostile-key construction

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact parent #1585 DEC-1361 at `de17e60b23bfd25a6f9470c5936f3a3cdfda7a7e`. One repair commit; **1,000 source-defined unittest methods unchanged**. This is test-only source-fixture maintenance, not an annual workflow or runtime change.

## Original exact-head CI regressions, kept as failures

- #1579 DEC-1355 `tests`: two hostile hash-collision tests fail **while constructing their test dictionaries**, before the synthetic evaluator is invoked. `Colliding.__eq__` raises when the ordinary dictionary insertion encounters an existing matching-hash string key. That is a fixture error, not evidence of an evaluator call.
- #1581 DEC-1357 `tests`: the above two fixture failures plus missing working-tree `.github/workflows/phase8a-annual-pattern-catalogue.yml` at source-audit `setUpClass`. The committed workflow **does exist** at the exact PR SHA, but the filesystem file is unavailable by the time later tests run. Other later new source-audit tests are vulnerable to the same working-tree state.

## Repair without rewriting history

- Arm each hostile key's equality assertion **after** safe dictionary construction. Its equality returns `False` only during setup. The evaluator is still required to reject the untrusted key without executing custom equality while the trap is armed.
- Four workflow source-audit test modules now obtain the actual committed workflow text through **read-only local** `git show HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml`. This avoids relying on the mutable working-tree copy, does not query GitHub, run the annual CLI, install a workflow, or open protected annual inputs. A missing committed blob or unavailable Git fails the tests instead of inventing a passing fixture.
- No helper, executable annual job, source control admission, production workflow or trading behavior is modified. No new tests are counted; the proposal remains 1,000 method definitions until new verified coverage is added.

Every original PR SHA retains its own historical CI verdict; this future fix does **not** turn failed #1579 or #1581 heads green. DEC-650/#820 independently enforced protected original no-write and DEC-651/#821/#779 exclusive immutable 2023 run385 attempt1 admission stay **BLOCKED**. This draft requires successful completed exact-head Phase 3 **and** full historical CI followed by independent qualified review. No protected evidence, run/retry/rerun/dispatch, workflow/ruleset/permission mutation, broker/trading, merge or promotion.
