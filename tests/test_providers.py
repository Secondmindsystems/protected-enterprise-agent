import unittest

from protected_enterprise_agent.providers import DeterministicDiscoveryDouble, ProtegrityDiscoveryClient


class ProviderTests(unittest.TestCase):
    def test_discovery_double_detects_fixture_entities(self):
        values = DeterministicDiscoveryDouble().discover("email a@example.test phone 202-555-0147 SSN 111-22-3333 account ACCT-10000001")
        self.assertEqual({item.entity_type for item in values}, {"EMAIL_ADDRESS", "PHONE_NUMBER", "SOCIAL_SECURITY_ID", "ACCOUNT_NUMBER"})

    def test_vendor_payload_normalization(self):
        text = "Contact a@example.test"
        start = text.index("a@example.test")
        payload = {"entities": [{"entity_type": "EMAIL_ADDRESS", "start": start, "end": len(text), "score": 0.98}]}
        values = ProtegrityDiscoveryClient._normalize(payload, text)
        self.assertEqual(values[0].entity_type, "EMAIL_ADDRESS")
        self.assertEqual(values[0].start, start)


if __name__ == "__main__":
    unittest.main()

