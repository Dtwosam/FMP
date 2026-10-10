# DEC-671 — Offline run-385 admission race interleaving model

**SOURCE-ONLY / DRAFT / NEVER MERGE / NO ACTION AUTHORIZATION.**

This tiny, deterministic model complements DEC-651 draft #821 and issue #779. It performs **no** GitHub API requests, no network access, no reads of historical/protected annual artifacts, no workflow dispatch, and no operations on actual repository refs, branch protections, tokens, tags or permissions.

The user-visible "review_main" operation records the approved 40-character *synthetic* commit. A later "our_dispatch" resolves the model's *current mutable main* and allocates the next synthetic run number. Two other events can intervene: "update_main" changes the commit, and "competing_dispatch" consumes a synthetic run number with unapproved inputs. The program enumerates the **six possible event orders after review_main**, not just one happy-path ordering.

It proves two **model-specific** failures:
- An ordinary client-side main SHA check is not an atomic compare-and-dispatch: changing main after observation but before our event can bind the unique run 385 to unreviewed source.
- Freezing the main ref alone does not reserve run 385: a competing authorized dispatcher can consume 385 with incorrect event inputs, leaving the legitimate event number 386, which the installed annual guards cannot repair.

| Model assumptions | Unsafe of 6 synthetic schedules |
| --- | ---: |
| Neither ref freeze nor dispatcher exclusion | 4 |
| Exclusive dispatcher only; mutable main | 3 |
| Frozen main only; competing dispatcher | 3 |
| Both controls **assumed** | 0 |

The last row is **MODEL_CONSISTENT_UNVERIFIED**, exit 3, and explicitly states server_enforcement_verified=false. It is not proof that GitHub or an administrator has established either boundary; actual privileged bypass actors and control-plane races are outside the toy model. All unsafe cases are BLOCKED exit 2. Every outcome says can_authorize_dispatch=false and annual_run_385_consumed=false.

The default CLI is inert and blocked. To run purely in-memory counterexamples:

    python -B scripts/dec671_offline_run385_race_model.py --execute-offline-model

To make both hypothetical assumptions **without changing any real settings**:

    python -B scripts/dec671_offline_run385_race_model.py --execute-offline-model --assume-ref-frozen --assume-dispatch-exclusive

The source defines 13 synthetic unit cases, testing SHA-change races, the competing-dispatch run-number loss, both isolated insufficiencies, all six schedules, and nonauthorizing CLI behavior.

A real review must still authenticate all GitHub principals capable of moving the reviewed ref, changing rulesets, bypassing protection, dispatching/retrying the workflow, selecting a source tree, or consuming the run number. Any permission/lock assumption without separately confirmed **server-side exclusive enforcement** is BLOCKED. DEC-650 actual runner OS isolation #820 is an additional independent blocker; a correct dispatch lock does not make protected-source checkout safe.

The work is for reviewer analysis only. No merge/ready promotion, no actual run385 dispatch/test/rerun/retry, no protected annual source/artifact access, no main/workflow/tag/ruleset/permission/runner change, broker or trading operation.
