# Known Limitations

- This is a proof-of-concept and challenge implementation, not production-ready security or a compliance control.
- The application-level surrogate transform is not Protegrity tokenization. Genuine protect/unprotect is outside the no-credential Path B.
- Live qualification requires local Protegrity Data Discovery 2.0.0 and Semantic Guardrails 1.1.1 containers. Test doubles establish application invariants only; they do not establish vendor behavior.
- Semantic Guardrails decisions are bounded to the pinned `customer-support` processor and its observed batch-outcome semantics. Labels and scores are model outputs, not universal security guarantees; future runtime versions require requalification before their outcomes can support this evidence package.
- The local sparse vector store is deliberately minimal, in-memory, and single-process. It proves the protected embedding/storage boundary but is not a production vector database.
- The deterministic model backend proves provider-neutral dispatch and utility checks. It does not measure hosted-model quality.
- Leak-canary scans prove absence of the enumerated synthetic fixture values on tested application-controlled surfaces. They do not prove absence of every possible sensitive value or cover infrastructure outside the inspected surfaces.
- Vendor container logs require separate inspection during live Docker qualification. The application does not claim universal log cleanliness.
- Person and entity detection quality is bounded by the pinned Protegrity component and tested fixture set.
- No automatic rehydration/unprotection is implemented.
