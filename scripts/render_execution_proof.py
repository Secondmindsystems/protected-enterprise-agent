from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REQUIRED_JSON = (
    "ADJUDICATION_RESULTS.json",
    "VENDOR_QUALIFICATION.json",
    "CANONICAL_RUN_MANIFEST.json",
    "SECURITY_RESULTS.json",
    "UTILITY_RESULTS.json",
    "ADVERSARIAL_RESULTS.json",
    "FAIL_CLOSED_RESULTS.json",
)


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path.name}")
    return value


def evaluate(root: Path, evidence_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    run_dir = (evidence_dir or root / "evidence" / "runs" / "latest").resolve()
    missing = [name for name in REQUIRED_JSON if not (run_dir / name).is_file()]
    if not (run_dir / "EVIDENCE_EVENTS.jsonl").is_file():
        missing.append("EVIDENCE_EVENTS.jsonl")
    if missing:
        return {"status": "NOT PROVEN", "missing": sorted(missing), "checks": {}}

    try:
        sys.path.insert(0, str(root / "src"))
        from protected_enterprise_agent.evidence import verify_evidence

        documents = {name: _read_object(run_dir / name) for name in REQUIRED_JSON}
        events = [json.loads(line) for line in (run_dir / "EVIDENCE_EVENTS.jsonl").read_text(encoding="utf-8").splitlines()]
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        technical = documents["ADJUDICATION_RESULTS.json"]
        vendor = documents["VENDOR_QUALIFICATION.json"]
        manifest = documents["CANONICAL_RUN_MANIFEST.json"]
        real_components = {
            event.get("provider_component")
            for event in events
            if event.get("details", {}).get("vendor_observed") is True
        }
        checks = {
            "frozen_commit": technical.get("commit") == head,
            "independent_adjudication": technical.get("disposition") == "PASS",
            "vendor_qualified": vendor.get("vendor_qualified") is True,
            "real_data_discovery": "Protegrity Data Discovery" in real_components,
            "real_semantic_guardrails": "Protegrity Semantic Guardrails" in real_components,
            "no_fallback": vendor.get("conditions", {}).get("fallback_not_used") is True,
            "causal_control": vendor.get("conditions", {}).get("causal_effect_observed") is True,
            "security": documents["SECURITY_RESULTS.json"].get("pass") is True,
            "utility": documents["UTILITY_RESULTS.json"].get("pass") is True,
            "adversarial": documents["ADVERSARIAL_RESULTS.json"].get("pass") is True,
            "fail_closed": documents["FAIL_CLOSED_RESULTS.json"].get("pass") is True,
            "evidence_integrity": manifest.get("evidence_pass") is True and not verify_evidence(run_dir / "EVIDENCE_EVENTS.jsonl"),
        }
    except (OSError, ValueError, json.JSONDecodeError, KeyError, AttributeError, TypeError, subprocess.SubprocessError) as exc:
        return {"status": "NOT PROVEN", "missing": [], "checks": {}, "error": f"{type(exc).__name__}: {exc}"}
    return {"status": "PROVEN" if all(checks.values()) else "NOT PROVEN", "missing": [], "checks": checks, "commit": head}


def main() -> int:
    parser = argparse.ArgumentParser(description="Render existing per-execution qualification evidence without creating evidence")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(args.root, args.evidence_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"EXECUTION PROOF: {result['status']}")
        if result.get("commit"):
            print(f"Frozen commit: {result['commit']}")
        for name, passed in result.get("checks", {}).items():
            print(f"  {'PASS' if passed else 'NOT PROVEN':10} {name}")
        for name in result.get("missing", []):
            print(f"  NOT PROVEN missing {name}")
        if result.get("error"):
            print(f"  NOT PROVEN {result['error']}")
    return 0 if result["status"] == "PROVEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
