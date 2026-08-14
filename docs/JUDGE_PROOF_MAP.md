# Judge Proof Map

The repository's differentiator is inspectable per-execution qualification, not the invention of new controls.

> Protegrity supplies the controls. Protected Enterprise Agent proves they governed the execution.

Installed is not enforced. Enforced is not proven.

| Scoped claim | Causal control | Existing evidence | Reproduce |
|---|---|---|---|
| Sensitive fixture values are transformed before tested embedding/storage surfaces | Protegrity Data Discovery spans determine application-surrogate replacement; trustworthy detection is required | Ingestion events, `VENDOR_QUALIFICATION.json`, `SECURITY_RESULTS.json` | Run live qualification, then `render_execution_proof.py` |
| Tested exfiltration and injection requests do not reach retrieval or model dispatch | Protegrity Semantic Guardrails batch outcome determines `BLOCK` | S2/S3 input-guardrail events, `ADVERSARIAL_RESULTS.json` | Run live qualification; inspect S2/S3 events |
| The legitimate support task retains its expected business resolution | Protected retrieval plus provider-neutral model boundary | S1 inference event, `UTILITY_RESULTS.json` | Run live qualification; inspect S1 utility result |
| Required-provider failure does not silently fall back | Typed provider failure and no fallback route | `FAIL_CLOSED_RESULTS.json`, automated test, vendor condition `fallback_not_used` | Run tests and `demo_fault_injection.py` |
| Missing required proof cannot become PASS | Read-only renderer requires the complete receipt set and valid hashes | Renderer output; negative-proof test/demo | Remove one receipt only in a temporary copy and rerun renderer |
| Final package corresponds to one frozen commit | Independent adjudicator compares evidence commit, HEAD, clean tree, claims, and tests | `ADJUDICATION_RESULTS.json`, `FRESH_CLONE_RESULTS.json` | Run both adjudicators from a clean clone |

Judge-facing invitation:

> Don't trust the README. Run the adjudicator.

Commands:

```powershell
$env:PYTHONPATH = "$PWD\src"
python .\scripts\adjudicate.py --root . --require-vendor
python .\scripts\adjudicate_submission.py --root .
python .\scripts\render_execution_proof.py --root .
python .\scripts\demo_fault_injection.py --root .
```

The renderer creates no evidence and grants no qualification. If required evidence is absent, malformed, mismatched to `HEAD`, or fails a required gate, it renders `NOT PROVEN`.
