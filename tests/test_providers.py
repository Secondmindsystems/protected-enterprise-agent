import unittest

from protected_enterprise_agent.providers import DeterministicDiscoveryDouble, ProtegrityDiscoveryClient, ProtegritySemanticGuardrailClient


class ProviderTests(unittest.TestCase):
    def test_discovery_double_detects_fixture_entities(self):
        values = DeterministicDiscoveryDouble().discover("email a@example.test phone 202-555-0147 SSN 111-22-3333 card 4111111111111111")
        self.assertEqual({item.entity_type for item in values}, {"EMAIL_ADDRESS", "PHONE_NUMBER", "SOCIAL_SECURITY_ID", "CREDIT_CARD"})

    def test_vendor_payload_normalization(self):
        text = "Contact a@example.test"
        start = text.index("a@example.test")
        payload = {"entities": [{"entity_type": "EMAIL_ADDRESS", "start": start, "end": len(text), "score": 0.98}]}
        values = ProtegrityDiscoveryClient._normalize(payload, text)
        self.assertEqual(values[0].entity_type, "EMAIL_ADDRESS")
        self.assertEqual(values[0].start, start)

    def test_pinned_v2_classifications_payload_normalization(self):
        text = "Contact a@example.test"
        start = text.index("a@example.test")
        payload = {
            "classifications": {
                "EMAIL_ADDRESS": [
                    {"score": 1.0, "location": {"start_index": start, "end_index": len(text)}, "classifiers": []}
                ]
            }
        }
        values = ProtegrityDiscoveryClient._normalize(payload, text)
        self.assertEqual(values, [values[0]])
        self.assertEqual(values[0].entity_type, "EMAIL_ADDRESS")
        self.assertEqual((values[0].start, values[0].end), (start, len(text)))

    def test_semantic_guardrail_uses_pinned_batch_outcome(self):
        approved = {"messages": [{"score": 0.47, "processors": [{"score": 0.47}]}], "batch": {"outcome": "approved", "score": 0.47}}
        rejected = {"messages": [{"score": 0.57, "processors": [{"score": 0.57, "explanation": "malicious"}]}], "batch": {"outcome": "rejected", "score": 0.57}}
        self.assertEqual(ProtegritySemanticGuardrailClient._normalize(approved).decision, "ALLOW")
        result = ProtegritySemanticGuardrailClient._normalize(rejected)
        self.assertEqual(result.decision, "BLOCK")
        self.assertIn("malicious", result.labels)


if __name__ == "__main__":
    unittest.main()
