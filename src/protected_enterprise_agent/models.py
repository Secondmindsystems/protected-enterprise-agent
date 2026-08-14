from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


class BoundaryViolation(RuntimeError):
    """A forbidden value was found at a protected boundary."""


class ProviderUnavailable(RuntimeError):
    """A required provider did not return a trustworthy result."""


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int
    score: float


@dataclass(frozen=True)
class GuardrailAssessment:
    score: float
    decision: str
    labels: tuple[str, ...] = ()
    provider: str = "Protegrity Semantic Guardrails"


@dataclass
class EvidenceEvent:
    event_id: str
    timestamp: str
    run_id: str
    scenario_id: str
    pipeline_stage: str
    fixture_id: str
    classification_result: str
    detected_entity_types: list[str]
    protection_action: str
    protection_provider: str
    provider_component: str
    component_version: str
    decision: str
    downstream_surface: str
    raw_sensitive_data_present: bool
    utility_result: str
    security_result: str
    evidence_hash: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def public_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentResponse:
    text: str
    security_result: str
    utility_result: str
    decision: str
    retrieved_fixture_ids: tuple[str, ...]

