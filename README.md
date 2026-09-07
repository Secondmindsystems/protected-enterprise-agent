# Protected Enterprise Agent

## Answer a support question using protected context

Protected Enterprise Agent is a financial-services support prototype built with synthetic customer records.

Before information is indexed, the application identifies sensitive values and replaces them with application-level surrogate identifiers. It then retrieves protected context, checks whether a model request should proceed, and inspects what reaches the model and what comes back.

The project was built for Protegrity's 2026 AI Pipeline Security Challenge and brings those steps together in one application you can inspect and test.

**[Run the local tests](#quick-start)** · [Inspect the architecture](ARCHITECTURE.md) · [Review the evidence summary](docs/EVIDENCE_SUMMARY.md)

## Follow a request through the application

A support request moves through four stages:

1. **Discover sensitive data.** Data Discovery identifies sensitive values before downstream storage.
2. **Store protected context.** The application indexes protected text and non-sensitive metadata.
3. **Decide whether the request proceeds.** An input guardrail determines whether retrieval and model dispatch are allowed.
4. **Check what crossed the boundary.** Deterministic checks inspect the model dispatch, returned output, and application evidence against the test leak manifest.

The application-level surrogate identifiers used by the no-credential path are not Protegrity tokenization.

Local deterministic tests use contract doubles. Testing the actual Protegrity integration requires real responses from both pinned Protegrity components.

## Quick start

Requirements:

* Python 3.11 or newer
* Git
* Docker with Compose 2.30 or newer for live Protegrity qualification

Create a virtual environment and install the local package:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
```

Run the deterministic test path:

```powershell
$env:PEA_PYTHON = "$PWD\.venv\Scripts\python.exe"
powershell -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\run_qualification.ps1
```

These tests use clearly labeled contract doubles. They test the application without representing the results as observed Protegrity behavior.

## Try it with a local model

You can replace the deterministic model implementation with a local Ollama model:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m protected_enterprise_agent.cli --root . --model-backend ollama --ollama-model gemma4:12b
```

The model remains downstream of the same request and output checks.

If the guardrail blocks the request or becomes unavailable, the application does not call the model. A model failure does not silently fall back to another path.

## Run the Protegrity integration

Live vendor qualification uses the official [Protegrity AI Developer Edition](https://github.com/Protegrity-AI-Developer-Edition/protegrity-ai-developer-edition) pinned to commit:

```text
15c113c10ba71b272e0e7515b04e2f81b8b6afe7
```

The pinned release is AI Developer Edition 1.2.0 with Data Discovery 2.0.0 and Semantic Guardrails 1.1.1.

Clone that repository outside this one, start both components, and run:

```powershell
$env:PROTEGRITY_DEV_EDITION_ROOT = 'C:\path\to\protegrity-ai-developer-edition'
powershell -ExecutionPolicy Bypass -File .\scripts\start_protegrity.ps1
$env:PYTHONPATH = "$PWD\src"
python .\scripts\qualify_runtime.py --root .
powershell -ExecutionPolicy Bypass -File .\scripts\run_qualification.ps1 -RequireVendor
```

The application uses these documented local endpoints:

* Data Discovery: `POST http://localhost:8580/pty/data-discovery/v2/classify/text`
* Semantic Guardrails: `POST http://localhost:8581/pty/semantic-guardrail/v1.1/conversations/messages/scan`

Live qualification requires actual responses from both components through the application path. Simply having the endpoints available is not enough.

## Inspect the evidence

Each canonical run writes sanitized evidence under `evidence/runs/latest/`, including results for security, utility, adversarial behavior, fail-closed behavior, leak scanning, runtime qualification, and vendor qualification.

To evaluate a frozen run:

```powershell
$env:PYTHONPATH = "$PWD\src"
.venv\Scripts\python .\scripts\adjudicate.py --root . --require-vendor
python .\scripts\adjudicate_submission.py --root .
```

A deterministic-only run remains a rehearsal. The vendor-qualified path requires real responses from the pinned components, execution through the application vendor path, no fallback, a guardrail decision that affects what the application does, and passing security, utility, and adversarial checks.

For the exact checks behind a result, inspect the generated adjudication record and the [judge proof map](docs/JUDGE_PROOF_MAP.md).

## Inspect an existing run

The proof renderer reads generated evidence without creating new evidence:

```powershell
$env:PYTHONPATH = "$PWD\src"
python .\scripts\render_execution_proof.py --root .
python .\scripts\demo_fault_injection.py --root .
```

If required evidence is missing, malformed, tied to a different commit, or records a failed requirement, the renderer returns `NOT PROVEN`.

The fault-injection command tests application behavior deterministically; it is not evidence of vendor behavior.

The source checkout does not include the original vendor-run artifacts. [The evidence summary](docs/EVIDENCE_SUMMARY.md) describes that recorded build separately from what can be reproduced from the checkout.

## Technical documentation

* [Architecture](ARCHITECTURE.md)
* [Threat model](docs/THREAT_MODEL.md)
* [Evidence summary](docs/EVIDENCE_SUMMARY.md)
* [Judge proof map](docs/JUDGE_PROOF_MAP.md)
* [Known limitations](KNOWN_LIMITATIONS.md)
* [Attribution and provenance](docs/PROVENANCE.md)

## Data policy

All customer records are fictional and use reserved `.test` email domains and synthetic values.

Raw synthetic values are confined to authoritative fixtures, the test-only leak manifest, and narrowly scoped tests. Normal logs, evidence, model dispatch, retrieved context, and public narrative artifacts are expected to contain only the protected representations defined by the application.

## About Second Mind Systems

Built by Tavio Lawrence as part of Second Mind Systems' work on AI harnesses, protected AI workflows, evaluation, model boundaries, and inspectable execution.

For more engineering work, visit the [Governed AI Systems Portfolio](https://github.com/Secondmindsystems/governed-ai-systems-portfolio).

For engineering roles, consulting, implementation, or technical collaboration: [secondmindsystems@gmail.com](mailto:secondmindsystems@gmail.com).

## License

Project code is MIT licensed. Protegrity components are not vendored in this repository; their upstream license applies separately.
