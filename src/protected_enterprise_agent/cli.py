from __future__ import annotations

import argparse
import json
from pathlib import Path

from .qualification import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Protected Enterprise Agent canonical qualification demo.")
    parser.add_argument("--require-vendor", action="store_true", help="Require live local Protegrity Data Discovery and Semantic Guardrails services.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = run(args.root.resolve(), args.require_vendor)
    print(json.dumps(result, indent=2, sort_keys=True))
    required = ("security", "utility", "adversarial", "evidence", "public_estate")
    return 0 if all(result[name] for name in required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
