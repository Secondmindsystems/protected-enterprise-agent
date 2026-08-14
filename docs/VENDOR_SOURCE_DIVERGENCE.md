# Vendor source divergence record

## Observation

At pinned vendor commit `15c113c10ba71b272e0e7515b04e2f81b8b6afe7`, narrative documentation indicates that the Semantic Guardrails compose path includes its Data Discovery dependencies. Direct inspection of the pinned compose files does not support treating that statement as operational truth:

- `data-discovery/docker-compose.yml` defines the Data Discovery dependency services.
- `semantic-guardrail/docker-compose.yml` defines the Semantic Guardrails service.
- the Semantic Guardrails sample assumes Data Discovery PII detection is running.

## Governed resolution

The local start route launches both compose files. Qualification inspects both compose projects and requires running service evidence from each. The two files must not be collapsed into a presumed single stack unless a future pinned vendor source proves that topology directly.

This record is a source-reconciliation note. It is not a vendor defect claim and does not alter the application architecture.
