# DEC-624 — Inert 2023 three-layer ref/SHA admission ordering model

**Status: SOURCE-ONLY / UNINSTALLED / DOES NOT AUTHORIZE DISPATCH.** This branch is stacked on DEC-623 PR #792; its exact input source remains the installed annual workflow Git blob `09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1`.

## Important security boundary after DEC-623

DEC-623 established that preflight accesses accepted EXP-044 GitHub run/artifact **metadata** before the current execution-authorization command. There is another boundary: the three annual jobs all **checkout** the dispatched ref before their existing main-only shell guard. Although the current `Require exact merged main manual dispatch` step precedes Python setup and `pip install -e .`, it checks only `workflow_dispatch` and `refs/heads/main`; it does not bind an independently reviewed tag, workflow path, and resolved commit SHA. A proposed tag-route early check after installation cannot protect the runtime-install boundary, and a normal shell step after checkout cannot protect the checkout step.

## Proposed *synthetic only* three-layer structure

1. **Job-level admission before checkout:** a future exact event/ref/type/repository/workflow/SHA condition, backed by independently reviewed immutable authority, must prevent unapproved runs from entering any job. The offline model represents this as a fabricated boolean job-admission marker; it **does not create `jobs.<job>.if` conditions**.
2. **Exact ref/SHA/workflow identity before setup and package installation:** an early no-network check in each job must precede potentially executing code or third-party setup at the target ref. The offline model inserts a fabricated step-name label only.
3. **Postinstall binding recheck before first evidence access:** future runtime authorization must also fail closed on ref/SHA/workflow identity before any external evidence API call or download. The offline model again inserts a fabricated step-name label only. This is stricter than simply preserving the existing `require-execution` placement in preflight, where metadata API calls currently come first.

The script pins the installed annual workflow source by Git blob, checks exact three-job source order, constructs these *labels in memory* and verifies the ordering. Eighteen missing/retyped/late adverse scenarios must fail. Reports undergo full source-pinned canonical JSON reconstruction; forged flags cannot acquire authority by recalculating the hash.

```sh
PYTHONPATH=src python scripts/phase8a_annual_pattern_catalogue_2023_three_layer_admission_model.py assess --out /tmp/dec624-three-layer-admission.json
```

The CLI is assess-only, writes outside checkout, does not talk to GitHub, and cannot create or modify a workflow, ref, runtime source, or actual job guard.

**Not a solution yet:** GitHub's event contexts and ref protection signals are not an independently authenticated continuous no-bypass administrator witness. The approved comparison SHA/ref must come from an independent reviewed source, not simply copy the current `GITHUB_SHA` back into its own expected value. This report does not prove GitHub actually evaluates the proposed guard, that any tag exists or is unretargetable, that an installed workflow would be runnable on tags, or that the protected 2023 annual run number remains unused now.

Issue #779 stays open. Real 2023 run 385/attempt 1 requires externally authenticated immutable tag/no-bypass enforcement, a separately reviewed installed three-job workflow and runtime amendment with precheckout/preinstall/preaccess gates and consistent expected SHA provenance, a fresh run inventory, and a distinct explicit one-shot action decision. Ambiguous dispatch outcomes remain terminal, without retry, replacement or attempt 2. No protected history, future-year research, cross-year synthesis, Phase 8B, brokerage, demo/live orders, real money or trading is authorized here.
