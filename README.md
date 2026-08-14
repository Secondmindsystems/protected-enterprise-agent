# Protected Enterprise Agent

Protected Enterprise Agent is a public-safe proof-of-concept for Protegrity's 2026 AI Pipeline Security Challenge. It demonstrates a financial-services support workflow in which sensitive synthetic data is discovered before protected retrieval, deterministic boundary checks prevent raw fixture values from entering model-facing surfaces, and the application still produces a useful business answer.

This repository is a prototype and tested architecture. It is not a production security product, compliance control, or guarantee against data leakage or prompt injection.

## Per-execution causal qualification

Protegrity supplies the controls. Protected Enterprise Agent proves they governed the execution.

The distinction is deliberately narrow: control availability does not prove causal control participation, and missing required evidence cannot become `PASS`. The qualified path records real responses from both pinned Protegrity components, requires their causal effect, rejects fallback, binds the result to a frozen commit, and independently checks security, utility, adversarial behavior, fail-closed behavior, and evidence integrity.

Installed is not enforced. Enforced is not proven.

Render the existing proof without creating new evidence:

```powershell
$env:PYTHONPATH = "$PWD\src"
python .\scripts\render_execution_proof.py --root .
python .\scripts\demo_fault_injection.py --root .
```

The renderer is read-only. Missing, malformed, commit-mismatched, or failed required evidence renders `NOT PROVEN`. The fault-injection command is a deterministic application test, not evidence of vendor behavior.

## What the demo proves

The canonical run makes four protection surfaces inspectable:

1. Ingestion: Protegrity Data Discovery classifies sensitive values before downstream storage.
2. Embedding and retrieval storage: only protected text and non-sensitive metadata are indexed.
3. Inference: Protegrity Semantic Guardrails causally informs the application allow/block policy, and a deterministic assertion scans the exact dispatch payload.
4. Output and evidence: the response and application-controlled evidence are scanned against an independent leak manifest.

The no-credential Path B transform uses deterministic application-level surrogate identifiers. It is not Protegrity tokenization.

## Requirements

- Python 3.11 or newer
- Git
- Docker with Compose 2.30 or newer for live vendor qualification
- The official [Protegrity AI Developer Edition](https://github.com/Protegrity-AI-Developer-Edition/protegrity-ai-developer-edition) repository pinned to commit `15c113c10ba71b272e0e7515b04e2f81b8b6afe7`

The pinned vendor release is AI Developer Edition 1.2.0, with Data Discovery 2.0.0 and Semantic Guardrails 1.1.1.

## Quick start

Create a virtual environment and install the local package:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e .
```

Run deterministic tests. These use clearly labeled contract doubles and do not count as observed Protegrity behavior:

```powershell
$env:PEA_PYTHON = "$PWD\.venv\Scripts\python.exe"
powershell -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run_qualification.ps1
```

Optionally replace only the model implementation with a local Ollama model. The deterministic backend remains the default; Ollama is untrusted downstream compute and stays between the same pre-dispatch Boundary C and post-output Boundary D checks:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m protected_enterprise_agent.cli --root . --model-backend ollama --ollama-model gemma4:12b
```

This route sends only protected context after the guardrail has allowed the execution. A guardrail block or outage produces zero model calls, and model failure does not fall back silently.

For live vendor qualification, clone the pinned official repository outside this repository, start both components, and rerun with the vendor gate:

```powershell
$env:PROTEGRITY_DEV_EDITION_ROOT = 'C:\path\to\protegrity-ai-developer-edition'
powershell -ExecutionPolicy Bypass -File .\scripts\start_protegrity.ps1
$env:PYTHONPATH = "$PWD\src"
python .\scripts\qualify_runtime.py --root .
powershell -ExecutionPolicy Bypass -File .\scripts\run_qualification.ps1 -RequireVendor
```

The application calls these documented local endpoints:

- Data Discovery: `POST http://localhost:8580/pty/data-discovery/v2/classify/text`
- Semantic Guardrails: `POST http://localhost:8581/pty/semantic-guardrail/v1.1/conversations/messages/scan`

## Inspect the proof

Each canonical run writes sanitized artifacts under `evidence/runs/latest/`:

- `PROVENANCE_MANIFEST.json`
- `CANONICAL_RUN_MANIFEST.json`
- `SECURITY_RESULTS.json`
- `UTILITY_RESULTS.json`
- `ADVERSARIAL_RESULTS.json`
- `FAIL_CLOSED_RESULTS.json`
- `LEAK_SCAN_RESULTS.json`
- `EVIDENCE_EVENTS.jsonl`
- `RUNTIME_QUALIFICATION.json`
- `VENDOR_QUALIFICATION.json`

Run independent adjudication against a frozen commit:

```powershell
$env:PYTHONPATH = "$PWD\src"
.venv\Scripts\python .\scripts\adjudicate.py --root . --require-vendor
python .\scripts\adjudicate_submission.py --root .
```

Only an adjudication `PASS` supports the state `QUALIFIED_FOR_OPERATOR_EXTERNALIZATION`. A deterministic-only run remains a rehearsal. Endpoint availability alone is insufficient: vendor qualification requires pinned runtime observation, real responses from both components, execution through the application vendor path, no fallback, a causal guardrail decision, and passing security, utility, and adversarial suites.

Don't trust the README. Run the adjudicator.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Known limitations](KNOWN_LIMITATIONS.md)
- [Demo script](DEMO_SCRIPT.md)
- [Attribution and provenance](docs/PROVENANCE.md)
- [Campaign continuation](CAMPAIGN_STATE.md)
- [Vendor source divergence](docs/VENDOR_SOURCE_DIVERGENCE.md)
- [Evidence summary](docs/EVIDENCE_SUMMARY.md)
- [Operator submission checklist](docs/SUBMISSION_CHECKLIST.md)
- [Judge proof map](docs/JUDGE_PROOF_MAP.md)

## Data policy

All customer records are fictional and use reserved `.test` email domains plus synthetic values. Raw synthetic values exist only in authoritative fixtures, the test-only leak manifest, and narrowly scoped tests. They must not appear in normal logs, evidence, model dispatch, retrieved context, or public narrative artifacts.

## License

Project code is MIT licensed. Protegrity components are not vendored here; consult the upstream repository and its license.
