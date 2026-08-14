import unittest

from protected_enterprise_agent.vendor_qualification import evaluate_vendor_qualification


def event(component: str, stage: str, decision: str, details: dict[str, object]) -> dict[str, object]:
    return {"provider_component": component, "pipeline_stage": stage, "decision": decision, "details": details}


class VendorQualificationTests(unittest.TestCase):
    def test_availability_is_not_qualification(self):
        result = evaluate_vendor_qualification(
            {"pinned_vendor_runtime_observed": False},
            [event("Protegrity Data Discovery", "ingestion", "ALLOW_PROTECTED_ONLY", {"vendor_observed": True, "detection_count": 2})],
            security_pass=True,
            utility_pass=True,
            adversarial_pass=True,
            fallback_used=False,
        )
        self.assertTrue(result["vendor_available"])
        self.assertFalse(result["vendor_qualified"])

    def test_all_independent_conditions_are_required(self):
        events = [
            event("Protegrity Data Discovery", "ingestion", "ALLOW_PROTECTED_ONLY", {"vendor_observed": True, "detection_count": 2}),
            event("Protegrity Semantic Guardrails", "inference", "ALLOW", {"vendor_observed": True, "risk_score": 0.1}),
            event("Protegrity Semantic Guardrails", "input_guardrail", "BLOCK", {"vendor_observed": True, "risk_score": 0.9}),
        ]
        result = evaluate_vendor_qualification(
            {"pinned_vendor_runtime_observed": True},
            events,
            security_pass=True,
            utility_pass=True,
            adversarial_pass=True,
            fallback_used=False,
        )
        self.assertTrue(result["vendor_qualified"])
        self.assertEqual(result["failed_conditions"], [])

    def test_fallback_or_missing_causal_block_fails_closed(self):
        events = [
            event("Protegrity Data Discovery", "ingestion", "ALLOW_PROTECTED_ONLY", {"vendor_observed": True, "detection_count": 1}),
            event("Protegrity Semantic Guardrails", "inference", "ALLOW", {"vendor_observed": True, "risk_score": 0.2}),
        ]
        result = evaluate_vendor_qualification(
            {"pinned_vendor_runtime_observed": True},
            events,
            security_pass=True,
            utility_pass=True,
            adversarial_pass=True,
            fallback_used=True,
        )
        self.assertFalse(result["vendor_qualified"])
        self.assertIn("fallback_not_used", result["failed_conditions"])
        self.assertIn("causal_effect_observed", result["failed_conditions"])


if __name__ == "__main__":
    unittest.main()
