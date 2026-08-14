from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Qualify the pinned local container runtime and vendor services")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "src"))
    from protected_enterprise_agent.vendor_qualification import observe_runtime

    result = observe_runtime()
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    output = args.output or root / "evidence" / "runs" / "latest" / "RUNTIME_QUALIFICATION.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["pinned_vendor_runtime_observed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
