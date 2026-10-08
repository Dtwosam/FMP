# DEC-621 — Ambiguous annual dispatch must remain a no-retry hold

**Status:** Offline-only synthetic incident model. Not an annual dispatcher, authorization, live run inventory, administrator attestation or permission to submit 2023 research.

## Scope and rationale

DEC-619 exposed the check-then-dispatch race when GitHub resolves mutable refs on its server. DEC-620 reviews *untrusted* claims of an exclusive no-bypass lock across that server transaction but provides no actual administrator proof. DEC-621 models the **post-submission uncertainty** that arises if a future authorized one-shot dispatch is attempted and the client loses its HTTP response, times out or cannot confirm a resulting run.

A failure response or timeout does **not** prove that the server rejected the request. If GitHub accepted the request, run 385 might already have been consumed. Sending another request or running a retry could therefore create a forbidden run 386 or attempt 2. The safe terminal state is a **hard hold with no second dispatch**, pending independent live run/receipt reconciliation and an entirely distinct human authorization decision, not an automated retry.

The active annual workflow is pinned at Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`, with original three-job main-ref enforcement in preflight, all catalogue cells and freeze. No part of that workflow or the 2023 runtime is modified by DEC-621. The previous 2022 annual freeze run is `37663157285`; the only prospective run is 2023 catalogue run 385 / attempt 1.

## Input and synthetic interpretation

The assess-only CLI takes an untrusted, local JSON file with strict fields: `schema`, `reviewed_code_sha` (lowercase 40-hex synthetic SHA), strict boolean `dispatch_call_made`, `client_observed_outcome` and a bounded list `observed_runs`. The allowed client outcomes are `not_called`, `local_validation_failed`, `http_accepted`, `http_rejected`, `transport_error`, `timeout` and `unknown`.

Each hypothetical observed run contains a positive integer `run_id`, `run_number`, `run_attempt`, `previous_annual_freeze_run_id`, `workflow`, `event` (exactly `workflow_dispatch`) and lowercase `head_sha`. An exact synthetic match requires run 385, attempt 1, the approved predecessor, the annual workflow name and the input reviewed SHA. Inputs are not real GitHub run records.

| Offline case | Synthetic interpretation | Dispatch/retry allowed? |
| --- | --- | --- |
| No attempted call, no observations | Not submitted *in the model*, not live inventory proof | No |
| Call attempted, timeout/transport error, no run observed | Ambiguous submission; server may have accepted | No |
| Call attempted, HTTP rejected, no run observed | Ambiguous response, not a server inventory proof | No |
| Call attempted, HTTP accepted, no run observed | Ambiguous run creation | No |
| One exact run observed with HTTP accepted | Needs independent external evidence | No |
| Wrong SHA, wrong run or attempt, wrong predecessor, multiple matches, or contradictory response | Terminal conflict | No |

Example fixture (does not describe a real request):

```json
{
  "schema": "fmp-2023-run385-ambiguous-dispatch-terminal-hold-v1",
  "reviewed_code_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "dispatch_call_made": true,
  "client_observed_outcome": "timeout",
  "observed_runs": []
}
```

Local simulation:

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_ambiguous_dispatch_hold_model.py assess \
  --simulation-json /tmp/dec621-fixture.json \
  --out /tmp/dec621-hold-report.json
```

The CLI uses duplicate-object-key JSON rejection, strict boolean/integer identity checks, refuses output inside the checkout and contains no GitHub API or network actions. It cannot issue a dispatch, mutate tags/branch/rulesets, read protected historical data, write an active workflow, place orders or trade.

Every possible report remains `terminal_one_shot_hold=true`, `dispatch_blocked=true`, `retry_authorized=false`, `second_dispatch_authorized=false`, `rerun_authorized=false`, `replacement_run_authorized=false`, `live_annual_run_inventory_authenticated=false` and `trading_authorized=false`. An independent validator reconstructs the whole report against pinned active annual source and uses **type-sensitive canonical JSON** comparison, so rehashing a forged privilege flag cannot confer authority.

## Operational gate still outstanding

Issue #779 requires independent, authenticated no-bypass administrator lock evidence across server-side dispatch, approved workflow+2023 runtime SHA/ref binding for a tag route, a fresh read of the annual workflow_dispatch history (run 385 absent), and a separate explicit one-shot execution decision. After any *future* ambiguous request, the one-shot action must be held for independent forensic reconciliation; **never infer safe retry from an HTTP error**. This source-only simulation cannot satisfy any of those real-world requirements.
