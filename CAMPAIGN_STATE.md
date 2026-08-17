# Campaign state

## Current disposition

`QUALIFIED_FOR_OPERATOR_EXTERNALIZATION`

Qualified lineage: `a4d2107` (deterministic gates) → `b0ca2a2` (hardened vendor
gate) → `336951d` (adapters aligned with observed pinned vendor APIs) →
`947a93a` (vendor-qualified evidence) → `5acacc4` (per-execution causal proof
surfaces) → `2b1f05f` (optional local real-model adapter) → this commit
(truth-layer state record).

Real Protegrity execution has been observed and independently adjudicated.
Vendor qualification passed with all causal conjuncts against the pinned
official checkout `15c113c10ba71b272e0e7515b04e2f81b8b6afe7`: pinned runtime
observed, real Data Discovery and Semantic Guardrails responses, application
execution through the real vendor path, no fallback, causal guardrail effect,
and passing leak, utility, and adversarial suites. An optional local Ollama
model backend was additionally qualified behind the same dispatch boundaries;
the deterministic backend remains the qualification default.

Receipts for the current run live under `evidence/runs/latest/`, including
`ADJUDICATION_RESULTS.json`, `VENDOR_QUALIFICATION.json`, and
`FRESH_CLONE_RESULTS.json`, each bound to the frozen commit they qualify.

## Historical progression

Earlier revisions of this file recorded `HOLD — OPERATOR_CONTAINER_RUNTIME_ONLY`
at baseline `a4d2107`, when no Linux-container runtime existed on the host and
real vendor execution had therefore not yet been observed. That hold was
resolved on 2026-08-13 by operator installation of Docker Desktop (WSL2
backend), after which the pinned vendor stacks were executed and the
qualification chain above completed. The prior hold text is superseded by this
disposition; it remains accurate as history, not as current state.

## Remaining operator-owned seams

External actions are deliberately outside this repository's authority:

1. Public GitHub repository creation and push of the frozen submission commit.
2. Demo recording and upload.
3. Submission email to the challenge recipient.
4. Preservation of submission receipts.

No further product or architecture work is planned before submission. The
qualification predicate and stop-gate discipline below remain in force for any
future requalification.

## Qualification predicate

`vendor_available` is diagnostic only. It is not a promotion gate.

`vendor_qualified` is true only when all of the following are independently
observed:

- pinned vendor runtime;
- real Data Discovery response;
- real Semantic Guardrails response;
- application execution through the real vendor path;
- no test-double or fallback use;
- causal Semantic Guardrails effect on an application decision;
- leak suite pass;
- utility suite pass;
- adversarial suite pass.

Any missing conjunct returns the campaign to hold.

## Re-verification route

```powershell
docker version
docker compose version
docker info --format '{{.OSType}}'

$env:PROTEGRITY_DEV_EDITION_ROOT = 'C:\path\to\protegrity-ai-developer-edition'
powershell -ExecutionPolicy Bypass -File .\scripts\start_protegrity.ps1

$env:PYTHONPATH = "$PWD\src"
python .\scripts\qualify_runtime.py --root .
powershell -ExecutionPolicy Bypass -File .\scripts\run_qualification.ps1 -RequireVendor
python .\scripts\adjudicate.py --root . --require-vendor
python .\scripts\adjudicate_submission.py --root .
```

Required versions and state:

- Docker server available and configured for Linux containers.
- Docker Compose 2.30 or newer.
- Official vendor checkout at `15c113c10ba71b272e0e7515b04e2f81b8b6afe7`.
- All Data Discovery and Semantic Guardrails services running.

## Stop gates

Stop without architecture expansion if any of these occurs:

- the vendor checkout SHA differs;
- Docker is not using Linux containers;
- Compose is older than 2.30;
- either vendor API is only reachable but cannot produce a valid response;
- the application silently uses a fallback;
- Semantic Guardrails does not causally affect at least one application decision;
- leak, utility, adversarial, evidence, public-estate, or clean-tree checks fail;
- external publication, submission, terms acceptance, credentials, or
  deployment would be required without operator authorization.
