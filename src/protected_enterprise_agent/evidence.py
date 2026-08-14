from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import EvidenceEvent
from .security import assert_boundary_clean


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EvidenceWriter:
    def __init__(self, output: Path, forbidden: tuple[str, ...], run_id: str | None = None) -> None:
        self.output = output
        self.forbidden = forbidden
        self.run_id = run_id or str(uuid4())
        self.events: list[EvidenceEvent] = []

    def emit(self, **values: object) -> EvidenceEvent:
        event = EvidenceEvent(event_id=str(uuid4()), timestamp=utc_now(), run_id=self.run_id, **values)
        payload = event.public_dict()
        payload.pop("evidence_hash", None)
        assert_boundary_clean("evidence receipt", payload, self.forbidden)
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        event = replace(event, evidence_hash=digest)
        self.events.append(event)
        return event

    def flush(self) -> None:
        self.output.parent.mkdir(parents=True, exist_ok=True)
        body = "".join(json.dumps(event.public_dict(), sort_keys=True) + "\n" for event in self.events)
        assert_boundary_clean("evidence file", body, self.forbidden)
        self.output.write_text(body, encoding="utf-8")


def verify_evidence(path: Path) -> list[str]:
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        payload = json.loads(line)
        expected = payload.pop("evidence_hash")
        actual = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        if expected != actual:
            errors.append(f"line {line_number}: evidence hash mismatch")
    return errors
