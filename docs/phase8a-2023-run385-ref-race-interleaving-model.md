# DEC-619 — Finite interleaving model for run 385 dispatch-ref races

**Status:** source-only threat model. Not a dispatch preflight, execution authorization, real GitHub administrative witness, live tag checker, or approved 2023 workflow amendment.

DEC-618 PR #787 was merged at main `68c8ac7d83ba5bc0b5ee70551dfb2b96192d2169`, with exact-head focused tests, historical/general regression, compilation, and Phase 3 acceptance passing. Its untrusted-report tampering review was resolved. Issue #779 still blocks the one-shot annual 2023 workflow run 385 / attempt 1. The installed annual workflow Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1` still requires `GITHUB_REF=refs/heads/main` in preflight, all 18 cells, and freeze.

## The check-then-dispatch failure

Suppose the caller checks reviewed SHA `A` at `main` before asking the GitHub service to dispatch by `main`. An independent actor may change `main` to SHA `B` **after the caller's verification but before GitHub resolves that ref**. The workflow can then consume unique run number 385 on `B`. Checking the recorded `head_sha` after submission detects the problem but cannot unconsume run number 385. Retrying or replacement is not authorized.

DEC-619 enumerates all *four* legal orderings of a client SHA verification, independent ref mutation, server ref resolution, and post-dispatch result-head verification, with client-check before server-resolution before postcheck. It models one wrong-commit consumption counterexample when ref mutation is possible, including on apparently tagged refs where rules can be bypassed or the tag deleted and recreated.

| Assumption profile | Mutations admitted | Synthetic bad ordering | Effective admin proof |
| --- | --- | --- | --- |
| Unprotected `main` | Yes | 1 | Absent |
| Exclusively locked `main` | No (assumed only) | 0 | Absent |
| Mutable tag | Yes | 1 | Absent |
| Tag protection with a bypass actor | Yes | 1 | Absent |
| Tag delete/recreate possible | Yes | 1 | Absent |
| Continuously locked tag with no bypass | No (assumed only) | 0 | Absent |

**Zero synthetic bad orderings is not evidence that a real GitHub ref is protected.** It merely expresses what could be concluded *if* an administrator established an exclusive lock and the model's assumptions applied throughout dispatch. A protected-tag option also remains incompatible with the active annual main-ref-only workflow, irrespective of modeled tag immutability. Separately approved workflow *and* runtime SHA/ref identity binding changes are required.

## Execution boundaries

All identifiers are synthetic fixture strings: SHA `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` is "reviewed" and `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb` is "unreviewed" **only inside this model**. None is a real release target or repository mutation.

The stdlib-only model uses the pinned original annual workflow source, rejects drift from the DEC-617 job/event/ref checks, and emits an untrusted deterministic JSON report. Its independent report validator rebuilds the whole analysis from the actual pinned source and constants before comparing content, so recomputing an unkeyed JSON fingerprint cannot assert authority, remove a counterexample or alter schedules. The CLI runs `assess` only and forbids output inside the repository checkout. Neither module makes a network request, calls GitHub, creates refs, invokes annual execution, reads protected historical data or trades.

All reports say actual run-385 status was **not** verified by this model, admin lock witnesses are absent, no active workflow/runtime amendment is approved, and run 385 dispatch, retries and broker/trading remain blocked.

Example:

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_ref_race_interleaving_model.py assess --out /tmp/dec619-ref-race-model.json
```

## Next independently gated action

Issue #779 remains the source of truth for required real administrator evidence of exclusive main lock or effective immutable tag/no bypass throughout GitHub's server-side dispatch transaction. Reauthenticate frozen runtime, ten prior annual runs through 384, and all historical evidence; review exact ref/SHA bindings; and obtain a **separate narrowly scoped, explicit one-shot run 385 decision** before any dispatch. Do not create rulesets/tags, relax main-ref checks, submit/retry research, authorize later years, synthesize/promote strategy, mutate brokers, place orders or trade under DEC-619.
