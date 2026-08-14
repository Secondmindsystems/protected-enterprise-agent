# Operator Submission Checklist

Official challenge facts were rechecked on August 13, 2026. The public page requires a GitHub repository, a short architecture overview, and a 10-15 minute recorded demo showing protection across at least two AI workflow stages. The listed submission recipient is `hackathons@protegrity.com`; the listed due date is August 24, 2026. The page also contains an inconsistent August 10 finalist-notification date, so the operator should confirm administrative timing before sending.

## Prepared package

- [x] Working repository and reproducible commands in `README.md`
- [x] Architecture overview and trust-boundary diagram in `ARCHITECTURE.md`
- [x] 10-15 minute recording script in `DEMO_SCRIPT.md`
- [x] Evidence-to-claim map in `docs/EVIDENCE_SUMMARY.md`
- [x] Judge-facing Claim -> Control -> Evidence -> Reproduce map in `docs/JUDGE_PROOF_MAP.md`
- [x] Read-only execution-proof renderer and deterministic negative-proof demo
- [x] Threat model, provenance, source-divergence record, and limitations
- [x] Independent technical adjudicator and submission-specific adjudicator
- [x] Fresh-clone live reproduction receipt

## Operator-owned external actions

- [ ] Confirm participant eligibility, registration approval, challenge terms, and the live deadline.
- [ ] Create or select the public GitHub repository and verify its visibility and license presentation.
- [ ] Record the demo without displaying the leak manifest or raw evidence canaries.
- [ ] Upload the demo video and verify the viewing permissions.
- [ ] Replace the placeholders below with the final public URLs.
- [ ] Email the completed entry to `hackathons@protegrity.com`.

## Submission email template

Subject: `2026 AI Pipeline Security Challenge - Protected Enterprise Agent`

Body:

```text
Hello Protegrity Hackathon Team,

Please accept my completed entry for the 2026 AI Pipeline Security Challenge.

Project: Protected Enterprise Agent
GitHub repository: <PUBLIC_GITHUB_URL>
Architecture overview: <PUBLIC_GITHUB_URL>/blob/<COMMIT>/ARCHITECTURE.md
10-15 minute demo: <DEMO_VIDEO_URL>

The project uses Protegrity Data Discovery at ingestion and Protegrity Semantic Guardrails before retrieval/inference. The repository includes the threat model, limitations, reproducibility commands, and machine-readable evidence package.

Participant name: <NAME>
Registration email: <EMAIL>

Thank you,
<NAME>
```

External publication, account actions, video upload, and email transmission remain operator actions; this repository does not perform them.
