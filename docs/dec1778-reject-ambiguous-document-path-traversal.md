# DEC-1778 — Refuse ambiguous parent traversal before offline documentary path normalization

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent child of PR #2024, SHA `5cfdd21caa6c54360061c7eb2f14c3b55b47ebb3`.

The source-only DEC-1752 and historic DEC-1764 readers open every ancestor using `O_DIRECTORY | O_NOFOLLOW`, then validate bounded regular leaf files. But `os.path.abspath` also **lexically normalizes `..`**, potentially removing a parent component before the directory-FD traversal. The opened path might no longer faithfully represent the caller's supplied path, even if it ultimately has byte-identical pinned evidence.

This draft explicitly rejects any `..` component in the **un-normalized `Path.parts`** before absolute normalization, for both offline report programs. It is an operator-input fail-closed requirement, not a sandbox or independently verified OS policy. Normal sources still work; source pins, annual blocks, fixed historic financial figures and risk interpretations are unchanged.

Adds **4** direct reader/CLI tests (**6493 cumulative proposed methods**) using real temp files addressed by `detour/../docs` and `detour/../historical-phase7.md`. Both must exit **2**, print a BLOCKED error and no report. No protected market data, GitHub admin/ruleset/ref/workflow or runner privilege mutation, 2023/run385 dispatch/retry, broker/demo/live order or real-money trading. #779/#820/#821 remain BLOCKED and no amount of local path hardening substitutes for real security admission. Exact-head Phase3/full historical-general CI and independent review required.
