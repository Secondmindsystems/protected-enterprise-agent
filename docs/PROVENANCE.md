# Attribution and Provenance

## Protegrity upstream

- Repository: `https://github.com/Protegrity-AI-Developer-Edition/protegrity-ai-developer-edition`
- Pinned commit: `15c113c10ba71b272e0e7515b04e2f81b8b6afe7`
- AI Developer Edition: 1.2.0
- Data Discovery: 2.0.0
- Semantic Guardrails: 1.1.1
- Python SDK: 1.2.1 upstream; not used by the credential-independent Path B
- Upstream license: MIT at the pinned repository

No upstream code, images, or model assets are vendored into this repository. Runtime containers are pulled by the official upstream Compose files.

## Challenge facts

The live Protegrity challenge page was checked on August 13, 2026. It described a U.S.-only virtual challenge, a June 30–August 24 build window, a GitHub repository, short architecture overview, 10–15 minute demo, at least two protected AI workflow stages, and two or more Protegrity components for the Primary Secure AI Pipelines focus.

The same page listed August 10 finalist notification and August 24 submission/winner dates. That administrative inconsistency is disclosed rather than silently reconciled.

## Local implementation

The project uses Python standard-library components for HTTP, sparse retrieval, evidence hashing, JSON, and tests. No confidential third-party corpus or real personal data is included.

