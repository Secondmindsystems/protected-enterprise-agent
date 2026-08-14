from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def command(root: Path, *args: str, env: dict[str, str] | None = None) -> tuple[int, str]:
    completed = subprocess.run(args, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)
    return completed.returncode, completed.stdout


def tracked_files(root: Path) -> list[Path]:
    code, output = command(root, "git", "ls-files")
    if code:
        raise RuntimeError(output)
    return [root / line for line in output.splitlines() if line]


def scan_text(paths: list[Path], patterns: dict[str, re.Pattern[str]], exclusions: tuple[str, ...] = ()) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for path in paths:
        relative = path.as_posix()
        if any(fragment in relative for fragment in exclusions):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        matched = [name for name, pattern in patterns.items() if pattern.search(text)]
        if matched:
            findings[str(path)] = matched
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Independent frozen-commit adjudicator")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--require-vendor", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "src"))
    from protected_enterprise_agent.qualification import run

    checks: dict[str, object] = {}
    head_code, head = command(root, "git", "rev-parse", "HEAD")
    status_code, status = command(root, "git", "status", "--porcelain", "--untracked-files=all")
    checks["frozen_commit"] = {"pass": head_code == 0 and bool(head.strip()), "value": head.strip()}
    status_lines = [line for line in status.splitlines() if not line.lower().startswith("warning:")]
    checks["clean_tree"] = {"pass": status_code == 0 and not status_lines, "details": status_lines}

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")
    test_code, test_output = command(root, sys.executable, "-m", "unittest", "discover", "-s", str(root / "tests"), "-v", env=environment)
    checks["automated_tests"] = {"pass": test_code == 0, "summary": test_output.splitlines()[-1:]}

    try:
        rehearsal = run(root, require_vendor=False)
        checks["deterministic_rehearsal"] = {"pass": all(rehearsal[key] for key in ("security", "utility", "adversarial", "evidence", "public_estate")), "result": rehearsal}
    except Exception as exc:  # independent adjudicator must preserve the exact failed gate
        checks["deterministic_rehearsal"] = {"pass": False, "error_type": type(exc).__name__, "message": str(exc)}

    if args.require_vendor:
        try:
            vendor = run(root, require_vendor=True)
            checks["vendor_qualification"] = {"pass": vendor["vendor_observed"] and all(vendor[key] for key in ("security", "utility", "adversarial", "evidence", "public_estate")), "result": vendor}
        except Exception as exc:
            checks["vendor_qualification"] = {"pass": False, "error_type": type(exc).__name__, "message": str(exc)}
    else:
        checks["vendor_qualification"] = {"pass": False, "not_run": True, "reason": "live vendor qualification required for final promotion"}

    files = tracked_files(root)
    secret_patterns = {
        "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "openai_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
        "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    }
    secret_findings = scan_text(files, secret_patterns)
    checks["secret_scan"] = {"pass": not secret_findings, "findings": secret_findings}

    private_patterns = {
        "private_system_name": re.compile(r"\b\x53econd\s+\x4dind\b", re.I),
    }
    private_findings = scan_text(files, private_patterns)
    checks["public_ip_scan"] = {"pass": not private_findings, "findings": private_findings}

    prohibited_claims = {
        "production_ready": re.compile(r"\b(?:is|proves|guarantees) production[- ]ready\b", re.I),
        "zero_risk": re.compile(r"\bzero[- ]risk\b", re.I),
        "compliance_claim": re.compile(r"\bguarantees? (?:regulatory )?compliance\b", re.I),
        "universal_prevention": re.compile(r"\bguarantees? (?:universal )?(?:leak|prompt injection) prevention\b", re.I),
    }
    claim_findings = scan_text([path for path in files if path.suffix.lower() in {".md", ".txt"}], prohibited_claims)
    checks["claim_review"] = {"pass": not claim_findings, "findings": claim_findings}

    required_docs = ("README.md", "ARCHITECTURE.md", "KNOWN_LIMITATIONS.md", "DEMO_SCRIPT.md", "docs/THREAT_MODEL.md", "docs/PROVENANCE.md")
    missing_docs = [item for item in required_docs if not (root / item).exists()]
    checks["submission_package"] = {"pass": not missing_docs, "missing": missing_docs}

    failed = [name for name, value in checks.items() if isinstance(value, dict) and not value.get("pass", False)]
    vendor_failed = "vendor_qualification" in failed
    if not failed:
        disposition = "PASS"
        state = "QUALIFIED_FOR_OPERATOR_EXTERNALIZATION"
    elif vendor_failed and all(name == "vendor_qualification" for name in failed):
        disposition = "HOLD"
        state = "READY_FOR_VENDOR_QUALIFICATION"
    else:
        disposition = "REPAIR_REQUIRED"
        state = "NOT_READY"

    result = {
        "schema_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": head.strip(),
        "disposition": disposition,
        "state": state,
        "failed_checks": failed,
        "checks": checks,
    }
    output = args.output or root / "evidence" / "runs" / "latest" / "ADJUDICATION_RESULTS.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if disposition == "PASS" else (2 if disposition == "HOLD" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
