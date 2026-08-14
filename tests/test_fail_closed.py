import tempfile
import unittest
from pathlib import Path

from protected_enterprise_agent.evidence import EvidenceWriter
from protected_enterprise_agent.models import ProviderUnavailable
from protected_enterprise_agent.pipeline import ProtectedEnterpriseAgent
from protected_enterprise_agent.providers import DeterministicGuardrailDouble
from protected_enterprise_agent.security import load_leak_manifest


ROOT = Path(__file__).resolve().parents[1]


class BrokenDiscovery:
    name = "broken discovery"
    version = "test"
    is_real_vendor = False

    def discover(self, text: str):
        raise ProviderUnavailable("intentional failure")


class FailClosedTests(unittest.TestCase):
    def test_provider_failure_does_not_write_raw_record_to_store_or_evidence(self):
        forbidden = load_leak_manifest(ROOT / "fixtures" / "leak_manifest.json")
        raw = "Avery North avery.north@example.test"
        with tempfile.TemporaryDirectory() as temporary:
            writer = EvidenceWriter(Path(temporary) / "events.jsonl", forbidden)
            agent = ProtectedEnterpriseAgent(BrokenDiscovery(), DeterministicGuardrailDouble(), forbidden, writer)
            with self.assertRaises(ProviderUnavailable):
                agent.ingest("customer-001", raw)
            self.assertEqual(agent.store.documents, ())
            writer.flush()
            self.assertNotIn("Avery North", writer.output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

