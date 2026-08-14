# Campaign state

## Current disposition

`HOLD — OPERATOR_CONTAINER_RUNTIME_ONLY`

Accepted frozen baseline: `a4d2107ed7c6228e5ad8f24a072a70c71d2315ae`.

The deterministic product path, proof surfaces, and independent adjudicator have passed their current gates. Real Protegrity execution has not been observed. The only active seam is operator installation or authorization of a qualifying Linux-container runtime. This file does not assert that the baseline is vendor-qualified.

## Continuation boundary

Do not reopen the deterministic gates conceptually unless new observed vendor evidence falsifies one of their premises. Do not change product architecture while the runtime seam remains unresolved.

After a qualifying runtime is available, proceed in this order:

1. Runtime qualification.
2. Untouched vendor baseline execution.
3. Application execution through the real vendor path.
4. At most one bounded vendor-native hardening attempt if the baseline exposes a localized gap.
5. Full deterministic and vendor requalification.
6. Independent adjudication of a clean successor commit.
7. Demo-candidate review.
8. Operator-controlled externalization.

## Exact operator re-entry

```powershell
docker version
docker compose version
docker info --format '{{.OSType}}'
docker run --rm hello-world

$env:PROTEGRITY_DEV_EDITION_ROOT = 'C:\path\to\protegrity-ai-developer-edition'
powershell -ExecutionPolicy Bypass -File .\scripts\start_protegrity.ps1

$env:PYTHONPATH = "$PWD\src"
python .\scripts\qualify_runtime.py --root .
powershell -ExecutionPolicy Bypass -File .\scripts\run_qualification.ps1 -RequireVendor
python .\scripts\adjudicate.py --root . --require-vendor
```

Required versions and state:

- Docker server available and configured for Linux containers.
- Docker Compose 2.30 or newer.
- Official vendor checkout at `15c113c10ba71b272e0e7515b04e2f81b8b6afe7`.
- All Data Discovery and Semantic Guardrails services running.
- Trivial container execution succeeds.

## Qualification predicate

`vendor_available` is diagnostic only. It is not a promotion gate.

`vendor_qualified` is true only when all of the following are independently observed:

- pinned vendor runtime;
- real Data Discovery response;
- real Semantic Guardrails response;
- application execution through the real vendor path;
- no test-double or fallback use;
- causal Semantic Guardrails effect on an application decision;
- leak suite pass;
- utility suite pass;
- adversarial suite pass.

Any missing conjunct keeps the campaign on hold.

## Stop gates

Stop without architecture expansion if any of these occurs:

- the vendor checkout SHA differs;
- Docker is not using Linux containers;
- Compose is older than 2.30;
- either vendor API is only reachable but cannot produce a valid response;
- the application silently uses a fallback;
- Semantic Guardrails does not causally affect at least one application decision;
- leak, utility, adversarial, evidence, public-estate, or clean-tree checks fail;
- a repair would require more than one bounded vendor-native attempt;
- external publication, submission, terms acceptance, credentials, or deployment would be required.

The first bounded hardening candidate, and only after untouched baseline evidence exists, is evaluation of the Data Discovery v2 Transform API as a local redaction endpoint. It is not pre-authorized as an architecture change and must be rejected if it expands scope or weakens the current proof boundary.
