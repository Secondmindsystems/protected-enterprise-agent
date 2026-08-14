from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


class RequiredGuardrailUnavailable:
    name = "required guardrail outage (deterministic demo)"
    version = "test-only-1"
    is_real_vendor = False

    def assess(self, text: str):
        from protected_enterprise_agent.models import ProviderUnavailable
        raise ProviderUnavailable("intentional required-guardrail outage")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic fail-closed and missing-proof demonstration")
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root / "scripts"))

    from protected_enterprise_agent.evidence import EvidenceWriter
    from protected_enterprise_agent.models import ProviderUnavailable
    from protected_enterprise_agent.pipeline import ProtectedEnterpriseAgent, deterministic_model, load_fixtures
    from protected_enterprise_agent.providers import DeterministicDiscoveryDouble, DeterministicGuardrailDouble
    from protected_enterprise_agent.security import load_leak_manifest
    from render_execution_proof import evaluate

    forbidden = load_leak_manifest(root / "fixtures" / "leak_manifest.json")
    model_calls = 0

    def model_spy(prompt: str) -> str:
        nonlocal model_calls
        model_calls += 1
        return deterministic_model(prompt)

    with tempfile.TemporaryDirectory() as temporary:
        temporary_path = Path(temporary)
        writer = EvidenceWriter(temporary_path / "fault-events.jsonl", forbidden)
        agent = ProtectedEnterpriseAgent(DeterministicDiscoveryDouble(), RequiredGuardrailUnavailable(), forbidden, writer, model_spy)
        for fixture in load_fixtures(root / "fixtures" / "customers.json"):
            agent.ingest(str(fixture["fixture_id"]), str(fixture["record"]))
        try:
            agent.ask("S1", "Please help with support case CASE-104.")
            outage_blocked = False
        except ProviderUnavailable:
            outage_blocked = model_calls == 0

        agent.guardrail = DeterministicGuardrailDouble()
        recovered = agent.ask(
            "S1",
            "I am unable to access my active Gold account; can you assist me with support case CASE-104 and its resolution?",
            ("expedited replacement",),
        )
        recovery_pass = recovered.decision == "ALLOW" and recovered.utility_result == "PASS" and model_calls == 1

        current = root / "evidence" / "runs" / "latest"
        incomplete = temporary_path / "incomplete-evidence"
        shutil.copytree(current, incomplete)
        (incomplete / "VENDOR_QUALIFICATION.json").unlink(missing_ok=True)
        missing_proof_blocked = evaluate(root, incomplete)["status"] == "NOT PROVEN"

    print("DETERMINISTIC NEGATIVE-PROOF DEMO (not vendor-behavior evidence)")
    print(f"  {'PASS' if outage_blocked else 'FAIL'} required guardrail outage blocked before model")
    print(f"  {'PASS' if missing_proof_blocked else 'FAIL'} missing vendor evidence rendered NOT PROVEN")
    print(f"  {'PASS' if recovery_pass else 'FAIL'} restored guardrail allowed identical legitimate workflow")
    return 0 if outage_blocked and missing_proof_blocked and recovery_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
