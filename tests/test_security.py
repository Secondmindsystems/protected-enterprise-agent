import unittest

from protected_enterprise_agent.models import BoundaryViolation
from protected_enterprise_agent.security import assert_boundary_clean, find_forbidden


class SecurityTests(unittest.TestCase):
    def test_nested_payload_scan(self):
        self.assertEqual(find_forbidden({"payload": ["safe", "secret-canary"]}, ("secret-canary",)), ["secret-canary"])

    def test_boundary_blocks_match(self):
        with self.assertRaises(BoundaryViolation):
            assert_boundary_clean("dispatch", "contains secret-canary", ("secret-canary",))


if __name__ == "__main__":
    unittest.main()

