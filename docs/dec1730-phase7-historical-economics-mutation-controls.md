# DEC-1730 — Adversarial controls for historical cost fragility and no-live claim

**DRAFT / NEVER MERGE / NEVER PROMOTE.** Exact-parent tests/docs-only child of #1976 at `f9be147381df910bb7034563229d758e5e209c8b`.

Adds **17 source-defined methods** (**5967 proposed**) that challenge the **existing** DEC-1718 Phase 7 historical performance guard using exclusively temporary text copies of the frozen documentation. All underlying published report bytes remain unchanged.

The mutations independently forge net return, dollar net P&L, 199-trade sample count and profit factor at each of 0.2-, 0.5-, and 1.0-pip adverse slippage; plus historic positive-window counts. The **actual** DEC-1718 numerical guard must fail every forged metric. Separate negative controls falsify the reported `PHASE7_PROMOTE_TO_SHADOW_DESIGN` status or replace the explicit denial of broker/demo/live order authority with an approval claim; the **actual** historic Phase 7 status guard must fail. A pristine control executes both original checks successfully.

This is not an alpha strategy improvement, forecasting result, live slippage estimate, or independently accepted Phase 8A annual research evidence. The established cost sensitivity remains retrospective: +0.757266% at 0.2 pips, +0.262176% at 0.5 pips, -0.562118% at 1.0 pip. New market evidence is not touched.

No production/parser/workflow/security changes, protected historical data, main/tag/ruleset mutation, annual dispatch/retry, strategy promotion, demo/live/broker/trading. External Phase 8A 2023/run385/attempt1 #779 remains BLOCKED. Exact-head Phase 3/full historical-general CI and independent qualified review are required.
