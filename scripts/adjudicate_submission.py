from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Independent challenge-fit and submission-congruence adjudicator")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    run_dir = root / "evidence" / "runs" / "latest"
    sys.path.insert(0, str(root / "src"))
    from protected_enterprise_agent.evidence import verify_evidence

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    technical = read_json(run_dir / "ADJUDICATION_RESULTS.json")
    vendor = read_json(run_dir / "VENDOR_QUALIFICATION.json")
    manifest = read_json(run_dir / "CANONICAL_RUN_MANIFEST.json")
    events = [json.loads(line) for line in (run_dir / "EVIDENCE_EVENTS.jsonl").read_text(encoding="utf-8").splitlines()]

    real_discovery = [event for event in events if event.get("provider_component") == "Protegrity Data Discovery" and event.get("details", {}).get("vendor_observed") is True]
    real_guardrails = [event for event in events if event.get("provider_component") == "Protegrity Semantic Guardrails" and event.get("details", {}).get("vendor_observed") is True]
    protected_stages = {event.get("pipeline_stage") for event in events if event.get("raw_sensitive_data_present") is False}
    challenge_checks = {
        "technical_adjudication_pass": technical.get("disposition") == "PASS" and technical.get("commit") == head,
        "vendor_qualified": vendor.get("vendor_qualified") is True,
        "two_real_protegrity_components": bool(real_discovery) and bool(real_guardrails),
        "two_or_more_protected_stages": len(protected_stages) >= 2,
        "security_utility_adversarial_evidence": all(manifest.get(name) is True for name in ("security_pass", "utility_pass", "adversarial_pass", "evidence_pass")),
        "evidence_hashes_valid": not verify_evidence(run_dir / "EVIDENCE_EVENTS.jsonl"),
        "causal_vendor_effect": bool([event for event in real_guardrails if event.get("decision") == "BLOCK"]),
    }
    challenge = {
        "schema_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": head,
        "pass": all(challenge_checks.values()),
        "checks": challenge_checks,
        "observations": {
            "real_data_discovery_events": len(real_discovery),
            "real_semantic_guardrail_events": len(real_guardrails),
            "protected_stages": sorted(str(stage) for stage in protected_stages),
        },
    }

    required = (
        "README.md", "ARCHITECTURE.md", "DEMO_SCRIPT.md", "KNOWN_LIMITATIONS.md",
        "docs/THREAT_MODEL.md", "docs/PROVENANCE.md", "docs/EVIDENCE_SUMMARY.md", "docs/SUBMISSION_CHECKLIST.md",
    )
    public_text = "\n".join((root / item).read_text(encoding="utf-8") for item in required if (root / item).is_file())
    congruence_checks = {
        "required_public_artifacts": all((root / item).is_file() for item in required),
        "no_obsolete_threshold_claim": "default `0.70` policy is provisional" not in public_text and "highest observed score is compared" not in public_text,
        "surrogate_boundary_explicit": "not Protegrity tokenization" in public_text,
        "two_compose_topology_disclosed": (
            "two official local stacks" in public_text
            and "two files must not be collapsed" in (root / "docs" / "VENDOR_SOURCE_DIVERGENCE.md").read_text(encoding="utf-8")
        ),
        "demo_matches_s4_observation": "this request is blocked before retrieval" in (root / "DEMO_SCRIPT.md").read_text(encoding="utf-8"),
        "technical_receipt_matches_head": technical.get("commit") == head,
        "challenge_fit_pass": challenge["pass"] is True,
    }
    congruence = {
        "schema_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": head,
        "pass": all(congruence_checks.values()),
        "checks": congruence_checks,
    }
    externalization = {
        "schema_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit": head,
        "state": "QUALIFIED_FOR_OPERATOR_EXTERNALIZATION" if challenge["pass"] and congruence["pass"] else "NOT_READY",
        "challenge_fit_pass": challenge["pass"],
        "submission_congruence_pass": congruence["pass"],
        "external_actions_performed": False,
        "operator_actions_remaining": ["public repository", "demo recording/upload", "terms and eligibility confirmation", "submission email"],
    }
    for name, value in (
        ("CHALLENGE_FIT_RESULTS.json", challenge),
        ("SUBMISSION_CONGRUENCE_RESULTS.json", congruence),
        ("EXTERNALIZATION_MANIFEST.json", externalization),
    ):
        (run_dir / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(externalization, indent=2, sort_keys=True))
    return 0 if externalization["state"] == "QUALIFIED_FOR_OPERATOR_EXTERNALIZATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
