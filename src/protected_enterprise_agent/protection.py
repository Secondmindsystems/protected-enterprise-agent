from __future__ import annotations

from .models import Detection, ProviderUnavailable


def surrogate_transform(text: str, detections: list[Detection], fixture_id: str) -> str:
    """Replace detected spans with deterministic application-level surrogates.

    This is intentionally not described as Protegrity tokenization.
    """
    if not detections:
        raise ProviderUnavailable("classifier returned no detections; raw path blocked")
    output: list[str] = []
    cursor = 0
    for index, detection in enumerate(sorted(detections, key=lambda item: item.start)):
        if detection.start < cursor:
            continue
        output.append(text[cursor:detection.start])
        safe_type = "".join(character for character in detection.entity_type.upper() if character.isalnum() or character == "_")
        output.append(f"[{safe_type}:SURR-{fixture_id}-{index:02d}]")
        cursor = detection.end
    output.append(text[cursor:])
    return "".join(output)

