# Evidence Summary

## Qualified claim

At the frozen submission commit, a live local run used Protegrity Data Discovery 2.0.0 and Semantic Guardrails 1.1.1 from AI Developer Edition 1.2.0. The run preserved the expected support-policy fact for the legitimate scenario and blocked the two adversarial scenarios while independent exact-canary scans found no enumerated fixture values on the tested vector, response, evidence, dispatch, or output surfaces.

This is scoped prototype evidence. It is not a production-readiness, compliance, universal data-loss-prevention, or universal prompt-injection-prevention claim.

## Causal component map

| Protegrity component | Protected stage | Causal effect | Evidence |
|---|---|---|---|
| Data Discovery | Ingestion before embedding/storage | Returned spans determine application-level surrogate replacement; absent trustworthy detection fails closed | `VENDOR_QUALIFICATION.json`, ingestion events in `EVIDENCE_EVENTS.jsonl` |
| Semantic Guardrails | Input guardrail before retrieval/inference | Pinned batch outcome determines `ALLOW` or `BLOCK`; blocked requests do not retrieve or dispatch | `VENDOR_QUALIFICATION.json`, input-guardrail events in `EVIDENCE_EVENTS.jsonl` |

Additional deterministic assertions scan the exact text before embedding, model dispatch, output, and evidence emission. These assertions are application controls, not additional Protegrity components.

## Machine-readable result set

The authoritative generated artifacts are under `evidence/runs/latest/` and are intentionally excluded from source control:

- `ADJUDICATION_RESULTS.json`: independent tests, live qualification, scans, documentation, clean-tree, and frozen-commit decision.
- `VENDOR_QUALIFICATION.json`: pinned runtime, real-response, application-path, causal-effect, no-fallback, security, utility, and adversarial gates.
- `RUNTIME_QUALIFICATION.json`: resolved Compose, container, image digest, port, WSL, Docker, Compose, and vendor-SHA observations.
- `SECURITY_RESULTS.json` and `LEAK_SCAN_RESULTS.json`: exact-canary findings by tested surface.
- `UTILITY_RESULTS.json`: legitimate-task business-fact preservation.
- `ADVERSARIAL_RESULTS.json`: exfiltration and prompt-injection decisions.
- `EVIDENCE_EVENTS.jsonl`: sanitized hash-verified event receipts.
- `CHALLENGE_FIT_RESULTS.json`, `SUBMISSION_CONGRUENCE_RESULTS.json`, and `FRESH_CLONE_RESULTS.json`: terminal submission gates.

## Reproduction

Follow `README.md`, run live qualification, run `scripts/adjudicate.py --require-vendor`, then run `scripts/adjudicate_submission.py`. A deterministic-only result is a rehearsal and cannot support externalization qualification.

For the compact claim-to-proof view, see `docs/JUDGE_PROOF_MAP.md`. `scripts/render_execution_proof.py` renders only existing receipts and must return `NOT PROVEN` when a required receipt is unavailable or any required gate fails.
