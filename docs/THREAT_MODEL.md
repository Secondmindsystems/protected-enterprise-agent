# Threat Model

## Protected assets

- Raw synthetic customer identifiers in the trusted fixture zone
- Protected representations in embedding, storage, retrieval, and inference
- Model and tool dispatch payloads
- Application responses, logs, and evidence
- Credentials and local vendor configuration

## Trust assumptions

- Fixture files are authoritative and fictional.
- The leak manifest is test-only and independent of detector output.
- Protegrity services are untrusted until their pinned runtime behavior is observed.
- Model behavior is not a security boundary.
- Application-controlled payloads can be scanned deterministically before consequence.

## Threats and controls

| Threat | Primary control | Test surface |
|---|---|---|
| Raw PII reaches embeddings or store | Discovery-driven transform plus pre-embedding assertion | Vector records and metadata |
| Retrieval exposes identifiers | Protected-only corpus | Retrieved context |
| Prompt requests exfiltration | Semantic risk signal plus explicit block policy | S2 |
| Retrieved prompt injection | Protected context and dispatch assertion; no instruction execution from records | S3 and threat corpus |
| User supplies PII | Input discovery and transform before retrieval/model | S4 |
| Model repeats raw values | Model never receives enumerated raw values; output assertion | Output scan |
| Logs/evidence leak | Structured, sanitized receipts and file scan | S5 |
| Provider fails or lies malformed | Typed fail-closed path | S7 |
| Fallback weakens contract | Test-double/vendor identity in evidence; vendor required for qualification | Adjudicator |
| Secret enters Git | Tracked-file secret scan and public-estate review | G10/G12 |
| Hidden machine state | Fresh-clone run from written instructions | G9 |

## Non-claims

The design does not claim formal noninterference, universal prompt-injection prevention, production hardening, regulatory compliance, or protection of unenumerated infrastructure surfaces.

