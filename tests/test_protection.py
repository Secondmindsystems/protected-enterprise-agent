import unittest

from protected_enterprise_agent.models import Detection, ProviderUnavailable
from protected_enterprise_agent.protection import surrogate_transform


class ProtectionTests(unittest.TestCase):
    def test_transform_replaces_detected_value_and_preserves_business_text(self):
        text = "email avery.north@example.test has Gold service"
        start = text.index("avery")
        protected = surrogate_transform(text, [Detection("EMAIL_ADDRESS", start, start + len("avery.north@example.test"), 0.99)], "customer-001")
        self.assertNotIn("avery.north@example.test", protected)
        self.assertIn("Gold service", protected)
        self.assertIn("SURR-customer-001-00", protected)

    def test_transform_fails_closed_without_detection(self):
        with self.assertRaises(ProviderUnavailable):
            surrogate_transform("raw record", [], "customer-001")


if __name__ == "__main__":
    unittest.main()

