# Agent2Allow Premise

## Mission
Build Agent2Allow into a practical, OSS-first agent gateway that is simple to run, secure by default, and reliable in production-like workflows.

## Positioning
Agent2Allow — Ship AI agents safely to production in 10 minutes — with deny-by-default permissions, human approvals, and auditable tool calls.

## Non-negotiables
- Keep it simple: no unnecessary framework or architecture complexity.
- Security first: deny-by-default, least privilege, auditable behavior.
- DX first: 10-minute quickstart must stay reliable.
- Every PR must deliver measurable value (DX, security, reliability, docs, or performance).
- No secrets in repo. No telemetry unless explicit opt-in.
- No scope creep: finish small, high-impact changes.

## Iteration Loop
1. Sync and scan repo status (code, docs, CI, open PRs/issues).
2. Research friction signals (repo-first; web when needed).
3. Prioritize one Quick Win and one Moat Builder.
4. Append plan in `docs/PLANS.md` and selection in `docs/NORTH_STAR.md`.
5. Implement in small, testable batches.
6. Validate with local checks and CI.
7. Publish via PR, merge when green, then update reports.

## Current Baseline (2026-02-18)
- Iteration 1 merged: quickstart lift, deterministic smoke demo, audit UI improvements.
- Iteration 2 merged: GitHub connector retries/backoff + denied-call troubleshooting docs.
- Iteration 3 merged: idempotency keys for `/v1/tool-calls` + SDK approval/idempotency examples.
- Iteration 4 merged: policy validation CLI, CI policy checks, one-command local `dev_check.sh`.

## Next Focus Areas
- Improve approval UX with bulk actions and clearer state transitions.
- Add audit event schema versioning and migration notes.
- Add connector extension guide with minimal test contract template.
- Expand SDK snippets for real GitHub mode safety checks.
