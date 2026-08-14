from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .evidence import EvidenceWriter
from .models import AgentResponse, BoundaryViolation, ProviderUnavailable
from .protection import surrogate_transform
from .providers import DiscoveryProvider, GuardrailProvider
from .retrieval import LocalVectorStore
from .security import assert_boundary_clean


ModelProvider = Callable[[str], str]


def deterministic_model(prompt: str) -> str:
    """Provider-neutral test/demo backend; it never receives raw fixture PII."""
    if "expedited replacement" in prompt:
        return "The active Gold account qualifies for expedited replacement under the cited support policy."
    if "fraud-team escalation" in prompt:
        return "The account in review requires fraud-team escalation under the cited support policy."
    return "The protected records do not establish a supported resolution."


class ProtectedEnterpriseAgent:
    def __init__(
        self,
        discovery: DiscoveryProvider,
        guardrail: GuardrailProvider,
        forbidden: tuple[str, ...],
        evidence: EvidenceWriter,
        model: ModelProvider = deterministic_model,
    ) -> None:
        self.discovery = discovery
        self.guardrail = guardrail
        self.forbidden = forbidden
        self.evidence = evidence
        self.model = model
        self.store = LocalVectorStore()

    def ingest(self, fixture_id: str, raw_record: str) -> str:
        try:
            detections = self.discovery.discover(raw_record)
            protected = surrogate_transform(raw_record, detections, fixture_id)
            assert_boundary_clean("embedding input", protected, self.forbidden)
            metadata = {"fixture_id": fixture_id, "protection": "application-level-surrogate", "discovery": self.discovery.name}
            assert_boundary_clean("vector metadata", metadata, self.forbidden)
            self.store.add(fixture_id, protected, metadata)
            self.evidence.emit(
                scenario_id="INGEST", pipeline_stage="ingestion", fixture_id=fixture_id,
                classification_result="DETECTED", detected_entity_types=sorted({item.entity_type for item in detections}),
                protection_action="APPLICATION_SURROGATE", protection_provider="application",
                provider_component=self.discovery.name, component_version=self.discovery.version,
                decision="ALLOW_PROTECTED_ONLY", downstream_surface="vector_store",
                raw_sensitive_data_present=False, utility_result="NOT_EVALUATED", security_result="PASS",
                details={"detection_count": len(detections), "vendor_observed": self.discovery.is_real_vendor},
            )
            return protected
        except (ProviderUnavailable, BoundaryViolation) as exc:
            self.evidence.emit(
                scenario_id="S7", pipeline_stage="ingestion", fixture_id=fixture_id,
                classification_result="ERROR", detected_entity_types=[], protection_action="BLOCK",
                protection_provider="none", provider_component=self.discovery.name,
                component_version=self.discovery.version, decision="FAIL_CLOSED",
                downstream_surface="none", raw_sensitive_data_present=False,
                utility_result="BLOCKED", security_result="PASS",
                details={"error_type": type(exc).__name__},
            )
            raise

    def ask(self, scenario_id: str, user_input: str, expected_facts: tuple[str, ...] = ()) -> AgentResponse:
        assessment = self.guardrail.assess(user_input)
        input_detections = self.discovery.discover(user_input)
        protected_input = surrogate_transform(user_input, input_detections, "query") if input_detections else user_input
        assert_boundary_clean("protected user input", protected_input, self.forbidden)

        if assessment.decision == "BLOCK":
            response_text = "Request blocked by the application risk policy. No model dispatch occurred."
            self.evidence.emit(
                scenario_id=scenario_id, pipeline_stage="input_guardrail", fixture_id="query",
                classification_result="ASSESSED", detected_entity_types=sorted({item.entity_type for item in input_detections}),
                protection_action="BLOCK", protection_provider="application-policy",
                provider_component=self.guardrail.name, component_version=self.guardrail.version,
                decision="BLOCK", downstream_surface="application_response",
                raw_sensitive_data_present=False, utility_result="NOT_APPLICABLE", security_result="PASS",
                details={"risk_score": assessment.score, "labels": list(assessment.labels), "vendor_observed": self.guardrail.is_real_vendor},
            )
            return AgentResponse(response_text, "PASS", "NOT_APPLICABLE", "BLOCK", ())

        documents = self.store.search(protected_input)
        retrieved = "\n".join(document.text for document in documents)
        assert_boundary_clean("retrieved context", retrieved, self.forbidden)
        prompt = f"Use only these protected records to answer the business question. Never reveal surrogate identifiers.\nQUESTION: {protected_input}\nCONTEXT:\n{retrieved}"
        assert_boundary_clean("model dispatch", prompt, self.forbidden)
        response_text = self.model(prompt)
        assert_boundary_clean("model output", response_text, self.forbidden)
        utility = "PASS" if all(fact.lower() in (retrieved + response_text).lower() for fact in expected_facts) else "FAIL"
        self.evidence.emit(
            scenario_id=scenario_id, pipeline_stage="inference", fixture_id=documents[0].fixture_id if documents else "none",
            classification_result="ASSESSED", detected_entity_types=sorted({item.entity_type for item in input_detections}),
            protection_action="PROTECTED_DISPATCH", protection_provider="application-surrogate",
            provider_component=self.guardrail.name, component_version=self.guardrail.version,
            decision="ALLOW", downstream_surface="application_response", raw_sensitive_data_present=False,
            utility_result=utility, security_result="PASS",
            details={"risk_score": assessment.score, "retrieved_count": len(documents), "vendor_observed": self.guardrail.is_real_vendor},
        )
        return AgentResponse(response_text, "PASS", utility, "ALLOW", tuple(document.fixture_id for document in documents))


def load_fixtures(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))

