#!/usr/bin/env python3
"""Write the historical trial inventory from unprotected repository documents.

The command reads the experiment log and the append-only trial ledger.
It does not append to the ledger and it does not open protected artifacts.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmp.research.trial_inventory import build_inventory, inventory_json, inventory_summary


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    check = "--check" in args
    inventory = build_inventory(ROOT)
    json_path = ROOT / "docs" / "trial-inventory.json"
    summary_path = ROOT / "docs" / "trial-inventory-summary.md"
    json_text = inventory_json(inventory)
    summary_text = inventory_summary(inventory)
    if check:
        same = (
            json_path.read_text(encoding="utf-8") == json_text
            and summary_path.read_text(encoding="utf-8") == summary_text
        )
        if not same:
            print("trial inventory outputs differ from docs/trial-inventory.json and docs/trial-inventory-summary.md", file=sys.stderr)
            return 1
        print("trial inventory outputs match")
        return 0
    json_path.write_text(json_text, encoding="utf-8")
    summary_path.write_text(summary_text, encoding="utf-8")
    print(f"wrote {json_path.relative_to(ROOT)} and {summary_path.relative_to(ROOT)}")
    print("programme-wide trial count: unknown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
