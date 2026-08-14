from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from .models import Detection, GuardrailAssessment, ProviderUnavailable


class DiscoveryProvider(Protocol):
    name: str
    version: str
    is_real_vendor: bool

    def discover(self, text: str) -> list[Detection]: ...


class GuardrailProvider(Protocol):
    name: str
    version: str
    is_real_vendor: bool

    def assess(self, text: str) -> GuardrailAssessment: ...


def _post(url: str, body: bytes, content_type: str, timeout: float) -> object:
    request = urllib.request.Request(url, data=body, headers={"Content-Type": content_type}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ProviderUnavailable(f"provider call failed closed: {type(exc).__name__}") from exc


@dataclass(frozen=True)
class ProtegrityDiscoveryClient:
    endpoint: str = "http://localhost:8580/pty/data-discovery/v2/classify/text"
    timeout: float = 10.0
    name: str = "Protegrity Data Discovery"
    version: str = "2.0.0"
    is_real_vendor: bool = True

    def discover(self, text: str) -> list[Detection]:
        payload = _post(self.endpoint, text.encode("utf-8"), "text/plain", self.timeout)
        detections = self._normalize(payload, text)
        if not isinstance(payload, (dict, list)):
            raise ProviderUnavailable("malformed Data Discovery result")
        return detections

    @classmethod
    def _normalize(cls, payload: object, text: str) -> list[Detection]:
        candidates: list[dict[str, object]] = []

        if isinstance(payload, dict) and isinstance(payload.get("classifications"), dict):
            for entity_type, entries in payload["classifications"].items():
                if not isinstance(entries, list):
                    continue
                for entry in entries:
                    if not isinstance(entry, dict) or not isinstance(entry.get("location"), dict):
                        continue
                    location = entry["location"]
                    candidates.append(
                        {
                            "entity_type": str(entity_type),
                            "start": location.get("start_index"),
                            "end": location.get("end_index"),
                            "score": entry.get("score", 1.0),
                        }
                    )

        def walk(node: object) -> None:
            if isinstance(node, dict):
                keys = {str(key).lower() for key in node}
                if keys & {"entity_type", "entity", "label", "classification"} and keys & {"start", "start_index", "offset"}:
                    candidates.append(node)
                for child in node.values():
                    walk(child)
            elif isinstance(node, list):
                for child in node:
                    walk(child)

        walk(payload)
        result: list[Detection] = []
        for item in candidates:
            entity_type = str(item.get("entity_type") or item.get("entity") or item.get("label") or item.get("classification"))
            start = int(item.get("start") or item.get("start_index") or item.get("offset") or 0)
            end_value = item.get("end") or item.get("end_index")
            if end_value is None:
                detected_text = str(item.get("text") or item.get("value") or "")
                end_value = start + len(detected_text)
            end = int(end_value)
            score = float(item.get("score") or item.get("confidence") or 1.0)
            if 0 <= start < end <= len(text):
                result.append(Detection(entity_type=entity_type, start=start, end=end, score=score))
        return sorted(result, key=lambda item: (item.start, item.end))


@dataclass(frozen=True)
class ProtegritySemanticGuardrailClient:
    endpoint: str = "http://localhost:8581/pty/semantic-guardrail/v1.1/conversations/messages/scan"
    threshold: float = 0.70
    timeout: float = 15.0
    name: str = "Protegrity Semantic Guardrails"
    version: str = "1.1.1"
    is_real_vendor: bool = True

    def assess(self, text: str) -> GuardrailAssessment:
        body = json.dumps({"messages": [{"from": "user", "to": "ai", "content": text, "processors": ["customer-support"]}]}).encode("utf-8")
        payload = _post(self.endpoint, body, "application/json", self.timeout)
        return self._normalize(payload, self.threshold)

    @classmethod
    def _normalize(cls, payload: object, threshold: float = 0.70) -> GuardrailAssessment:
        scores: list[float] = []
        labels: list[str] = []

        def walk(node: object) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    lowered = str(key).lower()
                    if lowered == "score" and isinstance(value, (int, float)):
                        scores.append(float(value))
                    elif lowered in {"label", "class", "classification", "explanation", "risk"} and isinstance(value, str):
                        labels.append(value)
                    walk(value)
            elif isinstance(node, list):
                for child in node:
                    walk(child)

        walk(payload)
        if not scores:
            raise ProviderUnavailable("malformed Semantic Guardrails result: no score")
        score = max(scores)
        batch = payload.get("batch") if isinstance(payload, dict) else None
        outcome = str(batch.get("outcome", "")).lower() if isinstance(batch, dict) else ""
        if outcome == "approved":
            decision = "ALLOW"
        elif outcome == "rejected":
            decision = "BLOCK"
        else:
            decision = "BLOCK" if score >= threshold else "ALLOW"
        return GuardrailAssessment(score=score, decision=decision, labels=tuple(sorted(set(labels))))


class DeterministicDiscoveryDouble:
    """Test-only contract double. It is never represented as Protegrity behavior."""

    name = "deterministic discovery test double"
    version = "test-only-1"
    is_real_vendor = False
    _patterns = {
        "PERSON": re.compile(r"(?<=Customer )[A-Z][a-z]+ [A-Z][a-z]+"),
        "EMAIL_ADDRESS": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "PHONE_NUMBER": re.compile(r"\b\d{3}-\d{3}-\d{4}\b"),
        "SOCIAL_SECURITY_ID": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "CREDIT_CARD": re.compile(r"\b\d{16}\b"),
    }

    def discover(self, text: str) -> list[Detection]:
        detections: list[Detection] = []
        for entity_type, pattern in self._patterns.items():
            detections.extend(Detection(entity_type, match.start(), match.end(), 0.99) for match in pattern.finditer(text))
        return sorted(detections, key=lambda item: (item.start, item.end))


class DeterministicGuardrailDouble:
    """Test-only policy double. It does not claim Semantic Guardrails equivalence."""

    name = "deterministic guardrail test double"
    version = "test-only-1"
    is_real_vendor = False
    _malicious = ("ignore previous", "reveal", "exfiltrate", "raw record", "system prompt", "all customer")

    def assess(self, text: str) -> GuardrailAssessment:
        normalized = text.lower()
        labels = tuple(term for term in self._malicious if term in normalized)
        score = min(1.0, 0.2 + 0.25 * len(labels))
        return GuardrailAssessment(score=score, decision="BLOCK" if score >= 0.7 else "ALLOW", labels=labels, provider=self.name)
